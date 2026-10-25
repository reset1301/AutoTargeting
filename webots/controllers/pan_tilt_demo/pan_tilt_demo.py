"""Demo-контроллер Webots для PanTiltTurret.

Двигает оси pan/tilt по кругу позиций — визуальный «Hello World» без Arduino.
Углы в Webots — радианы от центра (0 = «Arduino 90°»).

Соответствие Arduino (градусы 0…180, центр 90):
    webots_rad = (arduino_deg - 90.0) * math.pi / 180.0

Запуск: откройте worlds/pan_tilt_turret.wbt в Webots и нажмите Run.
"""

import math

from controller import Robot

# Те же три позы, что в serial_bridge_node demo_mode (в градусах Arduino).
_DEMO_ARDUINO_DEG = [
    (90.0, 90.0),
    (120.0, 60.0),
    (60.0, 120.0),
]

# Сколько секунд держать каждую позу.
_HOLD_SEC = 2.0


def arduino_deg_to_webots(deg: float) -> float:
    return (deg - 90.0) * math.pi / 180.0


def main() -> None:
    robot = Robot()
    timestep = int(robot.getBasicTimeStep())

    pan = robot.getDevice('pan')
    tilt = robot.getDevice('tilt')
    pan_sensor = robot.getDevice('pan_sensor')
    tilt_sensor = robot.getDevice('tilt_sensor')

    pan_sensor.enable(timestep)
    tilt_sensor.enable(timestep)

    # Position control: задаём целевой угол, Webots сам крутит мотор.
    step_idx = 0
    hold_until = robot.getTime() + _HOLD_SEC

    pan_deg, tilt_deg = _DEMO_ARDUINO_DEG[0]
    pan.setPosition(arduino_deg_to_webots(pan_deg))
    tilt.setPosition(arduino_deg_to_webots(tilt_deg))
    print(f'[pan_tilt_demo] start: pan={pan_deg:.0f}° tilt={tilt_deg:.0f}° (Arduino)')

    while robot.step(timestep) != -1:
        now = robot.getTime()
        if now < hold_until:
            continue

        step_idx = (step_idx + 1) % len(_DEMO_ARDUINO_DEG)
        pan_deg, tilt_deg = _DEMO_ARDUINO_DEG[step_idx]
        pan.setPosition(arduino_deg_to_webots(pan_deg))
        tilt.setPosition(arduino_deg_to_webots(tilt_deg))
        hold_until = now + _HOLD_SEC

        print(
            f'[pan_tilt_demo] target Arduino pan={pan_deg:.0f}° tilt={tilt_deg:.0f}° | '
            f'sensors rad pan={pan_sensor.getValue():.3f} tilt={tilt_sensor.getValue():.3f}'
        )


if __name__ == '__main__':
    main()
