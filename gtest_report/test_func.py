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
from jinja2 import Environment, FileSystemLoader

NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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
  def link(self):
    return f"{self.test_file.onlyname}/{self.name}.html"

  @property
  def tc_count(self):
    count = len(self.testcases)
    return count

  @property
  def tc_pass_count(self):
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

  def get_code_pos(self):
    # print("get_code_pos ...")
    start_pos = 0
    end_pos = 0
    if self.test_file.src_file:
      lookup = f'::{self.name}'
      filename = self.test_file.src_file
      nested_level = 0
      with open(filename) as f:
        for num, line in enumerate(f, 1):
          line = line.strip()
          # print(line)
          if lookup in line:
            start_pos = num - 1

          if start_pos > 0:
            if line.endswith("{"):
              nested_level = nested_level + 1

            if line.startswith("}"):
              nested_level = nested_level - 1
              if nested_level == 0:
                end_pos = num
                break
    # print(start_pos, end_pos)
    return (start_pos, end_pos)

  def generate_html(self):
    print(f"======test func: {self.name} generate_html======")
    templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "templates")
    env = Environment(loader=FileSystemLoader(templates_path))
    template = env.get_template('testfunc.html')
    output_from_parsed_template = template.render(model=self)
    # print(output_from_parsed_template)

    func_report_path = f"{self.test_file.report_dir}{self.test_file.rela_dir}/{self.test_file.onlyname}/"
    Path(func_report_path).mkdir(parents=True, exist_ok=True)
    # to save the results
    with open(func_report_path + self.html_filename, "w") as fh:
      fh.write(output_from_parsed_template)

    for tc in self.testcases:
      tc.generate_html()

  def generate_cfg(self):

    blist = [x for x in self.blocks if x.start_no == line_no]

    pass
