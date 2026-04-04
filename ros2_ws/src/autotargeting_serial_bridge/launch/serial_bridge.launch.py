"""Запуск serial_bridge_node с параметрами по умолчанию.

**Launch-файл** в ROS2 — это сценарий: какие узлы поднять и с какими параметрами.
Аналог — один «main», который стартует несколько сервисов с конфигом.

Переопределение порта (часто на Orange Pi вместо ttyUSB0 бывает ttyACM0):
  ros2 launch autotargeting_serial_bridge serial_bridge.launch.py \\
    serial_port:=/dev/ttyACM0

Перед запуском на роботе: `source /opt/ros/humble/setup.bash` и
`source ~/ros2_ws/install/setup.bash` (путь к workspace подставьте свой).
"""

from launch import LaunchDescription
# Аргументы командной строки launch передаются в узел как parameters (см. ниже).
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
# Строковые значения из launch нужно привести к int/bool — иначе ROS2 получит строку.
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'serial_port',
                default_value='/dev/ttyUSB0',
                description='Устройство UART Arduino (ls -l /dev/ttyUSB* /dev/ttyACM*)',
            ),
            DeclareLaunchArgument('baud_rate', default_value='9600', description='Скорость UART'),
            DeclareLaunchArgument(
                'demo_mode',
                default_value='false',
                description='Если true — узел сам шлёт тестовые углы (без топика)',
            ),
            Node(
                # package — имя ROS2-пакета (папка под ros2_ws/src с package.xml).
                package='autotargeting_serial_bridge',
                # executable — имя из entry_points console_scripts в setup.py.
                executable='serial_bridge_node',
                name='serial_bridge_node',
                output='screen',
                parameters=[
                    {
                        'serial_port': LaunchConfiguration('serial_port'),
                        'baud_rate': ParameterValue(
                            LaunchConfiguration('baud_rate'), value_type=int
                        ),
                        'demo_mode': ParameterValue(
                            LaunchConfiguration('demo_mode'), value_type=bool
                        ),
                    }
                ],
            ),
        ]
    )
