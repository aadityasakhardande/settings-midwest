#!/usr/bin/env python3
### Dependancies ###
import rospy
import subprocess
import rospkg
import numpy as np
import actionlib
import math
import time 
import yaml 
from datetime import datetime

# gmr functions 
from gmr_motion_msgs.msg import SingleRobotMotionAction, SingleRobotMotionGoal
from gmr_motion_msgs.msg import ContRobotMotionGoal, ContRobotMotionAction
from profile_msgs.msg import UnitRobotTraj
from profile_msgs.msg import RobotPose 


### Input block ###
velocity = 0.5
force = 0.0
tool_status = False
use_time = True
time = 1.0
CNT = 50
RPM = 0 
move_type = 0 # 0 = joint and 1 = linear motion 

#### SAE access end ###



### Functions setup and client  ###
def client(goal, type):
    # here type just toggles between type of motion if you wanna move the extender type = 0, if you wanna move the joint, type =1 
    if type == 0: 
        client = actionlib.SimpleActionClient('/motion_intf/single_ext_motion', SingleRobotMotionAction)
    else:
        client = actionlib.SimpleActionClient('/motion_intf/single_joint_motion', SingleRobotMotionAction)
    
    client.wait_for_server()
    motion_goal = SingleRobotMotionGoal(goal.target, goal.move_type) 
    client.send_goal(motion_goal)
    client.wait_for_result()
    client.get_result()


# traj is joint array in degrees
# ext_s is array of [1.0, 1.0, 1.0]
# type is motion type 1(joint) or 0(extender) 

def convert_to_rt(traj, ext_s, type): 
    if traj != []: 
        robot_traj = traj #[-0.715253381, 0.73722708, -0.332729569, 2.213845436, 1.871027865, -2.491614587] 
        robot_traj = [i * (math.pi/180) for i in robot_traj]  #angles are converted to degrees not needed for me
    else:
        robot_traj = [] 
    
    # creates a input with robot_traj, ext_s and also has roller position 
    pose = RobotPose()
    pose.joint_state = robot_traj
    pose.ext_state = ext_s

    # using defined structure of unitRobotTraj 
    rt = UnitRobotTraj()
    rt.pose = pose
    rt.velocity = velocity
    rt.force = force
    rt.tool_status = tool_status
    rt.use_time = use_time
    rt.time = time
    rt.CNT = CNT
    rt.RPM = RPM

    # send robot goal
    goal = SingleRobotMotionGoal()
    goal.target = rt
    goal.move_type = move_type 

    client(goal, type)



def call_ros_service(service_name):
    try:
        # Call the rosservice using subprocess to run the command
        service_call = subprocess.run(
            ["rosservice", "call", service_name, "{}"], 
            capture_output=True, text=True
        )
        
        # Check if the service call succeeded
        if "success: True" in service_call.stdout:
            print(f"Service {service_name} succeeded!")
            return True
        else:
            print(f"Service {service_name} failed! Response: {service_call.stdout}")
            return False
        
    except Exception as e:
        print(f"Failed to call service {service_name}: {e}")
        return False

# input the orientation
def orientation_input():
    while True:
        user_input = input("Please enter 0 for positive orientation and 1 for negative orientation of the robot - \n")
        if user_input in ['0', '1']:
            return int(user_input)
        else:
            print("Invalid orientation input. Please try again.")
            return

def board_setup_input():
    while True:
        user_input = input("Please enter 'True' for setting the board and 'False' for doing the calibration - \n")
        if user_input == 'True':
            return True
        elif user_input == 'False':
            return False
        else:
            print("Invalid setup input. Please try again.")
      

