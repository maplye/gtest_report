#!/usr/bin/env python3
# --------------------------------------------------------------------------------- #
# Tool for generating unit test case from test source code.
#
# Author: Yao Guorong
# Create: 2021-05-20
# Latest Revision: 2021-05-20
#
# --------------------------------------------------------------------------------- #
import glob, os
import re
import sys
from datetime import datetime
from pathlib import Path
import getopt
import itertools


from comment_parser import comment_parser
from jinja2 import Environment, FileSystemLoader

BASE_DIR = "test/unit_test/"
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class CodeLine:
  def __init__(self, line, is_hit, block_no=''):
    self.line = line
    self.is_hit = is_hit
    self.bno = block_no

class TestCaseInput:
  def __init__(self, title):
    self.title = title
    self.test_case = None
  
  def __str__(self):
    return f'test case input: ({self.title})' 

class TestCaseOutput:
  def __init__(self, title):
    self.title = title
    self.test_case = None
  
  def __str__(self):
    return f'test case output: ({self.title})'

class TestResult:
  def __init__(self, test_case_id):
    self.test_case_id = test_case_id
    self.result = ""
    self.output_info = ""


class TestCase:
  def __init__(self, title, descript=None):
    self.id = None
    self.title = title
    self.descript = descript
    self.test_func = None
    self.inputs = []
    self.outputs = []
    self.testresult = None
    self.comment = None
    self.result = None
    self.test_route = None

  def __str__(self):
    return f'test case: ({self.func_name})'

  def get_id(self):
    id = ""
    if self.comment:
      line_num = self.comment.line_number()
      id_line_idx = line_num
      test_filename = self.test_func.test_file.filename
      with open(test_filename) as fp:
        for i, line in enumerate(fp):
          if i >= id_line_idx and i <= id_line_idx +5 :
            pattern = '\((.+),(.+)\)'
            match = re.search(pattern, line) 
            if match:
              groups = match.groups()
              id = f"{match.group(1)}.{match.group(2).strip()}"
              break
    self.id = id
    return id
  
  @property
  def link(self):
    return f"{self.id}.html"
  
  def get_source_code(self):
    codelines = []
    src_file = self.test_func.test_file.src_file
    start_pos = self.test_func.get_start_pos() - 1
    end_pos = start_pos

    hit_line_nos = []
    # 13-15/16-18-20~21-22-23-27-28-34-37
    if self.test_route:
      print("== test route", self.test_route)
      state_area_list = self.test_route.split('-')
      for state_area in state_area_list:
        if '/' in state_area:
          line_no_str_list = state_area.split('/')
          for line_no_str in line_no_str_list:
            hit_line_nos.append(int(line_no_str.strip()))
        elif '~' in state_area:
          line_no_str_list = state_area.split('~')
          if len(line_no_str_list)==2:
            start_sno = int(line_no_str_list[0])
            end_sno = int(line_no_str_list[1]) + 1
            range_line_nos = range(start_sno, end_sno)
            hit_line_nos += range_line_nos
        else:
          hit_line_nos.append(int(state_area.strip()))

    if hit_line_nos:
      end_pos = start_pos + hit_line_nos[-1]
    print("start_pos:", start_pos)
    print("end_pos:", end_pos)
    if src_file:
      filename = f"src/{src_file}"
      with open(filename) as f:
        codeline_str_list = itertools.islice(f, start_pos, end_pos)

        for idx, line in enumerate(codeline_str_list):
          line_no = idx+1
          is_hit = line_no in hit_line_nos

          bno = ''
          if self.test_func.blocks:
            print("$func blogs:", self.test_func.blocks)
            blist = [x for x in self.test_func.blocks if int(x['value'])==line_no]
            print("$Blocklist:", blist)
            if blist:
              bno = blist[0]['name']

          codeline = CodeLine(line.rstrip(), is_hit, bno)
          codelines.append(codeline)
    return codelines
  
  def generate_html(self):
    print(f"======test case: {self.id} generate_html======")
    env = Environment(loader=FileSystemLoader('test/tools/templates'))
    template = env.get_template('testcase.html')

    lines = self.get_source_code()

    output_from_parsed_template = template.render(model=self, lines=lines)
    # print(output_from_parsed_template)
    
    func_report_path = f"{self.test_func.test_file.report_dir}{self.test_func.test_file.rela_dir}/{self.test_func.test_file.onlyname}/"
    Path(func_report_path).mkdir(parents=True, exist_ok=True)
    # to save the results
    with open(func_report_path+self.link, "w") as fh:
        fh.write(output_from_parsed_template)
  


