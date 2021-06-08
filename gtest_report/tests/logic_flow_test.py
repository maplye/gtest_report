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
    
    self.assertEqual(condition.block_type, "for")
    self.assertEqual(condition.start_no, 1)
    self.assertEqual(condition.end_no, 5)
    self.assertEqual(condition.body_start_no, 3)
    self.assertEqual(condition.body_end_no, 4)
    
  def testIfNestIf(self):
    code = u"""void FindPoint::FindPlanHandover(std::vector<std::vector<double>> waypoint)
        {
            std::cout << "挖机位置update: " << std::setprecision(10) << FP_stDestinationStatus_.dPosLat << " " << FP_stDestinationStatus_.dPosLon << std::endl;
            std::cout << "路线长度waypoint[0].size(): " << waypoint[0].size() << std::endl;
            bool bo_TransPoint = false;//是否找到交接点
            int ToHandover_Idx_temp = 0;
            double DistToEx_temp = 0;
            double DistToExH_temp = 0;
            double DistToEx_Min= 10000.0;//挖机与路径点最短距离初始值
            double DistToExH_Min = 1000.0;//挖机指向与路径点的距离初始值
            double DistHandover = 0.0;
            /*找到路径上与挖机位置最近的点*/
            for (uint i = 0; i < waypoint[0].size(); i++)
            {
                GNSSToGlobal(FP_stDestinationStatus_.dPosLat, FP_stDestinationStatus_.dPosLon, waypoint[1][i], waypoint[2][i]);
                DistToEx_temp = sqrt(pow(FP_stEucDistance_.dX , 2) + pow(FP_stEucDistance_.dY, 2));
                
                if (DistToEx_temp < DistToEx_Min)
                {
                    DistToEx_Min = DistToEx_temp;
                    FP_stPlanToDwa_.nNearestIdx = i; //equal nearest_ids
                }
            }
            std::cout << "最近点Index(planning to dwa): " << FP_stPlanToDwa_.nNearestIdx << std::endl;
            std::cout << "挖机定位点到主路的距离:" << DistToEx_Min << std::endl;
            /*根据最短距离，选择DWA模式*/
            if (DistToEx_Min <= 41.0)
                FP_nDwaMode_ = DWA_ParkingMode_A;
            else
            {
                FP_nDwaMode_ = DWA_ParkingMode_B;
            }
            /*寻找交接点*/
            if(DistToEx_Min >= 20 && DistToEx_Min < 120 )
            {
                std::cout << "DistToEx_Min:" << DistToEx_Min << std::endl;
                for (int d = max(20,int(DistToEx_Min)); d < 120; d++)
                {
                    double x_hat = d * sin(FP_stDestinationStatus_.dAngleHeading  / 180 * M_PI);//挖机为坐标原点，行向角指向的坐标X
                    double y_hat = d * cos(FP_stDestinationStatus_.dAngleHeading  / 180 * M_PI);//挖机为坐标原点，行向角指向的坐标Y
                    int min_nearest = max(100,FP_stPlanToDwa_.nNearestIdx - 1000);
                    int max_nearest = min(FP_stPlanToDwa_.nNearestIdx + 1000,int(waypoint[0].size()));
                    std::cout << "min_nearest:" << min_nearest << std::endl;
                    std::cout << "max_nearest:" << max_nearest << std::endl;
                    for (int j = min_nearest; j < max_nearest; j++)      
                    {
                        GNSSToGlobal(FP_stDestinationStatus_.dPosLat, FP_stDestinationStatus_.dPosLon, waypoint[1][j], waypoint[2][j]);
                        double DistToExH_temp = sqrt(pow((FP_stEucDistance_.dX  - x_hat), 2) + pow((FP_stEucDistance_.dY - y_hat), 2));
                        if (DistToExH_temp < DistToExH_Min)
                        {
                            DistToExH_Min = DistToExH_temp;
                            FP_stPlanToDwa_.nPlanToDwaIdx = j;
                        }
                        std::cout << "j:" << j << std::endl;
                    }
                    if (DistToExH_Min <= 2.5)
                    {
                        std::cout << "找到交接点" << std::endl;
                        bo_TransPoint = true;
                        break;
                    }
                }
            }
            else
            {
                std::cout << "最近点距离不在范围内" << std::endl;
                 bo_TransPoint = false;
                 FP_stPlanToDwa_.nPlanToDwaIdx = FP_stPlanToDwa_.nNearestIdx;
            }            
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
            else
            {
                ToHandover_Idx_temp = FP_stPlanToDwa_.nNearestIdx;//使用距离最近点计算终点
                std::cout << "找不到交接点，基于最近点E后退50m, point: " << ToHandover_Idx_temp <<std::endl;
            }
            for(int i = ToHandover_Idx_temp;i >= 0 ; i--) 
            {
                std::cout << "== ToHandover_Idx_temp " <<std::endl;
                GNSSToGlobal(waypoint[1][ToHandover_Idx_temp], waypoint[2][ToHandover_Idx_temp], waypoint[1][i], waypoint[2][i]); 
                DistHandover = sqrt(pow(FP_stEucDistance_.dX , 2) + pow(FP_stEucDistance_.dY, 2));
                std::cout << "(x,y): " << FP_stEucDistance_.dX << "," << FP_stEucDistance_.dY <<std::endl;
                std::cout << "(l,l): " << waypoint[1][i] << "," << waypoint[2][i] <<std::endl;
                std::cout << "DistHandover: " << DistHandover << std::endl;
                if(DistHandover >= 50.0)
                {
                    FP_stPlanToDwa_.nVirtualPIdx = i;//计算钝角的虚拟点
                    break;
                }
            }
            if(DistHandover < 50)//未找找到50m的点，取最近点
            {
                std::cout << "未找找到50m的点，取最近点" << std::endl;
                FP_stPlanToDwa_.nVirtualPIdx = ToHandover_Idx_temp;
            }
            std::cout << "最终的交接点为" <<FP_stPlanToDwa_.nVirtualPIdx<<std::endl;
            FP_stPlanToDwa_.nPlanToDwaIdx  = FP_stPlanToDwa_.nVirtualPIdx;
            FP_stPlanToDwa_.dPlanToDwaLat = waypoint[1][FP_stPlanToDwa_.nPlanToDwaIdx];
            FP_stPlanToDwa_.dPlanToDwaLon = waypoint[2][FP_stPlanToDwa_.nPlanToDwaIdx];
            FP_stPlanToDwa_.dNearestLat = waypoint[1][FP_stPlanToDwa_.nNearestIdx];
            FP_stPlanToDwa_.dNearestLon = waypoint[2][FP_stPlanToDwa_.nNearestIdx];
            FP_stPlanToDwa_.dVirtualPLat = waypoint[1][FP_stPlanToDwa_.nVirtualPIdx];
            FP_stPlanToDwa_.dVirtualPLon = waypoint[2][FP_stPlanToDwa_.nVirtualPIdx];

        }"""
    block_codes = analysis(code)
    print("===========================")
    pprint([x.start_no for x in block_codes])
    print("===========================")
    self.assertEqual(len(block_codes), 4)
    self.assertEqual(len(block_codes[0]), 18)
    self.assertEqual(len(block_codes[1]), 13)
    self.assertEqual(len(block_codes[2]), 4)
    self.assertEqual(len(block_codes[3]), 4)


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