def main():
    rospy.init_node("calibration_node")
    orientation = orientation_input()
    posearray = []


    ### poses for camera  
    
    posearray_positive = [
        #home
        [88.427, 29.013, 1.695, -2.096, -62.304, -90.149],
        #set 1
        [117.234, 14.186, -37.127, 82.989, -58.59, -204.936],
        [113.765, 6.931, -43.446, 89.597, -48.562, -206.4],
        [108.587, 0.076, -49.501, 100.499, -37.395, -211.079],
        [97.332, -6.788, -54.724, 130.624, -19.634, -230.997],
        [75.672, -4.19, -54.301, 240.59, -28.736, -323.382],
        [64.433, 6.601, -47.478, 260.796, -49.527, -331.296],
        
        # close the robot 
        [65.931, 32.466, -7.514, -54.781, -72.43, -18.409],
        [71.086, 20.538, -16.594, -48.76, -55.922, -26.772],
        [85.929, 8.118, -25.889, -16.49, -31.909, -65.422],
        [110.981, 17.092, -23.674, 57.797, -50.595, -151.275],
        [115.988, 25.817, -18.863, 63.916, -63.578, -160.876],
        
        
        # mid 2 
        [71.365, 52.962, 21.989, -38.781, -91.656, -56.293],
        [74.371, 48.514, 19.793, -32.168, -86.939, -59.832],
        [81.66, 41.464, 15.703, -17.628, -78.792, -69.238],
        [99.078, 36.73, 9.327, 16.855, -71.974, -96.186],
        [104.96, 38.431, 7.912, 29.058, -73.639, -106.382],
        [108.931, 40.827, 7.222, 37.548, -76.203, -113.511],

        #last 
        [107.818, 59.539, 29.623, 35.176, -97.109, -101.304],
        [101.827, 58.035, 33.735, 22.689, -97.041, -95.791],
        [97.165, 57.66, 36.065, 13.584, -97.47, -92.269],
        [81.052, 59.8, 38.197, -17.176, -99.843, -82.336],
        [74.151, 62.378, 35.856, -31.366, -101.145, -77.726],
        [71.449, 63.835, 34.268, -37.435, -101.863, -75.569]
     ]
  
    posearray_negative = [
        #home
        [-91.573, 29.013, 1.695, -2.096, -62.304, -90.149],
        #set 1
        [-62.766, 14.186, -37.127, 82.989, -58.59, -204.936],
        [-66.235, 6.931, -43.446, 89.597, -48.562, -206.4],
        [-71.413, 0.076, -49.501, 100.499, -37.395, -211.079],
        [-82.668, -6.788, -54.724, 130.624, -19.634, -230.997],
        [-104.328, -4.19, -54.301, 240.59, -28.736, -323.382],
        [-115.567, 6.601, -47.478, 260.796, -49.527, -331.296],
        
        # close the robot 
        [-114.069, 32.466, -7.514, -54.781, -72.43, -18.409],
        [-108.914, 20.538, -16.594, -48.76, -55.922, -26.772],
        [-94.071, 8.118, -25.889, -16.49, -31.909, -65.422],
        [-69.019, 17.092, -23.674, 57.797, -50.595, -151.275],
        [-64.012, 25.817, -18.863, 63.916, -63.578, -160.876],
        # [-76.707, 10.164, -26.738, 43.053, -37.269, -132.344], outlier
        
        # mid 2 
        [-108.635, 52.962, 21.989, -38.781, -91.656, -56.293],
        [-105.629, 48.514, 19.793, -32.168, -86.939, -59.832],
        [-98.34, 41.464, 15.703, -17.628, -78.792, -69.238],
        [-80.922, 36.73, 9.327, 16.855, -71.974, -96.186],
        [-75.04, 38.431, 7.912, 29.058, -73.639, -106.382],
        [-71.069, 40.827, 7.222, 37.548, -76.203, -113.511],

        #last 
        [-72.182, 59.539, 29.623, 35.176, -97.109, -101.304],
        [-78.173, 58.035, 33.735, 22.689, -97.041, -95.791],
        [-82.835, 57.66, 36.065, 13.584, -97.47, -92.269],
        [-98.948, 59.8, 38.197, -17.176, -99.843, -82.336],
        [-105.849, 62.378, 35.856, -31.366, -101.145, -77.726],
        [-108.551, 63.835, 34.268, -37.435, -101.863, -75.569]
        ]

 
    if orientation == 1:
        posearray = posearray_negative

    elif orientation == 0:
        posearray = posearray_positive
    
    else: 
        print("Invalid orientation input. Please try again.")
        return

    # setup the board 
    board_setup = board_setup_input() 


    # create a log file 
    # Get the current time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S") 
    # Define the file name
    file_name = f"alvium_calibration_run_{current_time}.txt"

    # Write data to the file
    with open(file_name, 'w') as file:
        file.write(f"Board setup : {board_setup}\n")
        file.write(f"Orientation : {posearray}\n")


    ### Setup the board -
    if board_setup == True: 
        print("Starting alvium calibration data collection\n")
        # print(posearray)
        # move to first angle and stop 
        #extender
        print("Moving extender to calibration position at 1000mm")
        convert_to_rt(posearray[0], [1.0, 0.0, 0.0], 0)
        print("Robot moved to 1000mm")
        # joint
        print("Moving robot to calibration home")
        convert_to_rt(posearray[0], [1.0, 0.0, 0.0], 1) 
        print("Robot is at board setup home pose, please close SS, adjust and setup checkboard as per instructions.")
        return

    ### Run calibration
    else :  
        print("Starting alvium calibration data collection . . . \n")
        # print(posearray)
        # Step 1: Reset calibration data counter before the loop
        print("Resetting calibration data counter...")
        if not call_ros_service("/rgb_camera/reset_calib_data_counter"):
            print("Failed to reset calibration data counter. Exiting.")
            return

        # Step 2: Loop through the poses and perform actions
        for i in range(len(posearray)):
            # Step 3: Move extender to calibration position (1.0m) on the first iteration
            print(f"\nMoving to pose {i+1}:")
            if i == 0:
                print("Moving extender to calibration position at 1000mm")
                convert_to_rt(posearray[i], [1.0, 0.0, 0.0], 0)
                # time.sleep(10)
                print(f"motion complete{i}")
                convert_to_rt(posearray[i], [1.0, 0.0, 0.0], 1) 
                print(f"motion complete{i} joint")
                
            else:
                print(f"Moving robot to pose {i+1}")
                convert_to_rt(posearray[i], [0.0, 0.0, 0.0], 1)
            
            # Step 4: Capture the calibration frame and wait for success
            print("Capturing calibration frame...")
            if not call_ros_service("/rgb_camera/capture_calib_frame"):
                print("Failed to capture calibration frame. Exiting.")
                return

            print(f"Pose {i+1} complete.\n")

        print("All poses completed successfully! Please go forward with further steps")

        ## add service that will look for calibration file. 

    
if __name__ == "__main__":
    main()