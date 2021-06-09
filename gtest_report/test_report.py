

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
from .logic_flow import analysis_lines


NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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
    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template('index.html')
    output_from_parsed_template = template.render(model=self)
    # print(output_from_parsed_template)

    # to save the results
    with open(f"{self.report_dir}/index.html", "w") as fh:
      fh.write(output_from_parsed_template)
