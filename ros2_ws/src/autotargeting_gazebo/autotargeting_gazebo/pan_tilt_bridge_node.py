"""Мост pan_tilt_deg (градусы) → joint_group_position_controller/commands (радианы).

Тот же вход, что у serial_bridge_node (geometry_msgs/msg/Point: x=PAN°, y=TILT°),
чтобы в симуляции проверять ту же «контрактную» цепочку без Arduino.
"""

import math
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Point
from std_msgs.msg import Float64MultiArray


def _clamp_deg(value: float) -> float:
    return float(max(0.0, min(180.0, value)))


class PanTiltBridgeNode(Node):
    def __init__(self) -> None:
        super().__init__('pan_tilt_sim_bridge')
        self.declare_parameter('controller_name', 'joint_group_position_controller')
        ctrl = self.get_parameter('controller_name').get_parameter_value().string_value
        topic = f'{ctrl}/commands'
        self._pub = self.create_publisher(Float64MultiArray, topic, 10)
        self._sub = self.create_subscription(
            Point,
            'pan_tilt_deg',
            self._on_pan_tilt,
            qos_profile_sensor_data,
        )
        self.get_logger().info(
            f'Подписка на pan_tilt_deg, публикация в {topic} (радианы для симуляции).'
        )

    def _on_pan_tilt(self, msg: Point) -> None:
        pan_d = _clamp_deg(msg.x)
        tilt_d = _clamp_deg(msg.y)
        out = Float64MultiArray()
        out.data = [math.radians(pan_d), math.radians(tilt_d)]
        self._pub.publish(out)


def main(args: Optional[list] = None) -> None:
    rclpy.init(args=args)
    node = PanTiltBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
