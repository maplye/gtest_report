#!/usr/bin/env python3
# --------------------------------------------------------------------------------- #
# Tool for generating unit test case from test source code.
#
# Author: Yao Guorong
# Create: 2021-05-20
# Latest Revision: 2021-05-20
#
# --------------------------------------------------------------------------------- #


class TestCov:

  def __init__(self, sf):
    self.sf = sf
    self.line_no = None
    self.run_times = None


class TestCoverage:

  def __init__(self, filename):
    self.filename = filename
    self.test_covs = []

  def transform_cov(self):
    print("transform_cov...")
    curr_sf = None

    with open(self.filename) as cov_file:
      for i, line in enumerate(cov_file):
        # SF
        if line.startswith("SF:/home/conan/projects/conchpilot/src/"):
          sf = line[35:].strip()
          curr_sf = sf

        if line.startswith("DA:"):
          if curr_sf:
            curr_test_cov = TestCov(sf)
            counts = line[3:].strip().split(",")
            curr_test_cov.line_no = int(counts[0])
            curr_test_cov.run_times = int(counts[1])
            # print(curr_test_cov.line_no, curr_test_cov.run_times)
            self.test_covs.append(curr_test_cov)

        if line.startswith("end_of_record"):
          curr_sf = None
