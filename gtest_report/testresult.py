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
import sys
import glob
from pathlib import Path
import getopt

from .test_file import TestFile
from .test_func import TestFunc
from .test_output import TestOutput
from .test_report import TestReport
from .test_coverage import TestCoverage

BASE_DIR = "test/unit_test/"


def generate_html(fname=None):
  report_dir = "reports/result/"
  try:
    options, args = getopt.getopt(sys.argv[1:], "r:", ["report="])
    for name, value in options:
      if name in ("-r", "--report"):
        report_dir = value
  except getopt.GetoptError:
    sys.exit()

  Path(report_dir).mkdir(parents=True, exist_ok=True)

  # output
  test_output = TestOutput("test/tools/unit_test.output")
  test_output.transform_output()

  # cov
  test_cov = TestCoverage("test/tools/conchpilotall.info")
  test_cov.transform_cov()

  # test files
  testfiles = []
  if fname:
    tf = TestFile(fname)
    tf.test_results = test_output.test_results
    tf.test_covs = test_cov.test_covs
    tf.report_dir = report_dir
    tf.generate_html()
    testfiles.append(tf)
  else:
    for filename in glob.glob("test/unit_test/**/*_test.cpp", recursive=True):
      # print(filename)
      tf = TestFile(filename)
      tf.test_results = test_output.test_results
      tf.test_covs = test_cov.test_covs
      tf.report_dir = report_dir
      tf.generate_html()
      testfiles.append(tf)

  # test report
  test_report = TestReport()
  test_report.testfiles = testfiles
  test_report.report_dir = report_dir
  test_report.generate_html()


def generate_html2(fname=None):

  here = os.path.dirname(os.path.abspath(__file__))
  # mod_path = files('gtest_report')
  print(here)


def main(fname=None):
  # generate_html(fname)

  fn = "test/unit_test/find_point/find_point_test.cpp"

  tf = TestFile(fn)
  tf.src_file = "src/find_point/find_point_new.cpp"
  func = TestFunc("FindPlanHandover", "")
  func.test_file = tf
  func.generate_cfg()


if __name__ == "__main__":
  # codelines = []
  # filename = "/home/conan/projects/conchpilot/src/adm_control/common/hysteresis_filter.cpp"
  # with open(filename) as f:
  #   codelines = f.readlines()

  # print(len(codelines))
  # print('=========================')
  # print(codelines[0].rstrip(),"***********")
  # print('=======================')
  # generate_html()

  import pkg_resources
  my_data = pkg_resources.resource_string(__name__, "foo.dat")

  # mod_path = files('gtest_report')
  print(my_data)
