#!/usr/bin/env python3
# --------------------------------------------------------------------------------- #
# Tool for generating unit test case from test source code.
#
# Author: Yao Guorong
# Create: 2021-05-20
# Latest Revision: 2021-05-20
#
# --------------------------------------------------------------------------------- #
import os
import re
from pathlib import Path
import itertools

from jinja2 import Environment, FileSystemLoader
from .logic_flow import analysis_lines


class CodeLine:

  def __init__(self, line, is_block_hit, block_no='', run_times=0):
    self.line = line
    self.bno = block_no
    self.is_block_hit = False
    self.run_times = run_times
    self.is_hit = (run_times > 0)


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
          if i >= id_line_idx and i <= id_line_idx + 5:
            pattern = '\((.+),(.+)\)'
            match = re.search(pattern, line)
            if match:
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
    (start_pos, end_pos) = self.test_func.get_code_pos()
    # end_pos = start_pos

    hit_line_nos = []
    # 13-15/16-18-20~21-22-23-27-28-34-37
    if self.test_route:
      print("== test route", self.test_route)
      # state_area_list = self.test_route.split('-')
      # for state_area in state_area_list:
      #   if '/' in state_area:
      #     line_no_str_list = state_area.split('/')
      #     for line_no_str in line_no_str_list:
      #       hit_line_nos.append(int(line_no_str.strip()))
      #   elif '~' in state_area:
      #     line_no_str_list = state_area.split('~')
      #     if len(line_no_str_list)==2:
      #       start_sno = int(line_no_str_list[0])
      #       end_sno = int(line_no_str_list[1]) + 1
      #       range_line_nos = range(start_sno, end_sno)
      #       hit_line_nos += range_line_nos
      #   else:
      #     hit_line_nos.append(int(state_area.strip()))

    # if hit_line_nos:
    #   end_pos = start_pos + hit_line_nos[-1]
    print("start_pos:", start_pos)
    print("end_pos:", end_pos)
    if src_file:
      filename = src_file
      print("filename:", filename)
      blocks = []
      with open(filename) as f:
        blockcode_str_list = itertools.islice(f, start_pos, end_pos)
        blocks = analysis_lines(blockcode_str_list)

      if self.test_route:
        route_list = self.test_route.split('-')

        for block in blocks:
          if block.no in route_list:
            for i in range(block.start_no, block.end_no):
              hit_line_nos.append(i)
          else:
            hit_line_nos = list(
                set(hit_line_nos) - set(range(block.start_no, block.end_no)))
      test_covs = self.test_func.test_file.test_covs

      with open(filename) as f:
        codeline_str_list = itertools.islice(f, start_pos, end_pos)

        for idx, line in enumerate(codeline_str_list):
          line_no = idx + 1
          is_block_hit = line_no in hit_line_nos

          run_times = 0
          test_covs = self.test_func.test_file.test_covs
          if test_covs:
            full_line_no = start_pos + line_no
            cov_list = [
                x for x in test_covs
                if x.sf == filename and x.line_no == full_line_no
            ]
            if cov_list:
              run_times = cov_list[0].run_times

          bno = ''
          if blocks:
            blist = [x for x in blocks if x.start_no == line_no]
            if blist:
              bno = blist[0].no

          codeline = CodeLine(line.rstrip(), is_block_hit, bno, run_times)
          codelines.append(codeline)
    return codelines

  def generate_html(self):
    print(f"======test case: {self.id} generate_html======")
    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "templates")
    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template('testcase.html')

    lines = self.get_source_code()

    output_from_parsed_template = template.render(model=self, lines=lines)
    # print(output_from_parsed_template)

    func_report_path = f"{self.test_func.test_file.report_dir}{self.test_func.test_file.rela_dir}/{self.test_func.test_file.onlyname}/"
    Path(func_report_path).mkdir(parents=True, exist_ok=True)
    # to save the results
    with open(func_report_path + self.link, "w") as fh:
      fh.write(output_from_parsed_template)
