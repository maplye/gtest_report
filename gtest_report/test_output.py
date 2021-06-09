#!/usr/bin/env python3
# --------------------------------------------------------------------------------- #
# Tool for generating unit test case from test source code.
#
# Author: Yao Guorong
# Create: 2021-05-20
# Latest Revision: 2021-05-20
#
# --------------------------------------------------------------------------------- #


class TestResult:

  def __init__(self, test_case_id):
    self.test_case_id = test_case_id
    self.result = ""
    self.output_info = ""


class TestOutput:

  def __init__(self, filename):
    self.filename = filename
    self.test_results = []

  def transform_output(self):
    curr_test_result = None

    with open(self.filename) as output_file:
      for i, line in enumerate(output_file):
        # start
        if line.startswith("[ RUN      ]"):
          test_case_id = line[13:].strip()
          curr_test_result = TestResult(test_case_id)
        else:
          # append output
          if curr_test_result:
            if line.startswith("[       OK ]"):
              # end OK
              curr_test_result.result = "OK"

              self.test_results.append(curr_test_result)
              curr_test_result = None

            elif line.startswith("[  FAILED  ]"):
              # end FAILED
              curr_test_result.result = "FAILED"

              self.test_results.append(curr_test_result)
              curr_test_result = None
            else:
              # Info
              curr_test_result.output_info += line
