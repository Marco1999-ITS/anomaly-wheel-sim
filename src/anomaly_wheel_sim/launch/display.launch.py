from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share = get_package_share_directory('anomaly_wheel_sim')
    urdf_file = os.path.join(pkg_share, 'urdf', 'wheel.urdf')
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'wheel_view.rviz') 

    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        Node(
            package='anomaly_wheel_sim',
            executable='serial_bridge',
            name='serial_bridge',
            output='screen' 
        ),
        Node(
            package='anomaly_wheel_sim',
            executable='sim_controller',
            name='sim_controller',
            output='screen' 
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}]
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file] 
        )
    ])