#!/usr/bin/python
#coding=utf-8
"""Tests for comment_parser.parsers.go_parser.py"""

import unittest
from gtest_report.logic_flow import LogicFlow
from pprint import pprint


class LogicFlowTest(unittest.TestCase):

  lf = None

  def setUp(self):
    print("LF setup")

    self.lf = LogicFlow()

  def tearDown(self):
    print("LF teardown")

  def testSingleIf(self):
    code = """
    if (DistToExH_Min <= 2.5)
    {
      bo_TransPoint = true;
      break;
    }
    """

    block_codes = self.lf.analysis(code)

    self.assertEqual(len(block_codes), 1)
    self.assertEqual(block_codes[0].no, "C1")
    self.assertEqual(len(block_codes[0].code_lines), 5)

  def testSingleIfElse(self):
    code = """
    if (DistToExH_Min <= 2.5)
    {
      bo_TransPoint = true;
      break;
    }
    else
    {
      bo_TransPoint = false;
    }
    """

    block_codes = self.lf.analysis(code)
    print("=== block: ")
    pprint([x.code_lines for x in block_codes])
    print("=== branch-0: ")
    pprint([x.branchs[0].code_lines for x in block_codes])
    print("===========================")

    self.assertEqual(len(block_codes), 1)
    self.assertEqual(len(block_codes[0].branchs[0].code_lines), 5)

  def testSingleIfElseWithoutBackBrace(self):
    code = """
    if (DistToExH_Min <= 2.5)
    {
      bo_TransPoint = true;
      break;
    }
    else
      bo_TransPoint = false;
    """

    block_codes = self.lf.analysis(code)
    print("===========================")
    pprint([x.code_lines for x in block_codes])
    print("===========================")

    self.assertEqual(len(block_codes), 2)
    self.assertEqual(len(block_codes[0].code_lines), 5)
    self.assertEqual(len(block_codes[1].code_lines), 2)

  def testSingleFor(self):
    code = """
    for(int i = ToHandover_Idx_temp;i >= 0 ; i--)
    {
      std::cout << "== ToHandover_Idx_temp " <<std::endl;
      std::cout << "DistHandover: " << DistHandover << std::endl;
    }
    """
    condition = self.lf.analysis(code)[0]

    # self.assertEqual(condition.block_type, "for")
    self.assertEqual(condition.start_no, 2)
    self.assertEqual(condition.end_no, 6)

  def testIfNestIf(self):
    code = u"""
    if(bo_TransPoint == true)
    {
        std::cout << "Index: " << FP_stPlanToDwa_.nPlanToDwaIdx << " angle:" << FP_stDestinationStatus_.dAngleHeading  << std::endl;
        if(FP_stPlanToDwa_.nPlanToDwaIdx  < FP_stPlanToDwa_.nNearestIdx)
        {
            ToHandover_Idx_temp = FP_stPlanToDwa_.nPlanToDwaIdx ;
            std::cout << "left back 50m" << std::endl;
        }
        else
        {
            ToHandover_Idx_temp = FP_stPlanToDwa_.nNearestIdx;
            std::cout << "right forward 50m" << std::endl;
        }
    }
    """
    block_codes = self.lf.analysis(code)
    print("===========================")
    pprint([x.start_no for x in block_codes])
    print("===========================")
    self.assertEqual(len(block_codes), 2)
    self.assertEqual(block_codes[0].start_no, 2)
    self.assertEqual(block_codes[0].end_no, 15)
    self.assertEqual(block_codes[1].start_no, 5)
    self.assertEqual(block_codes[1].end_no, 11)

  def testSingleForNestIf(self):
    code = """
    for(int i = ToHandover_Idx_temp;i >= 0 ; i--)
    {
      std::cout << "== ToHandover_Idx_temp " <<std::endl;
      std::cout << "DistHandover: " << DistHandover << std::endl;
      if(DistHandover >= 50.0)
      {
          FP_stPlanToDwa_.nVirtualPIdx = i;
          break;
      }
    }
    """
    blocks = self.lf.analysis(code)

    self.assertEqual(len(blocks), 2)
    self.assertEqual(blocks[0].start_no, 2)
    self.assertEqual(blocks[0].end_no, 11)
    self.assertEqual(blocks[1].start_no, 6)
    self.assertEqual(blocks[1].end_no, 12)

  def testForNestFor(self):
    code = """
    for (int d = max(20,int(DistToEx_Min)); d < 120; d++)
    {
        std::cout << "min_nearest:" << min_nearest << std::endl;
        std::cout << "max_nearest:" << max_nearest << std::endl;
        for (int j = min_nearest; j < max_nearest; j++)
        {
            std::cout << "j:" << j << std::endl;
        }
    }
    """
    blocks = self.lf.analysis(code)

    print("===========================")
    pprint([x.code_lines for x in blocks])
    print("===========================")

    self.assertEqual(len(blocks), 2)
    self.assertEqual(blocks[0].start_no, 2)
    self.assertEqual(blocks[0].end_no, 10)
    self.assertEqual(blocks[1].start_no, 6)
    self.assertEqual(blocks[1].end_no, 11)
