#!/usr/bin/env python3
import rospy
from std_srvs.srv import SetBool

revs = 100
pulses_per_rev = 400
iter = pulses_per_rev*revs
stay_time = 0.00005

def main():
    rospy.init_node("time_tests")
    rospy.wait_for_service("/io_module/pulse_stepper")
    toggle_service = rospy.ServiceProxy("/io_module/pulse_stepper", SetBool)
    for i in range(iter):
        toggle_service(True)
        # rospy.logwarn("toggle_true")
        rospy.sleep(stay_time)
        toggle_service(False)
        rospy.logwarn(iter-i)


if __name__ == '__main__':
    main()