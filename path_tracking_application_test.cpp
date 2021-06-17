/******************************************************************************
 * Copyright (c) The Conch Global Authors. 2021 .All Rights Reserved.
 * Description:
 * unit test code for planning
 *
 * Author: Yao Guorong
 * Create: 2021-04-29
 *****************************************************************************/
#include "common/basetest.h"
#include "planning/path_tracking_application.h"

using namespace conch::testing;

namespace conch
{
namespace planning
{

class PathTrackingApplicationTest : public BaseTest {
protected: 
  PathTrackingApplication pta;

  virtual void SetUp() {
    pta.kc1 = 1.5;
    pta.kc2 = 1.2;
    pta.kc3 = 1.0;
    pta.ke = 0.0;
    // pta.ks = 0.35;
    pta.k_se = 0;
    // pta.dispre_min = 5.0;
    pta.dispre_max = 18.0;
    pta.curvityMax = 0.01;
    pta.curvityMax1 = 0.01;
    pta.curvityMax2 = 0.01;
  }

  virtual void TearDown() {
  }

  PathTrackingApplicationTest() {
  }

  ~PathTrackingApplicationTest() {
  }

  // 用于测试的路径，从data_record/uA_110_xy.csv中获取40-45行
  std::vector<std::vector<double>> waypoints = {
    {3.9005881807,4.0054939754,4.1103997676,4.2153055623,4.3202113594,4.4251171516},
    {2.3039161935,2.3693305668,2.4358536629,2.5034854724,2.5711172861,2.6387490993},
    {31.55048337,31.78801368,32.04309483,32.31432073,32.60034841,32.89989805},
    {7.526479563,7.525849731,7.525249959,7.524678656,7.524134837,7.523616692},
    {1,1,1,1,1,1},
    {-0.0535,-0.0533,-0.0529,-0.0526,-0.0523,-0.052}
  };
  // 带弯道的路径点
  std::vector<std::vector<double>> waypoints_curve = {
    {3.9005881807,4.0054939754,4.1103997676,4.2153055623,4.3202113594,4.4251171516},
    {2.3039161935,2.3693305668,2.4358536629,2.5034854724,2.5711172861,2.6387490993},
    {31.55048337,31.78801368,32.04309483,32.31432073,32.60034841,32.89989805},
    {7.526479563,7.525849731,7.525249959,7.524678656,7.524134837,7.523616692},
    {1,1,1,1,1,1},
    {0.0535,0.0533,0.0529,0.0526,0.0523,0.052}
  };

