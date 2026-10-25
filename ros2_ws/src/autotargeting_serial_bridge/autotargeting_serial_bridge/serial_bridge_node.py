"""Узел-мост: подписка на углы pan/tilt → строка в UART для Arduino.

В терминах ROS2 это один **Node** (узел): процесс, который участвует в графе DDS.
Он **подписывается** на **Topic** (топик) — именованный канал сообщений; другие узлы
могут **публиковать** туда же. Здесь вход — углы, выход — байты в USB-UART к Arduino.

Соглашение по сообщению geometry_msgs/msg/Point:
  - x — угол PAN (градусы, 0…180)
  - y — угол TILT (градусы, 0…180)
  - z — не используется

Строка на линии (по умолчанию): $PAN,TILT\\n — см. README roadmap проекта.
Целевая ОС для запуска: Ubuntu 22.04, ROS 2 Humble (как на Orange Pi).
"""

import threading
from typing import Optional

import serial
from geometry_msgs.msg import Point
import rclpy
from rclpy.node import Node
# QoS — политика доставки сообщений (очередь, надёжность). Для «свежих» команд
# углов часто берут профиль как у сенсоров: последнее сообщение важнее старых.
from rclpy.qos import qos_profile_sensor_data


def _clamp_angle(value: float) -> int:
    # Стандартный hobby-серво обычно ожидает угол 0…180°; выход за диапазон не шлём.
    return int(max(0, min(180, round(value))))


class SerialBridgeNode(Node):
    """ROS2-узел: превращает сообщения топика в текстовую строку для прошивки Arduino."""

    def __init__(self) -> None:
        # Имя узла в графе ROS2 (видно в `ros2 node list`).
        super().__init__('serial_bridge_node')

        # Parameters — «настройки извне», как properties в Spring: их можно менять
        # при запуске или через `ros2 param set`, не перекомпилируя код.
        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('baud_rate', 9600)
        self.declare_parameter('use_frame_prefix', True)
        self.declare_parameter('demo_mode', False)
        self.declare_parameter('demo_period_sec', 3.0)

        port = self.get_parameter('serial_port').get_parameter_value().string_value
        baud = self.get_parameter('baud_rate').get_parameter_value().integer_value
        self._use_prefix = self.get_parameter('use_frame_prefix').get_parameter_value().bool_value
        demo = self.get_parameter('demo_mode').get_parameter_value().bool_value
        demo_period = float(self.get_parameter('demo_period_sec').get_parameter_value().double_value)

        # Запись в COM/UART из колбэка подписки и из таймера может прийти почти одновременно;
        # lock защищает последовательность байт в порту (как synchronized на общем ресурсе).
        self._serial_lock = threading.Lock()
        self._ser: Optional[serial.Serial] = None

        try:
            # pyserial открывает устройство Linux вроде /dev/ttyUSB0 — это «низкий уровень»,
            # тот же поток байтов, что и Serial Monitor в Arduino IDE.
            self._ser = serial.Serial(port, baud, timeout=0.2)
            self.get_logger().info(f'UART открыт: {port} @ {baud}')
        except serial.SerialException as e:
            self.get_logger().error(
                f'Не удалось открыть {port}: {e}. '
                'Проверьте кабель, права на порт (dialout) и имя устройства.'
            )
            # В demo можно поднять узел без железа (только логи); для боевого режима без порта — выход.
            if not demo:
                raise SystemExit(1) from e

        # Subscription: при каждом новом сообщении в топике вызывается _on_pan_tilt.
        self._sub = self.create_subscription(
            Point,
            'pan_tilt_deg',
            self._on_pan_tilt,
            qos_profile_sensor_data,
        )

        self._demo_step = 0
        if demo:
            if demo_period < 0.5:
                demo_period = 0.5
            # Timer в ROS2 периодически вызывает колбэк в том же executor (как scheduled task).
            self._demo_timer = self.create_timer(demo_period, self._demo_tick)
            self.get_logger().info('Режим demo_mode: периодическая отправка углов на UART')

    def _write_line(self, pan: int, tilt: int) -> None:
        if self._ser is None or not self._ser.is_open:
            self.get_logger().warning('UART недоступен, строка не отправлена')
            return
        body = f'{pan},{tilt}'
        # Префикс '$' согласован со скетчем: проще отличить кадр от мусора при синхронизации.
        line = f'${body}\n' if self._use_prefix else f'{body}\n'
        data = line.encode('ascii', errors='strict')
        with self._serial_lock:
            self._ser.write(data)

    def _on_pan_tilt(self, msg: Point) -> None:
        pan = _clamp_angle(msg.x)
        tilt = _clamp_angle(msg.y)
        self._write_line(pan, tilt)

    def _demo_tick(self) -> None:
        # Небольшой «Hello World» без внешнего publisher: три позиции по кругу.
        seq = [(90, 90), (120, 60), (60, 120)]
        pan, tilt = seq[self._demo_step % len(seq)]
        self._demo_step += 1
        self.get_logger().info(f'demo: pan={pan} tilt={tilt}')
        self._write_line(pan, tilt)

    def destroy_node(self) -> bool:
        # Явно закрываем порт, чтобы освободить USB-UART для других процессов.
        with self._serial_lock:
            if self._ser is not None and self._ser.is_open:
                self._ser.close()
        return super().destroy_node()


def main(args=None) -> None:
    # rclpy.init — инициализация клиентской библиотеки ROS2 для этого процесса (один раз).
    rclpy.init(args=args)
    node = SerialBridgeNode()
    try:
        # spin — цикл обработки: доставка сообщений таймерам и подпискам, пока не остановите узел.
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
