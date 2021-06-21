#!/usr/bin/env python3
import logging

from gtest_report import testresult

if __name__ == "__main__":

  logging.basicConfig(level=logging.DEBUG,
                      format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

  testresult.main()