  //模拟Last_steering_angle_des = 40
  void updateSteeringAngleDesSimulate(){
    // 当前档位
    pta.gear_current_ = -1;
    // 当前车速
    pta.velocity_current_ = 10;
    // 预瞄位置曲率
    pta.preview_curvature_ = 0.02;
    // 横向误差
    pta.error_lateral_r_=NAN;
    // 预瞄点序列长度
    pta.prepoint_sequence_length_ = 3;
    // 预瞄点序列
    Eigen::MatrixXd seqPre(3, 3);
    seqPre(0, 0) = 1;
    seqPre(1, 0) = 1;
    seqPre(2, 0) = 1;
    seqPre(0, 1) = 8.5;
    seqPre(1, 1) = 8.5;
    seqPre(2, 1) = 1;
    seqPre(0, 2) = 9.8;
    seqPre(1, 2) = 9.8;
    seqPre(2, 2) = 1;
    pta.seq_pre_point = seqPre;
    // 车轮距离
    pta.wheel_base_ = 4.57;
    // 路线点
    pta.waypoint_= {
      {1,2,3},
      {1,2,3},
      {18,15,12},
      {-10.30,-12.30,-14.30},
      {-10.30,-12.30,-14.30},
      {-10.30,-12.30,-14.30}
    };
    
    pta.ind_current_front_ = 0;
    pta.heading_current_ = 1;

    pta.updateSteeringAngleDes();
  }

};


/******************************************************************************
 * @pathTracking
 * 输出期望路径，当前demo场景路径由决策给出，后续由卡调给出
 *****************************************************************************/
// #pathTracking-imu state is wrong
TEST_F(PathTrackingApplicationTest, pathTracking_imu_state_is_wrong) {
  pta.imu_state_ = 3;
  // pta.imu_state_last_ = 3;

  pta.pathTracking();

  // TODO: 获取日志信息
}

// #pathTracking-steer control state is wrong
TEST_F(PathTrackingApplicationTest, pathTracking_steer_control_state_is_wrong) {
  pta.steer_control_state_ = 0xFF;
  // pta.imu_state_last_ = 3;

  pta.pathTracking();

  // TODO: 获取日志信息
}

// #pathTracking-drive mode changed
TEST_F(PathTrackingApplicationTest, pathTracking_drive_mode_changed) {
  pta.drive_mode_ = 1;

  pta.pathTracking();

  // TODO: 获取日志信息
  // TODO: 只执行了一次，对后面函数调用是否有影响
  // routeIsNew = true 
}

// #pathTracking-road list changed
TEST_F(PathTrackingApplicationTest, pathTracking_road_list_changed) {
  // >没有进入DWA
  pta.parking_control_ = 0;
  pta.road_list_ = "a";
  pta.last_road_list_ = "b";

  // pta.pathTracking();

  // TODO: 发送数据和逻辑分离
  // <ParkingEnd
}

// #pathTracking
TEST_F(PathTrackingApplicationTest, pathTracking) {
  // >不进入DWA控制
  pta.parking_control_ = 0;
  // >路径点更新完成
  pta.data_fill_flag_ = 1;
  // >坐标原点
  pta.B0_ = 31.13554949;
  pta.L0_ = 118.1772826;
  // >前后轮距离
  pta.wheel_base_ = 4.57;
  // >前进路径点
  pta.waypoint_temp_forward_ = waypoints;
  // >回程路径点
  pta.waypoint_temp_backoff_ = waypoints;
  // >planning to dwa index
  pta.ids8_ = 6;
  // >卡调任务为卸料作业 上山
  pta.dc_command_ = 1;
  // >实际速度
  pta.velocity_current_ = 10;
  // >实际加速度
  pta.a_actual_ = 1;
  // >障碍物
  pta.MainTarget.LonDis = 87.5;
  pta.MainTarget.length_ = 10;
  // >执行器相应延迟
  pta.time_delay_ = 0.7;
  // >当前经纬度
  pta.latitude_current_ = 31.13555006;
  pta.longitude_current_ = 118.1772837;
  // >当前航向角
  pta.heading_current_ = 1;
  // >当前转向角
  pta.steering_angle_current_ = 10;
  pta.pre_index_ = 1;
  pta.speed_limit_charge_ = 30;
  pta.speed_limit_discharge_ = 20;

  pta.pathTracking();
  // TODO
  // <期望速度
  // EXPECT_DOUBLE_EQ(pta.velocity_des_, 0);
  // <期望转角
  // EXPECT_DOUBLE_EQ(pta.steering_angle_des_, 0);
}

// #pathTracking hybrid_astar
TEST_F(PathTrackingApplicationTest, pathTracking_hybrid_astar) {
  // >hybrid_astar
  pta.parking_control_ = 2;
  // >路径点更新完成
  pta.data_fill_flag_ = 1;
  // >坐标原点
  pta.B0_ = 31.13554949;
  pta.L0_ = 118.1772826;
  // >前后轮距离
  pta.wheel_base_ = 4.57;
  // >前进路径点
  pta.waypoint_temp_forward_ = waypoints;
  // >回程路径点
  pta.waypoint_temp_backoff_ = waypoints;
  // >planning to dwa index
  pta.ids8_ = 6;
  // >卡调任务为卸料作业 上山
  pta.dc_command_ = 1;
  // >实际速度
  pta.velocity_current_ = 10;
  // >实际加速度
  pta.a_actual_ = 1;
  // >障碍物
  pta.MainTarget.LonDis = 87.5;
  pta.MainTarget.length_ = 10;
  // >执行器相应延迟
  pta.time_delay_ = 0.7;
  // >当前经纬度
  pta.latitude_current_ = 31.13555006;
  pta.longitude_current_ = 118.1772837;
  // >当前航向角
  pta.heading_current_ = 1;
  // >当前转向角
  pta.steering_angle_current_ = 10;
  pta.pre_index_ = 1;
  pta.speed_limit_charge_ = 30;
  pta.speed_limit_discharge_ = 20;
  
  pta.waypoint_ = {
    {3.9005881807,4.0054939754,4.1103997676,4.2153055623,4.3202113594,4.4251171516},
    {2.3039161935,2.3693305668,2.4358536629,2.5034854724,2.5711172861,2.6387490993},
    {31.55048337,31.78801368,32.04309483,32.31432073,32.60034841,32.89989805},
    {7.526479563,7.525849731,7.525249959,7.524678656,7.524134837,7.523616692},
    {1,1,1,1,1,1},
    {-0.0535,-0.0533,-0.0529,-0.0526,-0.0523,-0.052}
  };

  pta.wayPoint_forword = {
    {3.9005881807,4.0054939754,4.1103997676,4.2153055623,4.3202113594,4.4251171516},
    {2.3039161935,2.3693305668,2.4358536629,2.5034854724,2.5711172861,2.6387490993},
    {31.55048337,31.78801368,32.04309483,32.31432073,32.60034841,32.89989805},
    {7.526479563,7.525849731,7.525249959,7.524678656,7.524134837,7.523616692},
    {1,1,1,1,1,1},
    {-0.0535,-0.0533,-0.0529,-0.0526,-0.0523,-0.052}
  };
  pta.wayPoint_backoff = {
    {3.9005881807,4.0054939754,4.1103997676,4.2153055623,4.3202113594,4.4251171516},
    {2.3039161935,2.3693305668,2.4358536629,2.5034854724,2.5711172861,2.6387490993},
    {31.55048337,31.78801368,32.04309483,32.31432073,32.60034841,32.89989805},
    {7.526479563,7.525849731,7.525249959,7.524678656,7.524134837,7.523616692},
    {1,1,1,1,1,1},
    {-0.0535,-0.0533,-0.0529,-0.0526,-0.0523,-0.052}
  };

  pta.pathTracking();
  // TODO
  // <期望速度
  // EXPECT_DOUBLE_EQ(pta.velocity_des_, 0);
  // <期望转角
  // EXPECT_DOUBLE_EQ(pta.steering_angle_des_, 0);
}


// #pathTracking - backoff
TEST_F(PathTrackingApplicationTest, pathTracking_backoff) {
  // >不进入DWA控制
  pta.parking_control_ = 0;
  // >路径点更新完成
  pta.data_fill_flag_ = 1;
  // >坐标原点
  pta.B0_ = 31.13554949;
  pta.L0_ = 118.1772826;
  // >前后轮距离
  pta.wheel_base_ = 4.57;
  // >前进路径点
  pta.waypoint_temp_forward_ = waypoints;
  // >回程路径点
  pta.waypoint_temp_backoff_ = waypoints;
  // >planning to dwa index
  pta.ids8_ = 6;
  // >卡调任务为卸料作业 下山
  pta.dc_command_ = 2;
  pta.end_ = 1;
  // >实际速度
  pta.velocity_current_ = 10;
  // >实际加速度
  pta.a_actual_ = 1;
  // >障碍物
  pta.MainTarget.LonDis = 87.5;
  pta.MainTarget.length_ = 10;
  // >执行器相应延迟
  pta.time_delay_ = 0.7;
  // >当前经纬度
  pta.latitude_current_ = 31.13555006;
  pta.longitude_current_ = 118.1772837;
  // >当前航向角
  pta.heading_current_ = 1;
  // >当前转向角
  pta.steering_angle_current_ = 10;
  pta.pre_index_ = 0;
  pta.speed_limit_charge_ = 30;
  pta.speed_limit_discharge_ = 20;

  // 第一次执行
  pta.pathTracking();
  // 第二次执行进入backoff
  pta.pathTracking();

  // <期望速度
  EXPECT_DOUBLE_EQ(pta.velocity_des_, 0);
  // <期望转角
  EXPECT_GE(pta.steering_angle_des_, 0);
}

// #pathTracking - ind_handover_0
TEST_F(PathTrackingApplicationTest, pathTracking_ind_handover_0) {
  // >不进入DWA控制
  pta.parking_control_ = 0;
  // >路径点更新完成
  pta.data_fill_flag_ = 1;
  // >坐标原点
  pta.B0_ = 31.13554949;
  pta.L0_ = 118.1772826;
  // >前后轮距离
  pta.wheel_base_ = 4.57;
  // >前进路径点
  pta.waypoint_temp_forward_ = waypoints;
  // >回程路径点
  pta.waypoint_temp_backoff_ = waypoints;
  // >planning to dwa index
  pta.ids8_ = 0;
  // >卡调任务为卸料作业 下山
  pta.dc_command_ = 1;
  pta.end_ = 1;
  // >实际速度
  pta.velocity_current_ = 10;
  // >实际加速度
  pta.a_actual_ = 1;
  // >障碍物
  pta.MainTarget.LonDis = 87.5;
  pta.MainTarget.length_ = 10;
  // >执行器相应延迟
  pta.time_delay_ = 0.7;
  // >当前经纬度
  pta.latitude_current_ = 31.13555006;
  pta.longitude_current_ = 118.1772837;
  // >当前航向角
  pta.heading_current_ = 1;
  // >当前转向角
  pta.steering_angle_current_ = 10;
  pta.pre_index_ = 0;
  pta.speed_limit_charge_ = 30;
  pta.speed_limit_discharge_ = 20;

  pta.pathTracking();

  // <期望速度
  EXPECT_DOUBLE_EQ(pta.velocity_des_, 0);
  // <期望转角
  EXPECT_GE(pta.steering_angle_des_, 0);
}


/******************************************************************************
 * @updateVelocityDes
 * update the desire steering velocity
 *****************************************************************************/
// #updateVelocityDes
TEST_F(PathTrackingApplicationTest, updateVelocityDes) {
  pta.x_current_rear_ = -190.90;
  pta.y_current_rear_ = -8.30;
  // >后续路线
  pta.waypoint_temp_backoff_ = waypoints;
  // >卡调任务为卸料作业
  pta.dc_command_ = 1;
  // >期望档位
  pta.gear_des_ = 1;
  // >实际速度
  pta.velocity_current_ = 10;
  // >实际加速度
  pta.a_actual_ = 1;
  // >路线点
  pta.waypoint_= waypoints;

  pta.end_ = 0;
  
  pta.MainTarget.length_ = 10;
  pta.main_dis_ = 87.5;
  pta.data_fill_flag_ = 1;
  pta.error_lateral_r_ = 1;
  pta.ind_current_rear_ = 0;
  pta.pre_index_ = 0;

  pta.updateVelocityDes();

  // <期望速度
  // 10.9504 11.9008
  EXPECT_NEAR(pta.velocity_des_, 10.9504, 3);
}

// #updateVelocityDes
TEST_F(PathTrackingApplicationTest, updateVelocityDes_end) {
  pta.x_current_rear_ = -190.90;
  pta.y_current_rear_ = -8.30;
  // >后续路线
  pta.waypoint_temp_backoff_ = waypoints;
  // >卡调任务为卸料作业
  pta.dc_command_ = 1;
  // >期望档位
  pta.gear_des_ = 1;
  // >实际速度
  pta.velocity_current_ = 10;
  // >实际加速度
  pta.a_actual_ = 1;
  // >路线点
  pta.waypoint_= waypoints;
  // >到达路径终点
  pta.end_ = 1;
  
  pta.MainTarget.length_ = 10;
  pta.main_dis_ = 87.5;
  pta.data_fill_flag_ = 1;
  pta.error_lateral_r_ = 1;
  pta.ind_current_rear_ = 0;
  pta.pre_index_ = 0;

  pta.updateVelocityDes();

  // <期望速度
  EXPECT_EQ(pta.velocity_des_, 0);
}

// #updateVelocityDes在弯道，进行减速
TEST_F(PathTrackingApplicationTest, updateVelocityDes_curvature) {
  pta.x_current_rear_ = -190.90;
  pta.y_current_rear_ = -8.30;
  // >后续路线
  pta.waypoint_temp_backoff_ = waypoints;
  // >卡调任务为卸料作业
  pta.dc_command_ = 1;
  // >期望档位
  pta.gear_des_ = 1;
  // >实际速度
  pta.velocity_current_ = 10;
  // >实际加速度
  pta.a_actual_ = 1;
  // >路线点
  pta.waypoint_= waypoints_curve;
  pta.end_ = 0;
  
  pta.MainTarget.length_ = 10;
  pta.main_dis_ = 87.5;
  pta.data_fill_flag_ = 1;
  pta.error_lateral_r_ = 1;
  pta.ind_current_rear_ = 0;
  pta.pre_index_ = 0;

  pta.updateVelocityDes();

  // <期望速度
  // 10.9504 11.9008
  EXPECT_NEAR(pta.velocity_des_, 10.9504, 3);
}

// #updateVelocityDes在弯道，进行减速
TEST_F(PathTrackingApplicationTest, updateVelocityDes_obs_distance_30) {
  pta.x_current_rear_ = -190.90;
  pta.y_current_rear_ = -8.30;
  // >后续路线
  pta.waypoint_temp_backoff_ = waypoints;
  // >卡调任务为卸料作业
  pta.dc_command_ = 1;
  // >期望档位
  pta.gear_des_ = 1;
  // >实际速度
  pta.velocity_current_ = 10;
  // >实际加速度
  pta.a_actual_ = 1;
  // >路线点
  pta.waypoint_= waypoints_curve;
  
  pta.MainTarget.length_ = 10;
  pta.main_dis_ = 27.5;
  pta.data_fill_flag_ = 1;
  pta.error_lateral_r_ = 1;
  pta.ind_current_rear_ = 0;
  pta.pre_index_ = 0;
  pta.data_fill_flag_ = 0;
  pta.end_ = 0;

  pta.updateVelocityDes();

  // <期望速度
  // 10.9504 11.9008
  EXPECT_EQ(pta.velocity_des_, 0);
}

// #updateVelocityDes在弯道，进行减速
TEST_F(PathTrackingApplicationTest, updateVelocityDes_error_lateral_r_2) {
  pta.x_current_rear_ = -190.90;
  pta.y_current_rear_ = -8.30;
  // >后续路线
  pta.waypoint_temp_backoff_ = waypoints;
  // >卡调任务为卸料作业
  pta.dc_command_ = 1;
  // >期望档位
  pta.gear_des_ = 1;
  // >实际速度
  pta.velocity_current_ = 10;
  // >实际加速度
  pta.a_actual_ = 1;
  // >路线点
  pta.waypoint_= waypoints_curve;
  
  pta.MainTarget.length_ = 10;
  pta.main_dis_ = 87.5;
  pta.data_fill_flag_ = 1;
  pta.error_lateral_r_ = 2.1;
  pta.ind_current_rear_ = 0;
  pta.pre_index_ = 0;
  pta.end_ = 0;

  pta.updateVelocityDes();

  // <期望速度
  // 10.9504 11.9008
  EXPECT_EQ(pta.velocity_des_, 5.0);
}

// #updateVelocityDes在弯道，进行减速
TEST_F(PathTrackingApplicationTest, updateVelocityDes_error_lateral_r_1_5) {
  pta.x_current_rear_ = -190.90;
  pta.y_current_rear_ = -8.30;
  // >后续路线
  pta.waypoint_temp_backoff_ = waypoints;
  // >卡调任务为卸料作业
  pta.dc_command_ = 1;
  // >期望档位
  pta.gear_des_ = 1;
  // >实际速度
  pta.velocity_current_ = 10;
  // >实际加速度
  pta.a_actual_ = 1;
  // >路线点
  pta.waypoint_= waypoints_curve;
  
  pta.MainTarget.length_ = 10;
  pta.main_dis_ = 87.5;
  pta.data_fill_flag_ = 1;
  pta.error_lateral_r_ = 1.6;
  pta.ind_current_rear_ = 0;
  pta.pre_index_ = 0;
  pta.end_ = 0;

  pta.updateVelocityDes();

  // <期望速度
  // 10.9504 11.9008
  EXPECT_EQ(pta.velocity_des_, 10.0);
}

// #updateVelocityDes在弯道，进行减速
TEST_F(PathTrackingApplicationTest, updateVelocityDes_error_lateral_r_20) {
  pta.x_current_rear_ = -190.90;
  pta.y_current_rear_ = -8.30;
  // >后续路线
  pta.waypoint_temp_backoff_ = waypoints;
  // >卡调任务为卸料作业
  pta.dc_command_ = 1;
  // >期望档位
  pta.gear_des_ = 1;
  // >实际速度
  pta.velocity_current_ = 10;
  // >实际加速度
  pta.a_actual_ = 1;
  // >路线点
  pta.waypoint_= waypoints_curve;
  
  pta.MainTarget.length_ = 10;
  pta.main_dis_ = 87.5;
  pta.data_fill_flag_ = 1;
  pta.error_lateral_r_ = 20.1;
  pta.ind_current_rear_ = 0;
  pta.pre_index_ = 0;
  pta.end_ = 0;

  pta.updateVelocityDes();

  // <期望速度
  // 10.9504 11.9008
  EXPECT_EQ(pta.velocity_des_, 0);
}

// #updateVelocityDes在弯道，进行减速
TEST_F(PathTrackingApplicationTest, updateVelocityDes_dc_vehcontrol_req_4) {
  pta.x_current_rear_ = -190.90;
  pta.y_current_rear_ = -8.30;
  // >后续路线
  pta.waypoint_temp_backoff_ = waypoints;
  // >卡调任务为卸料作业
  pta.dc_command_ = 1;
  // >期望档位
  pta.gear_des_ = 1;
  // >实际速度
  pta.velocity_current_ = 10;
  // >实际加速度
  pta.a_actual_ = 1;
  // >路线点
  pta.waypoint_= waypoints_curve;
  
  pta.MainTarget.length_ = 10;
  pta.main_dis_ = 87.5;
  pta.data_fill_flag_ = 1;
  pta.error_lateral_r_ = 1;
  pta.ind_current_rear_ = 0;
  pta.pre_index_ = 0;
  pta.dc_vehcontrol_req_ = 4;
  pta.end_ = 0;

  pta.updateVelocityDes();

  // <期望速度
  // 10.9504 11.9008
  EXPECT_EQ(pta.velocity_des_, 0);
}

/******************************************************************************
 * @updateSteeringAngleDes
 * update the desire steering angle based on Pure Pursuit and Stanley
 *****************************************************************************/
// #前进
TEST_F(PathTrackingApplicationTest, updateSteeringAngleDes) {
  updateSteeringAngleDesSimulate();
  // >当前档位
  pta.gear_current_ = -2;
  // >当前车速
  pta.velocity_current_ = 10;
  // >预瞄位置曲率
  pta.preview_curvature_ = 0.02;
  // >横向误差
  pta.error_lateral_r_=2;
  // >预瞄点序列长度
  pta.prepoint_sequence_length_ = 3;
  // >预瞄点序列
  Eigen::MatrixXd seqPre(3, 3);
  seqPre(0, 0) = 1;
  seqPre(1, 0) = 1;
  seqPre(2, 0) = 1;
  seqPre(0, 1) = 8.5;
  seqPre(1, 1) = 8.5;
  seqPre(2, 1) = 1;
  seqPre(0, 2) = 9.8;
  seqPre(1, 2) = 9.8;
  seqPre(2, 2) = 1;
  pta.seq_pre_point = seqPre;
  // >车轮距离
  pta.wheel_base_ = 4.57;
  // >路线点
  pta.waypoint_= {{-192.90,-198.90,-199.90},{-10.30,-12.30,-14.30},
    {-10.30,-12.30,-14.30},{-10.30,-12.30,-14.30},
    {-10.30,-12.30,-14.30},{-0.005,0.005,0.005}};
  
  pta.ind_current_front_ = 0;
  pta.curvityMax1 = 0.01;
  pta.kc1 = 1.5;
  pta.kc3 = 1.0;
  pta.steering_angle_current_ = 210;
  pta.heading_current_ = 1;

  pta.updateSteeringAngleDes();

  // <期望转角
  EXPECT_DOUBLE_EQ(pta.steering_angle_des_, 40);
}


// #前进
TEST_F(PathTrackingApplicationTest, updateSteeringAngleDes_curvityCurrent) {
  updateSteeringAngleDesSimulate();
  // >当前档位
  pta.gear_current_ = -2;
  // >当前车速
  pta.velocity_current_ = 10;
  // >预瞄位置曲率
  pta.preview_curvature_ = 0.02;
  // >横向误差
  pta.error_lateral_r_=10;
  // >预瞄点序列长度
  pta.prepoint_sequence_length_ = 3;
  // >预瞄点序列
  Eigen::MatrixXd seqPre(3, 3);
  seqPre(0, 0) = 1;
  seqPre(1, 0) = 1;
  seqPre(2, 0) = 1;
  seqPre(0, 1) = 8.5;
  seqPre(1, 1) = 8.5;
  seqPre(2, 1) = 1;
  seqPre(0, 2) = 9.8;
  seqPre(1, 2) = 9.8;
  seqPre(2, 2) = 1;
  pta.seq_pre_point = seqPre;
  // >车轮距离
  pta.wheel_base_ = 4.57;
  // >路线点
  pta.waypoint_= {{-192.90,-198.90,-199.90},{-10.30,-12.30,-14.30},
    {-10.30,-12.30,-14.30},{-10.30,-12.30,-14.30},
    {-10.30,-12.30,-14.30},{-0.02,0.005,0.005}};
  
  pta.ind_current_front_ = 0;
  pta.curvityMax1 = 0.01;
  pta.kc1 = 1.5;
  pta.kc3 = 1.0;
  pta.steering_angle_current_ = 210;
  pta.heading_current_ = 1;

  pta.updateSteeringAngleDes();

  // <期望转角
  EXPECT_ROUND_EQ(pta.steering_angle_des_, 38);
}

// #前进
TEST_F(PathTrackingApplicationTest, updateSteeringAngleDes_NaN) {
  updateSteeringAngleDesSimulate();
  // >当前档位
  pta.gear_current_ = -2;
  // >当前车速
  pta.velocity_current_ = 10;
  // >预瞄位置曲率
  pta.preview_curvature_ = 0.02;
  // >横向误差
  pta.error_lateral_r_=NAN;
  // >预瞄点序列长度
  pta.prepoint_sequence_length_ = 3;
  // >预瞄点序列
  Eigen::MatrixXd seqPre(3, 3);
  seqPre(0, 0) = 1;
  seqPre(1, 0) = 1;
  seqPre(2, 0) = 1;
  seqPre(0, 1) = 8.5;
  seqPre(1, 1) = 8.5;
  seqPre(2, 1) = 1;
  seqPre(0, 2) = 9.8;
  seqPre(1, 2) = 9.8;
  seqPre(2, 2) = 1;
  pta.seq_pre_point = seqPre;
  // >车轮距离
  pta.wheel_base_ = 4.57;
  // >路线点
  pta.waypoint_= {{-192.90,-198.90,-199.90},{-10.30,-12.30,-14.30},
    {-10.30,-12.30,-14.30},{-10.30,-12.30,-14.30},
    {-10.30,-12.30,-14.30},{-0.005,0.005,0.005}};
  
  pta.ind_current_front_ = 0;
  pta.curvityMax1 = 0.01;
  pta.kc1 = 1.5;
  pta.kc3 = 1.0;
  pta.steering_angle_current_ = 210;

  pta.updateSteeringAngleDes();

  // <期望转角
  EXPECT_ROUND_EQ(pta.steering_angle_des_, 35.68);
}

// #倒车
TEST_F(PathTrackingApplicationTest, updateSteeringAngleDes_back) {
  // >当前档位
  pta.gear_current_ = -1;
  // >当前车速
  pta.velocity_current_ = 10;
  // >预瞄位置曲率
  pta.preview_curvature_ = 0.02;
  // >横向误差
  pta.error_lateral_r_=10;
  // >预瞄点序列长度
  pta.prepoint_sequence_length_ = 3;
  // >预瞄点序列
  Eigen::MatrixXd seqPre(3, 3);
  seqPre(0, 0) = 1;
  seqPre(1, 0) = 1;
  seqPre(2, 0) = 1;
  seqPre(0, 1) = 8.5;
  seqPre(1, 1) = 8.5;
  seqPre(2, 1) = 1;
  seqPre(0, 2) = 9.8;
  seqPre(1, 2) = 9.8;
  seqPre(2, 2) = 1;
  pta.seq_pre_point = seqPre;
  // >车轮距离
  pta.wheel_base_ = 4.57;
  // >路线点
  pta.waypoint_= {
    {1,2,3},
    {1,2,3},
    {18,15,12},
    {-10.30,-12.30,-14.30},
    {-10.30,-12.30,-14.30},
    {-10.30,-12.30,-14.30}
  };
  
  pta.ind_current_rear_ = 0;
  pta.heading_current_ = 0;
  pta.k_for_stanley_ = 0.77;
  pta.dis_pre_for_stanley_ = 2.0;

  pta.updateSteeringAngleDes();

  // <期望转角
  EXPECT_DOUBLE_EQ(pta.steering_angle_des_, 4);
}

// #倒车
TEST_F(PathTrackingApplicationTest, updateSteeringAngleDes_back_NAN) {
  // >当前档位
  pta.gear_current_ = -1;
  // >当前车速
  pta.velocity_current_ = 10;
  // >预瞄位置曲率
  pta.preview_curvature_ = 0.02;
  // >横向误差
  pta.error_lateral_r_=NAN;
  // >预瞄点序列长度
  pta.prepoint_sequence_length_ = 3;
  // >预瞄点序列
  Eigen::MatrixXd seqPre(3, 3);
  seqPre(0, 0) = 1;
  seqPre(1, 0) = 1;
  seqPre(2, 0) = 1;
  seqPre(0, 1) = 8.5;
  seqPre(1, 1) = 8.5;
  seqPre(2, 1) = 1;
  seqPre(0, 2) = 9.8;
  seqPre(1, 2) = 9.8;
  seqPre(2, 2) = 1;
  pta.seq_pre_point = seqPre;
  // >车轮距离
  pta.wheel_base_ = 4.57;
  // >路线点
  pta.waypoint_= {{-192.90,-198.90,-199.90},{-10.30,-12.30,-14.30},
    {-10.30,-12.30,-14.30},{-10.30,-12.30,-14.30},
    {-10.30,-12.30,-14.30},{-10.30,-12.30,-14.30}};
  
  pta.ind_current_rear_ = 0;
  pta.heading_current_ = 0;

  pta.updateSteeringAngleDes();

  // <期望转角
  EXPECT_DOUBLE_EQ(pta.steering_angle_des_, 20.6);
}

/******************************************************************************
 * @getObsDis
 * 获取障碍物距离
 *****************************************************************************/
// #获取障碍物距离
TEST_F(PathTrackingApplicationTest, getObsDis) {
  // >障碍物在自车坐标系下的坐标(5,5)
  double x = 5;
  double y = 5;
  double z = 90;
  // >障碍物长度
  int obs_width_ = 10;
  // >车辆当前位置
  pta.x_current_rear_ = 0;
  pta.y_current_rear_ = 0;
  // >航向角
  pta.heading_current_ = 0;
  // >当前位置索引
  pta.ind_current_rear_ = 0;
  // >路径点
  pta.waypoint_= {
    {1,2,3,4,5,6},
    {1,2,3,4,5,6},
  };

  double ret = pta.getObsDis(x, y, z, obs_width_);
  // <障碍物距离=5.66
  // TODO(#227)
  // EXPECT_EQ(round(ret, 2), 5.66); // 4* 1.414
}

/******************************************************************************
 * @updatePointRef
 * update the reference point depending on the preview distance
 *****************************************************************************/
// #弯道情况下找预瞄点
TEST_F(PathTrackingApplicationTest, updatePointRef) {
  // >当前车速
  pta.velocity_current_ = 10;
  // >预瞄位置曲率
  pta.preview_curvature_ = 0.02;
  // >误差
  pta.error_lateral_r_=10;
  // >预瞄点序列长度
  pta.prepoint_sequence_length_ = 3;
  // pta.dispre_min = 5;
  pta.dispre_max = 18;
  // pta.ks = 0.35;
  // >预瞄点序列
  Eigen::MatrixXd seqPre(3, 3);
  seqPre(0, 0) = 1;
  seqPre(1, 0) = 1;
  seqPre(2, 0) = 1;
  seqPre(0, 1) = 6;
  seqPre(1, 1) = 6;
  seqPre(2, 1) = 1;
  seqPre(0, 2) = 9.8;
  seqPre(1, 2) = 9.8;
  seqPre(2, 2) = 1;
  pta.seq_pre_point = seqPre;
  pta.dispre_max = 18;
  pta.dispre_min_straight_ = 9;
  pta.ks_straight_ = 0.5;
  pta.dispre_min_curve_ = 5;
  pta.ks_curve_ = 0.35;


  // disPre: 8.5, 以该距离找寻最近点
  Eigen::Vector2d pointRef = pta.updatePointRef();

  // <Reference Point
  // TODO
  // EXPECT_EQ(pta.pre_index_, 1);
  // EXPECT_EQ(pointRef(0), 6);
  // EXPECT_EQ(pointRef(1), 6);
}

// #updatePointRef
TEST_F(PathTrackingApplicationTest, updatePointRef_error_lateral_r_big) {
  // >当前车速
  pta.velocity_current_ = 10;
  // >预瞄位置曲率
  pta.preview_curvature_ = 0.02;
  // >横向偏差大
  pta.error_lateral_r_=20;
  // >预瞄点序列长度
  pta.prepoint_sequence_length_ = 3;
  // >预瞄点序列
  Eigen::MatrixXd seqPre(3, 3);
  seqPre(0, 0) = 1;
  seqPre(1, 0) = 1;
  seqPre(2, 0) = 1;
  seqPre(0, 1) = 8.5;
  seqPre(1, 1) = 8.5;
  seqPre(2, 1) = 1;
  seqPre(0, 2) = 9.8;
  seqPre(1, 2) = 9.8;
  seqPre(2, 2) = 1;
  pta.seq_pre_point = seqPre;

  Eigen::Vector2d pointRef = pta.updatePointRef();

  // <Reference Point
  EXPECT_EQ(pta.pre_index_, 10);
  EXPECT_EQ(pointRef(0), 0);
  EXPECT_EQ(pointRef(1), 1);
}

// #updatePointRef
TEST_F(PathTrackingApplicationTest, updatePointRef_prepoint_sequence_length_0) {
  // >当前车速
  pta.velocity_current_ = 10;
  // >预瞄位置曲率
  pta.preview_curvature_ = 0.02;
  // >误差
  pta.error_lateral_r_=10;
  // >预瞄点序列长度
  pta.prepoint_sequence_length_ = 0;
  // >预瞄点序列
  Eigen::MatrixXd seqPre(3, 1);
  seqPre(0, 0) = 1;
  seqPre(1, 0) = 1;
  seqPre(2, 0) = 1;
  // seqPre(0, 1) = 8.5;
  // seqPre(1, 1) = 8.5;
  // seqPre(2, 1) = 1;
  // seqPre(0, 2) = 9.8;
  // seqPre(1, 2) = 9.8;
  // seqPre(2, 2) = 1;
  pta.seq_pre_point = seqPre;

  Eigen::Vector2d pointRef = pta.updatePointRef();

  // <Reference Point
  EXPECT_EQ(pointRef(0), 1);
  EXPECT_EQ(pointRef(1), 1);
}

/******************************************************************************
 * @updateErrorLateral
 * update the lateral error in Stanley model
 *****************************************************************************/
// #updateErrorLateral
TEST_F(PathTrackingApplicationTest, updateErrorLateral) {
  int ind_current_rear = 0;
  double x_current_rear = 1;
  double y_current_rear = 1;

  // >路线点
  pta.waypoint_= {
    {1,2,3},
    {3,2,1}
  };
  // >预瞄点序列
  Eigen::MatrixXd seqPre(3, 3);
  seqPre(0, 0) = 1;
  pta.seq_pre_point = seqPre;

  double ret = pta.updateErrorLateral(ind_current_rear, x_current_rear, y_current_rear);

  // <ErrorLateral
  EXPECT_DOUBLE_EQ(ret, 1.4142135623730949);
}

// #updateErrorLateral minus
TEST_F(PathTrackingApplicationTest, updateErrorLateral_minus) {
  int ind_current_rear = 0;
  double x_current_rear = 1;
  double y_current_rear = 1;

  // >路线点
  pta.waypoint_= {
    {1,2,3},  //x
    {3,2,1}   //y
  };
  // >预瞄点序列
  Eigen::MatrixXd seqPre(3, 3);
  seqPre(0, 0) = 0;
  pta.seq_pre_point = seqPre;

  double ret = pta.updateErrorLateral(ind_current_rear, x_current_rear, y_current_rear);

  // <ErrorLateral
  EXPECT_DOUBLE_EQ(ret, -1.4142135623730949);
}

// #updateErrorLateral indCurr_bigger
TEST_F(PathTrackingApplicationTest, updateErrorLateral_indCurr_bigger) {
  int ind_current_rear = 3;
  double x_current_rear = 1;
  double y_current_rear = 1;

  // >路线点
  pta.waypoint_= {
    {1,2,3,4},
    {4,3,2,1}
  };
  // >预瞄点序列
  Eigen::MatrixXd seqPre(3, 3);
  seqPre(0, 0) = 1;
  pta.seq_pre_point = seqPre;

  double ret = pta.updateErrorLateral(ind_current_rear, x_current_rear, y_current_rear);

  // <ErrorLateral
  EXPECT_DOUBLE_EQ(ret, 2.1213203435596424);
}


/******************************************************************************
 * @updateErrorHeading
 * update the heading error in Stanley model
 *****************************************************************************/
// #updateErrorHeading
TEST_F(PathTrackingApplicationTest, updateErrorHeading) {
  // >路线点
  pta.waypoint_= waypoints;

  int indCur = 0;
  pta.heading_current_ = 10;

  pta.updateErrorHeading(indCur);

  // <error_heading
  EXPECT_DOUBLE_EQ(pta.error_heading_, -181.40731176082323);
}

// #updateErrorHeading big than PI
TEST_F(PathTrackingApplicationTest, updateErrorHeading_big_than_PI) {
  // >路线点
  pta.waypoint_= waypoints;

  pta.waypoint_[2][0] = 300;

  int indCur = 0;
  pta.heading_current_ = 0;

  pta.updateErrorHeading(indCur);

  // <error_heading
  EXPECT_DOUBLE_EQ(pta.error_heading_, -59.999999999999986);
}

// #updateErrorHeading small than -PI
TEST_F(PathTrackingApplicationTest, updateErrorHeading_small_than_minus_PI) {
  // >路线点
  pta.waypoint_= waypoints;

  pta.waypoint_[2][0] = 10;

  int indCur = 0;
  pta.heading_current_ = 10;

  pta.updateErrorHeading(indCur);

  // <error_heading
  EXPECT_DOUBLE_EQ(pta.error_heading_, -202.95779513082323);
}

/******************************************************************************
 * @updateIndCurrent
 * find current position of the vehicle
 *****************************************************************************/
// #updateIndCurrent
TEST_F(PathTrackingApplicationTest, updateIndCurrent) {
  
  int indCur = 1;
  double xCur = 4.2;
  double yCur = 2.5;
  bool routeIsNew = false;
  bool isRear = true;
  pta.waypoint_= {
    {3.9005881807,4.0054939754,4.1103997676,4.2153055623,4.3202113594,4.4251171516},
    {2.3039161935,2.3693305668,2.4358536629,2.5034854724,2.5711172861,2.6387490993},
    {31.55048337,31.78801368,32.04309483,32.31432073,32.60034841,32.89989805},
    {7.526479563,7.525849731,7.525249959,7.524678656,7.524134837,7.523616692},
    {1,1,1,1,1,1},
    {-0.0535,-0.0533,-0.0529,-0.0526,-0.0523,-0.052}
  };
  pta.prepoint_sequence_maximum_length_ = 150;


  pta.updateIndCurrent(indCur, xCur, yCur, routeIsNew, isRear); 

  // <indCur
  EXPECT_FLOAT_EQ(indCur, 3);
  EXPECT_FLOAT_EQ(pta.prepoint_sequence_length_, 5);
}

// #updateIndCurrent routeIsNew
TEST_F(PathTrackingApplicationTest, updateIndCurrent_routeIsNew) {
  
  int indCur = 1;
  double xCur = 4.2;
  double yCur = 2.5;
  bool routeIsNew = true;
  bool isRear = true;
  pta.waypoint_= {
    {3.9005881807,4.0054939754,4.1103997676,4.2153055623,4.3202113594,4.4251171516},
    {2.3039161935,2.3693305668,2.4358536629,2.5034854724,2.5711172861,2.6387490993},
    {31.55048337,31.78801368,32.04309483,32.31432073,32.60034841,32.89989805},
    {7.526479563,7.525849731,7.525249959,7.524678656,7.524134837,7.523616692},
    {1,1,1,1,1,1},
    {-0.0535,-0.0533,-0.0529,-0.0526,-0.0523,-0.052}
  };
  pta.prepoint_sequence_maximum_length_ = 150;


  pta.updateIndCurrent(indCur, xCur, yCur, routeIsNew, isRear); 

  // <indCur
  EXPECT_FLOAT_EQ(indCur, 3);
  EXPECT_FLOAT_EQ(pta.prepoint_sequence_length_, 6);
}

// #updateIndCurrent bigger
TEST_F(PathTrackingApplicationTest, updateIndCurrent_current_index_bigger) {
  
  int indCur = 4;
  double xCur = -190.90;
  double yCur = -8.30;
  bool routeIsNew = false;
  bool isRear = true;
  pta.waypoint_= {{-192.90,-198.90,-199.90},{-10.30,-12.30,-14.30},
    {-10.30,-12.30,-14.30},{-10.30,-12.30,-14.30},
    {-10.30,-12.30,-14.30},{-10.30,-12.30,-14.30}};
  pta.prepoint_sequence_maximum_length_ = 150;

  pta.updateIndCurrent(indCur, xCur, yCur, routeIsNew, isRear); 

  // <indCur
  EXPECT_FLOAT_EQ(indCur, 3);
}

/******************************************************************************
 * @GNSSToGlobal
 * 将经纬度转化为系以（B0.L0）为圆心的x,y坐标
 *****************************************************************************/
// #GNSSToGlobal
TEST_F(PathTrackingApplicationTest, GNSSToGlobal) {
  
  pta.B0_ = 31.13554949;  //data_record/uA_110_gps.csv line 1 
  pta.L0_ = 118.1772826;
  pta.latitude_current_ = 31.13555006; //data_record/uA_110_gps.csv line 5
  pta.longitude_current_ = 118.1772837;

  pta.GNSSToGlobal(); 

  // <输出x,y坐标 参照data_record/uA_110_xy.csv line 5
  EXPECT_FLOAT_EQ(pta.x_current_rear_, 0.10490579); 
  EXPECT_FLOAT_EQ(pta.y_current_rear_, 0.063196927);
}

/******************************************************************************
 * @GNSSToGlobal2
 * 将经纬度转化为系以（B0.L0）为圆心的x,y坐标
 *****************************************************************************/
// #GNSSToGlobal2
TEST_F(PathTrackingApplicationTest, GNSSToGlobal2) {
  
  double B0 = 31.1367846;
  double L0 = 118.1789369;
  double latCurrent = 32.1367847;
  double lonCurrent = 119.1789369;

  pta.GNSSToGlobal2(B0, L0, latCurrent, lonCurrent); 

  // <输出x,y坐标
  EXPECT_FLOAT_EQ(pta.x_h_, 95367.672);
  EXPECT_FLOAT_EQ(pta.y_h_, 111472);
}


/******************************************************************************
 * @locatCorrection
 * transform earch coord to Cartisian coord with initial Lat and Lon at starting point
 *****************************************************************************/
// #locatCorrection
TEST_F(PathTrackingApplicationTest, locatCorrection) {
  
  pta.velocity_current_ = 10;
  pta.time_delay_ = 0.7;
  pta.heading_current_ = 1;
  pta.steering_angle_current_ = 50;
  pta.wheel_base_ = 4.57;
  pta.x_current_rear_ = -190.90;
  pta.y_current_rear_ = -8.30;

  pta.locatCorrection();
  // <heading_current
  EXPECT_DOUBLE_EQ(pta.heading_current_, 1);
}

/******************************************************************************
 * @globalToFrenet
 * trans global coordinate to vehicle coordinate
 *****************************************************************************/
// #globalToFrenet
TEST_F(PathTrackingApplicationTest, globalToFrenet) {
  
  int sizePre = 3;
  pta.x_current_rear_ = 2;
  pta.y_current_rear_ = 2;
  pta.ind_current_rear_ = 0;
  pta.heading_current_ = M_PI / 4;
  pta.waypoint_= {
    {2,4,-2}, //x
    {2,4,2},  //y
  };

  Eigen::MatrixXd ret = pta.globalToFrenet(sizePre);

  // <seq_pre_point
  EXPECT_DOUBLE_EQ(round(ret(0, 0), 2), 0);
  EXPECT_DOUBLE_EQ(round(ret(1, 0), 2), 0);
  EXPECT_DOUBLE_EQ(round(ret(0, 1), 2), 0);
  EXPECT_DOUBLE_EQ(round(ret(1, 1), 2), 2.83);
  EXPECT_DOUBLE_EQ(round(ret(0, 2), 2), -2.83);
  EXPECT_DOUBLE_EQ(round(ret(1, 2), 2), -2.83);
}

// #globalToFrenet sizePre=0
TEST_F(PathTrackingApplicationTest, globalToFrenet_sizePre_0) {
  
  int sizePre = 0;
  pta.x_current_rear_ = 2;
  pta.y_current_rear_ = 2;
  pta.ind_current_rear_ = 0;
  pta.heading_current_ = M_PI / 4;
  pta.waypoint_= {
    {4}, //x
    {4}, //y
  };

  Eigen::MatrixXd ret = pta.globalToFrenet(sizePre);

  // <seq_pre_point
  EXPECT_DOUBLE_EQ(round(ret(0, 0), 2), 0);
  EXPECT_DOUBLE_EQ(round(ret(1, 0), 2), 2.83);
}

// #globalToFrenet 超出索引判断
TEST_F(PathTrackingApplicationTest, globalToFrenet_over_index) {
  
  int sizePre = 2;
  pta.x_current_rear_ = 2;
  pta.y_current_rear_ = 2;
  pta.ind_current_rear_ = 0;
  pta.heading_current_ = M_PI / 4;
  pta.waypoint_= {
    {4}, //x
    {4}, //y
  };
  // TODO: waypoint_[0][ind_current_rear_ + i] over size???
  Eigen::MatrixXd ret = pta.globalToFrenet(sizePre);

  // <seq_pre_point
  EXPECT_DOUBLE_EQ(round(ret(0, 0), 2), 0);
  EXPECT_DOUBLE_EQ(round(ret(1, 0), 2), 2.83);
}
/******************************************************************************
 * @findOrigin
 * give T matrix transforming from global to huace
 * 全局坐标原点在自车坐标系下的坐标
 *****************************************************************************/
// #findOrigin
TEST_F(PathTrackingApplicationTest, findOrigin) {
  
  double xCur = 2;
  double yCur = 2;
  double headingCur = M_PI / 6; //30d
  
  Eigen::Vector2d ret = pta.findOrigin(xCur, yCur, headingCur);

  // <seq_pre_point
  EXPECT_EQ(round(ret(0), 2), -0.73);
  EXPECT_EQ(round(ret(1), 2), -2.73);
}

// #findOrigin
TEST_F(PathTrackingApplicationTest, findOrigin_x_plus_y_minus) {
  
  double xCur = 2;
  double yCur = -2;
  double headingCur = M_PI / 6;
  
  Eigen::Vector2d ret = pta.findOrigin(xCur, yCur, headingCur);

  // <seq_pre_point
  EXPECT_EQ(round(ret(0), 2), -2.73);
  EXPECT_EQ(round(ret(1), 2), 0.73);
}

// #findOrigin
TEST_F(PathTrackingApplicationTest, findOrigin_x_minus_y_minus) {
  
  double xCur = -2;
  double yCur = -2;
  double headingCur = M_PI / 6;
  
  Eigen::Vector2d ret = pta.findOrigin(xCur, yCur, headingCur);

  // <seq_pre_point
  EXPECT_EQ(round(ret(0), 2), 0.73);
  EXPECT_EQ(round(ret(1), 2), 2.73);
}

// #findOrigin
TEST_F(PathTrackingApplicationTest, findOrigin_x_minus_y_plus) {
  
  double xCur = -2;
  double yCur = 2;
  double headingCur = M_PI / 6;
  
  Eigen::Vector2d ret = pta.findOrigin(xCur, yCur, headingCur);

  // <seq_pre_point
  EXPECT_EQ(round(ret(0), 2), 2.73);
  EXPECT_EQ(round(ret(1), 2), -0.73);
}

// #findOrigin xy is 0
TEST_F(PathTrackingApplicationTest, findOrigin_xy_0) {
  
  double xCur = 0;
  double yCur = 0;
  double headingCur = M_PI / 6;
  
  Eigen::Vector2d ret = pta.findOrigin(xCur, yCur, headingCur);

  // <seq_pre_point
  EXPECT_EQ(round(ret(0), 2), 0);
  EXPECT_EQ(round(ret(1), 2), 0);
}

/******************************************************************************
 * @getErrorYaw
 * getErrorYaw
 *****************************************************************************/
// #getErrorYaw
TEST_F(PathTrackingApplicationTest, getErrorYaw) {
  // >路径点
  pta.waypoint_temp_ = {
    {3.9005881807,4.0054939754,4.1103997676,4.2153055623,4.3202113594,4.4251171516},
    {2.3039161935,2.3693305668,2.4358536629,2.5034854724,2.5711172861,2.6387490993},
    {31.55048337,31.78801368,32.04309483,32.31432073,32.60034841,32.89989805},
    {7.526479563,7.525849731,7.525249959,7.524678656,7.524134837,7.523616692},
    {1,1,1,1,1,1},
    {-0.0535,-0.0533,-0.0529,-0.0526,-0.0523,-0.052}
  };
  pta.ind_current_rear_ = 0;
  pta.imu_heading_ = 2;
  
  float ret = pta.getErrorYaw();

  // <error_yaw_
  EXPECT_FLOAT_EQ(ret, 5.526479563);
}

/******************************************************************************
 * @GetHybirdState
 * GetHybirdState
 *****************************************************************************/
// #GetHybirdState
TEST_F(PathTrackingApplicationTest, GetHybirdState) {
  // >路径点
  pta.parking_control_ = HYBIRDASTAR_CONTROL;
  pta.wayPoint_backoff = {
    {3,4},
    {2,2},
    {2,2},
    {0,0}
  };
  pta.x_current_rear_ = 2;
  pta.y_current_rear_ = 2;
  pta.dc_command_ = 4;

  pta.GetHybirdState();

  // <error_yaw_
  EXPECT_FLOAT_EQ(pta.enum_avp_state_, PARKING_IN);
}

// /******************************************************************************
//  * @ParkingEnd
//  * ParkingEnd
//  *****************************************************************************/
// // #ParkingEnd
// TEST_F(PathTrackingApplicationTest, ParkingEnd) {
  
//   double xCur = -190.90;
//   double yCur = -8.30;
//   double headingCur = 1;
  
//   pta.ParkingEnd();

//   // <seq_pre_point
//   // EXPECT_DOUBLE_EQ(ret(0), 96.159501016322309);
//   // EXPECT_DOUBLE_EQ(ret(1), 165.12132013853304);
// }

}  // namespace planning
}  // namespace conch