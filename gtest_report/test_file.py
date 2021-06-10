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
from datetime import datetime
from pathlib import Path

from comment_parser import comment_parser
from jinja2 import Environment, FileSystemLoader
from .test_func import TestFunc
from .test_case import TestCase, TestCaseInput, TestCaseOutput

NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class TestFile:

  pre_test_suite = None
  pre_test_case = None
  # test results from run output message
  test_results = None
  test_covs = None
  report_dir = None
  src_file = None

  def __init__(self, filename):
    self.filename = filename
    self.testfuncs = []
    self.title = filename[15:]
    self.created_date = NOW

    # self.dir = 'test/tools/reports/'+'-'.join(self.title.split('/')[0:-1]) # decision/decision_test
    self.rela_dir = '-'.join(
        self.title.split('/')[0:-1])  # decision/decision_test
    self.shortname = os.path.basename(self.filename)  # decision_test.cpp
    self.onlyname = os.path.splitext(os.path.basename(
        self.filename))[0]  # decision_test
    self.htmlname = os.path.splitext(
        self.filename)[0] + ".html"  #decision_test.html

  @property
  def link(self):
    return f"{self.rela_dir}/{self.shortname}.html"

  def get_testcases(self):
    testcases = []
    for testfunc in self.testfuncs:
      testcases += testfunc.testcases
    return testcases

  @property
  def tc_count(self):
    testcases = self.get_testcases()
    count = len(testcases)
    return count

  @property
  def tc_pass_count(self):
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
          test_result_list = [
              r for r in self.test_results if r.test_case_id == test_case_id
          ]
          if len(test_result_list) > 0:
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
    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "templates")
    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template('testfile.html')
    output_from_parsed_template = template.render(model=self)
    # print(output_from_parsed_template)
    # print("rela_dir:", self.rela_dir)
    # print("path:", self.report_dir+self.rela_dir)
    Path(self.report_dir + self.rela_dir).mkdir(parents=True, exist_ok=True)
    # to save the results
    with open(self.report_dir + self.link, "w") as fh:
      fh.write(output_from_parsed_template)

    for ts in self.testfuncs:
      ts.generate_html()
