#!/usr/bin/python
#coding=utf-8
"""Tests for comment_parser.parsers.go_parser.py"""

import unittest
from gtest_report.logic_flow import LogicFlow
from pprint import pprint


class LogicFlowTest(unittest.TestCase):

  lf = None

  def setUp(self):
    print("setup")

    self.lf = LogicFlow()

  def tearDown(self):
    print("teardown")

  def print_block(self, block):
    for block in block.child_blocks:
      print(block.start_no, block.end_no, block.code_lines[0])
      print("type:", block.block_type)
      if len(block.child_blocks) > 0:
        self.print_block(block)

  def test_SingleIf(self):
    code = """
    void Test::TestFunc() {
      if (DistToExH_Min <= 2.5)
      {
        bo_TransPoint = true;
        break;
      }
    }
    """

    block = self.lf.analysis(code)[0]

    self.assertEqual(len(block.child_blocks), 1)
    self.assertEqual(block.child_blocks[0].start_no, 2)
    self.assertEqual(block.child_blocks[0].end_no, 6)
    self.assertEqual(block.child_blocks[0].block_type, "if")

  def test_SingleIfNoBrace(self):
    code = """
    void Test::TestFunc() {
      if (DistToExH_Min <= 2.5)
        bo_TransPoint = true;

      if (DistToExH_Min > 5){
        bo_TransPoint = false;
      }
    }
    """

    block = self.lf.analysis(code)[0]

    self.assertEqual(len(block.child_blocks), 2)
    self.assertEqual(block.child_blocks[0].start_no, 2)
    self.assertEqual(block.child_blocks[0].end_no, 3)
    self.assertEqual(block.child_blocks[0].block_type, "if")

  def test_SingleIfElse(self):
    code = """
    void Test::TestFunc() {
      if (a <= 0)
      {
        b = true;
      }
      if (DistToExH_Min <= 2.5)
      {
        bo_TransPoint = true;
      }
      else
      {
        bo_TransPoint = false;
      }
    }
    """

    block = self.lf.analysis(code)[0]

    print("===========================")
    self.print_block(block)
    print("===========================")

    self.assertEqual(len(block.child_blocks), 2)
    self.assertEqual(block.child_blocks[0].start_no, 2)
    self.assertEqual(block.child_blocks[0].end_no, 5)
    self.assertEqual(block.child_blocks[0].block_type, "if")
    self.assertEqual(block.child_blocks[1].start_no, 6)
    self.assertEqual(block.child_blocks[1].end_no, 13)
    self.assertEqual(block.child_blocks[1].block_type, "ifelse")

  def test_SingleIfElseWithoutBackBrace(self):
    code = """
    void Test::TestFunc() {
      if (DistToExH_Min <= 2.5)
        bo_TransPoint = true;
      else
        bo_TransPoint = false;
    }
    """

    block = self.lf.analysis(code)[0]

    print("===========================")
    self.print_block(block)
    print("===========================")

    self.assertEqual(len(block.child_blocks), 1)
    self.assertEqual(block.child_blocks[0].start_no, 2)
    self.assertEqual(block.child_blocks[0].end_no, 5)
    self.assertEqual(block.child_blocks[0].block_type, "ifelse")

  def test_SingleFor(self):
    code = """
    void Test::TestFunc() {
      for(int i = ToHandover_Idx_temp;i >= 0 ; i--)
      {
        std::cout << "== ToHandover_Idx_temp " <<std::endl;
        std::cout << "DistHandover: " << DistHandover << std::endl;
      }
    }
    """
    block = self.lf.analysis(code)[0]

    print("===========================")
    self.print_block(block)
    print("===========================")

    self.assertEqual(len(block.child_blocks), 1)
    self.assertEqual(block.child_blocks[0].block_type, "for")
    self.assertEqual(block.child_blocks[0].start_no, 2)
    self.assertEqual(block.child_blocks[0].end_no, 6)

  def test_IfNestIf(self):
    code = """
    void Test::TestFunc() {
      if(bo_TransPoint == true)
      {
        std::cout << "Index: " << FP_stPlanToDwa_.nPlanToDwaIdx << std::endl;
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
    }
    """
    block = self.lf.analysis(code)[0]
    print("===========================")
    self.print_block(block)
    print("===========================")
    self.assertEqual(len(block.child_blocks), 1)
    self.assertEqual(block.child_blocks[0].block_type, "if")
    self.assertEqual(block.child_blocks[0].start_no, 2)
    self.assertEqual(block.child_blocks[0].end_no, 15)
    self.assertEqual(block.child_blocks[0].child_blocks[0].block_type, "ifelse")
    self.assertEqual(block.child_blocks[0].child_blocks[0].start_no, 5)
    self.assertEqual(block.child_blocks[0].child_blocks[0].end_no, 14)

  def test_SingleForNestIf(self):
    code = """
    void Test::TestFunc() {
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
    }
    """
    block = self.lf.analysis(code)[0]
    print("===========================")
    self.print_block(block)
    print("===========================")

    self.assertEqual(len(block.child_blocks), 1)
    self.assertEqual(block.child_blocks[0].block_type, "for")
    self.assertEqual(block.child_blocks[0].start_no, 2)
    self.assertEqual(block.child_blocks[0].end_no, 11)
    self.assertEqual(block.child_blocks[0].child_blocks[0].block_type, "if")
    self.assertEqual(block.child_blocks[0].child_blocks[0].start_no, 6)
    self.assertEqual(block.child_blocks[0].child_blocks[0].end_no, 10)

  def test_ForNestFor(self):
    code = """
    void Test::TestFunc() {
      for (int d = max(20,int(DistToEx_Min)); d < 120; d++)
      {
          std::cout << "min_nearest:" << min_nearest << std::endl;
          std::cout << "max_nearest:" << max_nearest << std::endl;
          for (int j = min_nearest; j < max_nearest; j++)
          {
              std::cout << "j:" << j << std::endl;
          }
      }
    }
    """
    block = self.lf.analysis(code)[0]

    print("===========================")
    self.print_block(block)
    print("===========================")

    self.assertEqual(len(block.child_blocks), 1)
    self.assertEqual(block.child_blocks[0].block_type, "for")
    self.assertEqual(block.child_blocks[0].start_no, 2)
    self.assertEqual(block.child_blocks[0].end_no, 10)
    self.assertEqual(block.child_blocks[0].child_blocks[0].block_type, "for")
    self.assertEqual(block.child_blocks[0].child_blocks[0].start_no, 6)
    self.assertEqual(block.child_blocks[0].child_blocks[0].end_no, 9)
