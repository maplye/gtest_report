#!/usr/bin/python
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
    print("===========================")
    print(block_codes)
    print("===========================")

    self.assertEqual(len(block_codes), 1)

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
    pprint(block_codes)
    print("===========================")

    self.assertEqual(len(block_codes), 2)
    self.assertEqual(len(block_codes[0]), 5)
    self.assertEqual(len(block_codes[1]), 4)
     
  
  

  def testSingleFor(self):
    code = """
    for(int i = ToHandover_Idx_temp;i >= 0 ; i--) 
    {
      std::cout << "== ToHandover_Idx_temp " <<std::endl;
      std::cout << "DistHandover: " << DistHandover << std::endl;
    }
    """
    condition = analysis(code)[0]
    
    self.assertEqual(condition.block_type, "for")
    self.assertEqual(condition.start_no, 1)
    self.assertEqual(condition.end_no, 5)
    self.assertEqual(condition.body_start_no, 3)
    self.assertEqual(condition.body_end_no, 4)
    
  def testIfNestIf(self):
    code = """void FindPoint::FindPlanHandover(std::vector<std::vector<double>> waypoint)
    {
    if (DistToExH_Min <= 2.5)
    {
      std::cout << "== ToHandover_Idx_temp " <<std::endl;
      std::cout << "DistHandover: " << DistHandover << std::endl;
      if(DistHandover >= 50.0)
      {
          FP_stPlanToDwa_.nVirtualPIdx = i;
          if(DistHandover >= 30.0)
          {
              std::cout << DistHandover << std::endl;
          }
          break;
      }
    }
    }"""
    block_codes = analysis(code)
    print("===========================")
    pprint(block_codes)
    print("===========================")
    self.assertEqual(len(block_codes), 3)
    self.assertEqual(len(block_codes[0]), 14)
    self.assertEqual(len(block_codes[1]), 9)
    self.assertEqual(len(block_codes[2]), 4)


  def testSingleForNestIf(self):
    code = """for(int i = ToHandover_Idx_temp;i >= 0 ; i--) 
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
    condition = analysis(code)[0]
    
    self.assertEqual(condition.start_no, 1)
    self.assertEqual(condition.end_no, 5)
    self.assertEqual(condition.body, [3,4])

  def testSingleForNestFor(self):
    code = """for (int d = max(20,int(DistToEx_Min)); d < 120; d++)
    {
        std::cout << "min_nearest:" << min_nearest << std::endl;
        std::cout << "max_nearest:" << max_nearest << std::endl;
        for (int j = min_nearest; j < max_nearest; j++)      
        {
            std::cout << "j:" << j << std::endl;
        }
    }
    """
    condition = analysis(code)[0]
    
    self.assertEqual(condition.start_no, 1)
    self.assertEqual(condition.end_no, 5)
    self.assertEqual(condition.body, [3,4])