class TestFunc:
  
  def __init__(self, name, descript):
    self.name = name
    self.descript = descript
    self.testcases = []
    self.test_file = None
    self.html_filename = f"{self.name}.html"
    self.created_date = NOW
    self.block_text = None
    self.blocks = None

  def __str__(self):
    return f'test suite: ({self.name})'
  
  @property
  def link( self ):
    return f"{self.test_file.onlyname}/{self.name}.html"

  @property
  def tc_count( self ):
    count = len(self.testcases)
    return count

  @property
  def tc_pass_count( self ):
    testcase_list = self.testcases
    testcases_pass = [x for x in testcase_list if x.result == "OK"]
    count = len(testcases_pass)
    return count
  
  @property
  def tc_percent(self):
    percent = 0
    if self.tc_count > 0:
      percent = round(self.tc_pass_count * 100 / self.tc_count, 1)
    return percent

  def get_start_pos(self):
    pos = 0
    if self.test_file.src_file:
      lookup = f'::{self.name}'
      filename = f'src/{self.test_file.src_file}'
      with open(filename) as f:
          for num, line in enumerate(f, 1):
              if lookup in line:
                  pos = num
    return pos
  
  def get_blocks(self):
    blocks = []
    if self.block_text:
      blockstr_list = self.block_text.split()
      for blockstr in blockstr_list:
        block = blockstr.split(':')
        if len(block)==2:
          bname = block[0]
          bvalue = block[1]
          blocks.append({'name': bname, 'value': bvalue})
    return blocks

  def generate_html(self):
    print(f"======test func: {self.name} generate_html======")
    env = Environment(loader=FileSystemLoader('test/tools/templates'))
    template = env.get_template('testfunc.html')
    output_from_parsed_template = template.render(model=self)
    # print(output_from_parsed_template)
    
    func_report_path = f"{self.test_file.report_dir}{self.test_file.rela_dir}/{self.test_file.onlyname}/"
    Path(func_report_path).mkdir(parents=True, exist_ok=True)
    # to save the results
    with open(func_report_path+self.html_filename, "w") as fh:
        fh.write(output_from_parsed_template)
    
    for tc in self.testcases:
      tc.generate_html()
  

class TestFile:

  pre_test_suite = None
  pre_test_case = None
  # test results from run output message
  test_results = None
  report_dir = None
  src_file = None


  def __init__(self, filename):
    self.filename = filename
    self.testfuncs  = []
    self.title = filename[15:]
    self.created_date = NOW
    
    # self.dir = 'test/tools/reports/'+'-'.join(self.title.split('/')[0:-1]) # decision/decision_test
    self.rela_dir = '-'.join(self.title.split('/')[0:-1]) # decision/decision_test
    self.shortname = os.path.basename(self.filename)    # decision_test.cpp
    self.onlyname = os.path.splitext(os.path.basename(self.filename))[0]  # decision_test
    self.htmlname = os.path.splitext(self.filename)[0]+ ".html" #decision_test.html

  @property
  def link( self ):
    return f"{self.rela_dir}/{self.shortname}.html"

  def get_testcases(self):
    testcases = []
    for testfunc in self.testfuncs:
      testcases += testfunc.testcases
    return testcases

  @property
  def tc_count( self ):
    testcases = self.get_testcases()
    count = len(testcases)
    return count
  
  @property
  def tc_pass_count( self ):
    testcase_list = self.get_testcases()
    testcases_pass = [x for x in testcase_list if x.result == "OK"]
    count = len(testcases_pass)
    return count
  
  @property
  def tc_percent(self):
    percent = 0
    if self.tc_count > 0:
      percent = round(self.tc_pass_count * 100 / self.tc_count, 1)
    return percent

  def __extract__(self):
    return comment_parser.extract_comments(self.filename, mime='text/x-c++')

  def __transform__(self):
    print("transform: ", self.filename)
    comments = self.__extract__()
    for comment in comments:
      comment_text = comment.text().strip()
      is_multiline = comment.is_multiline()
      # test_func = None
      
      # test func
      if is_multiline:
        clines = comment_text.split('\n')

        name_str = clines[1].strip()
        desc = clines[2][2:].strip()

        if name_str.startswith("* @"):
          name = name_str[3:]
          test_func = TestFunc(name, desc)
          test_func.test_file = self
          
          self.pre_test_func = test_func

          self.testfuncs.append(self.pre_test_func)

        for cline in clines:
          # cpp file
          if cline.startswith(" * $cpp:"):
            self.src_file = cline[9:]
          
          # block
          if cline.startswith(" * $Block:"):
            print("$Block:")
            block_text = cline[11:]
            if self.pre_test_func:
              self.pre_test_func.block_text = block_text
              blocks = self.pre_test_func.get_blocks()
              print(blocks)
              self.pre_test_func.blocks = blocks

        
      if is_multiline is False:
        print(comment_text)
        # test case
        if comment_text.startswith("#"):
          tc_title = comment_text[1:]
          
          test_case = TestCase(tc_title)
          test_case.comment = comment
          test_case.test_func = test_func

          test_case_id = test_case.get_id()
          print('test_case_id', test_case_id)
          # test_result = next((r for r in self.test_results if r.test_case_id == test_case_id), None)
          test_result_list = [r for r in self.test_results if r.test_case_id == test_case_id]
          if len(test_result_list)>0:
            test_case.testresult = test_result_list[0]
            test_case.result = test_result_list[0].result

          self.pre_test_case = test_case
          self.pre_test_func.testcases.append(self.pre_test_case)

        # test route
        if comment_text.startswith("&"):
          test_route = comment_text[1:]
          if self.pre_test_case:
            self.pre_test_case.test_route = test_route
        
        # input
        if comment_text.startswith(">"):
          input_title = comment_text[1:]
          test_input = TestCaseInput(input_title)
          test_input.test_case = test_case
          if self.pre_test_case:
            self.pre_test_case.inputs.append(test_input)
        
        # output
        if comment_text.startswith("<"):
          if self.pre_test_case:
            output_title = comment_text[1:]
            test_output = TestCaseOutput(output_title)
            test_output.test_case = test_case
            self.pre_test_case.outputs.append(test_output)

  def generate_html(self):
    print(f"******test file: {self.filename} generate_html******")
    self.__transform__()
    
    env = Environment(loader=FileSystemLoader('test/tools/templates'))
    template = env.get_template('testfile.html')
    output_from_parsed_template = template.render(model=self)
    # print(output_from_parsed_template)
    # print("rela_dir:", self.rela_dir)
    # print("path:", self.report_dir+self.rela_dir)
    Path(self.report_dir+self.rela_dir).mkdir(parents=True, exist_ok=True)
    # to save the results
    with open(self.report_dir + self.link, "w") as fh:
        fh.write(output_from_parsed_template)

    for ts in self.testfuncs:
      ts.generate_html()


