"""Gazebo Fortress + pan-tilt URDF + ros2_control + мост pan_tilt_deg → суставы.

Запуск:
  source /opt/ros/humble/setup.bash
  source install/setup.bash
  ros2 launch autotargeting_gazebo pan_tilt_sim.launch.py

Тест углов (градусы 0…180, как у Arduino):
  ros2 topic pub /pan_tilt_deg geometry_msgs/msg/Point "{x: 45.0, y: 135.0, z: 0.0}" --once
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    gz_args = LaunchConfiguration('gz_args', default='')

    pkg_share = FindPackageShare('autotargeting_gazebo')
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name='xacro')]),
            ' ',
            PathJoinSubstitution([pkg_share, 'urdf', 'pan_tilt.xacro.urdf']),
        ]
    )
    robot_description = {
        'robot_description': ParameterValue(robot_description_content, value_type=str)
    }
    controllers_file = PathJoinSubstitution([pkg_share, 'config', 'pan_tilt_controllers.yaml'])

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            robot_description,
            {'use_sim_time': ParameterValue(use_sim_time, value_type=bool)},
        ],
    )

    gz_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description', '-name', 'pan_tilt', '-allow_renaming', 'true'],
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        output='screen',
        arguments=['joint_state_broadcaster'],
    )

    joint_group_position_spawner = Node(
        package='controller_manager',
        executable='spawner',
        output='screen',
        arguments=[
            'joint_group_position_controller',
            '--param-file',
            controllers_file,
        ],
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
    )

    pan_tilt_bridge = Node(
        package='autotargeting_gazebo',
        executable='pan_tilt_bridge_node',
        name='pan_tilt_sim_bridge',
        output='screen',
        parameters=[{'use_sim_time': ParameterValue(use_sim_time, value_type=bool)}],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'use_sim_time',
                default_value='true',
                description='Использовать /clock от симулятора',
            ),
            DeclareLaunchArgument(
                'gz_args',
                default_value='',
                description='Доп. аргументы для gz sim (после мира empty.sdf)',
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        PathJoinSubstitution(
                            [FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py']
                        )
                    ]
                ),
                launch_arguments=[('gz_args', [gz_args, ' -r -v 1 empty.sdf'])],
            ),
            clock_bridge,
            node_robot_state_publisher,
            gz_spawn_entity,
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=gz_spawn_entity,
                    on_exit=[joint_state_broadcaster_spawner],
                )
            ),
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=joint_state_broadcaster_spawner,
                    on_exit=[joint_group_position_spawner],
                )
            ),
            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=joint_group_position_spawner,
                    on_exit=[pan_tilt_bridge],
                )
            ),
        ]
    )
