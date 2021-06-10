#!/usr/bin/python
#coding=utf-8
"""Tests for comment_parser.parsers.go_parser.py"""

import unittest
from gtest_report.logic_flow import analysis
from pprint import pprint


class GoParserTest(unittest.TestCase):

  def testSingleIf(self):
    code = """
    if (DistToExH_Min <= 2.5)
    {
      bo_TransPoint = true;
      break;
    }
    """

    block_codes = analysis(code)

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

    block_codes = analysis(code)
    print("===========================")
    pprint([x.code_lines for x in block_codes])
    print("===========================")

    self.assertEqual(len(block_codes), 2)
    self.assertEqual(len(block_codes[0].code_lines), 5)
    self.assertEqual(len(block_codes[1].code_lines), 4)

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

    block_codes = analysis(code)
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
    condition = analysis(code)[0]

    # self.assertEqual(condition.block_type, "for")
    self.assertEqual(condition.start_no, 2)
    self.assertEqual(condition.end_no, 6)

  def testIfNestIf(self):
    code = u"""
    if(bo_TransPoint == true)
    {
        std::cout << "挖机朝向上存在与主路的交点P，交点的Index: " << FP_stPlanToDwa_.nPlanToDwaIdx << " 挖机的朝向角为:" << FP_stDestinationStatus_.dAngleHeading  << std::endl;
        if(FP_stPlanToDwa_.nPlanToDwaIdx  < FP_stPlanToDwa_.nNearestIdx)
        {
            ToHandover_Idx_temp = FP_stPlanToDwa_.nPlanToDwaIdx ;
            std::cout << "交点P在最近点E的左侧，基于交点P后退50m" << std::endl;
        }
        else
        {
            ToHandover_Idx_temp = FP_stPlanToDwa_.nNearestIdx;
            std::cout << "交点P在最近点E的右侧，基于最近点E后退50m" << std::endl;
        }
    }
    """
    block_codes = analysis(code)
    print("===========================")
    pprint([x.start_no for x in block_codes])
    print("===========================")
    self.assertEqual(len(block_codes), 3)
    self.assertEqual(block_codes[0].start_no, 2)
    self.assertEqual(block_codes[0].end_no, 15)
    self.assertEqual(block_codes[1].start_no, 5)
    self.assertEqual(block_codes[1].end_no, 11)
    self.assertEqual(block_codes[2].start_no, 10)
    self.assertEqual(block_codes[2].end_no, 16)

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
    blocks = analysis(code)

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
    blocks = analysis(code)

    print("===========================")
    pprint([x.code_lines for x in blocks])
    print("===========================")

    self.assertEqual(len(blocks), 2)
    self.assertEqual(blocks[0].start_no, 2)
    self.assertEqual(blocks[0].end_no, 10)
    self.assertEqual(blocks[1].start_no, 6)
    self.assertEqual(blocks[1].end_no, 11)