class TestReport:

  testfiles = []
  created_date=NOW
  report_dir = None

  def get_testcases(self):
    testcases = []
    for testfile in self.testfiles:
      for testfunc in testfile.testfuncs:
        testcases += testfunc.testcases
    return testcases

  @property
  def tc_count( self ):
    testcases = self.get_testcases()
    count = len(testcases)
    return count
  
  @property
  def tc_pass_count( self ):
    testcase_list = self.get_testcases()
    testcases_pass = [x for x in testcase_list if x.result == "OK"]
    count = len(testcases_pass)
    return count

  @property
  def tc_percent(self):
    percent = 0
    if self.tc_count > 0:
      percent = round(self.tc_pass_count * 100 / self.tc_count, 1)
    return percent


  def generate_html(self):
    print("******TEST REPORT generate_html******")
    env = Environment(loader=FileSystemLoader('test/tools/templates'))
    template = env.get_template('index.html')
    output_from_parsed_template = template.render(model=self)
    # print(output_from_parsed_template)

    # to save the results
    with open(f"{self.report_dir}/index.html", "w") as fh:
      fh.write(output_from_parsed_template)


class TestOutput:
  def __init__(self, filename):
    self.filename = filename
    self.test_results = []
  
  def transform_output(self):
    curr_test_result = None

    with open(self.filename) as output_file:
      for i, line in enumerate(output_file):
        #start
        if line.startswith("[ RUN      ]"):
          test_case_id = line[13:].strip()
          curr_test_result = TestResult(test_case_id)
        else:
          # append output
          if curr_test_result:
            if line.startswith("[       OK ]"):
              #end OK
              curr_test_result.result  = "OK"

              self.test_results.append(curr_test_result)
              curr_test_result = None
            
            elif line.startswith("[  FAILED  ]"):
              #end FAILED
              curr_test_result.result  = "FAILED"

              self.test_results.append(curr_test_result)
              curr_test_result = None
            else:
              # Info
              curr_test_result.output_info += line


if __name__ == "__main__":
  report_dir = "reports/result/"
  try:
    options, args = getopt.getopt(sys.argv[1:], "r:", ["report="])
    for name,value in options:
      if name in ("-r","--report"):
        report_dir = value
  except getopt.GetoptError:
    sys.exit()
  
  Path(report_dir).mkdir(parents=True, exist_ok=True)

  # output
  test_output = TestOutput("test/tools/unit_test.output")
  test_output.transform_output()

  # test files
  testfiles = []
  for filename in glob.glob("test/unit_test/**/*_test.cpp", recursive=True):
    # print(filename)
    tf = TestFile(filename)
    tf.test_results = test_output.test_results
    tf.report_dir = report_dir
    tf.generate_html()
    testfiles.append(tf)

  # test report
  test_report = TestReport()
  test_report.testfiles = testfiles
  test_report.report_dir = report_dir
  test_report.generate_html()


if __name__ == "__main__1":
  codelines = []
  filename = "/home/conan/projects/conchpilot/src/adm_control/common/hysteresis_filter.cpp"
  with open(filename) as f:
    codelines = f.readlines()
  
  print(len(codelines))
  print('=========================')
  print(codelines[0].rstrip(),"***********")
  print('=======================')
  