from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_pub',
        arguments=[
            '-0.375', '0', '0.257953',         # translation x y z
            # '0.7101854', '0.0', '-0.7041470', '0.0',  # rotation qx qy qz qw
            '0.7070895', '0.004936496', '-0.7070895', '0.004936496',  # rotation qx qy qz qw
            'tool0',                     # parent frame
            'tcp_hack'                 # child frame
        ]
    )

    return LaunchDescription([
        static_tf
    ])