from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution
import os, yaml

def generate_launch_description():
    def convert_to_str(value):
        if isinstance(value, bool):
            return 'True' if value else 'False'
        return str(value)

    config_path = os.path.join(os.path.dirname(__file__), 'launch_arguments.yaml')

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        
    launch_args = []

    if config: 
        for section, parameters in config.items():
            for key, value in parameters.items():
                launch_args.append(DeclareLaunchArgument(
                    f"{section}__{key}",
                    default_value=convert_to_str(value)
                ))

    backend_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ssgui'),
                'launch',
                'gui.launch.py'
            ])
        ])
    )

    return LaunchDescription(
        launch_args + [
        backend_launch
    ])