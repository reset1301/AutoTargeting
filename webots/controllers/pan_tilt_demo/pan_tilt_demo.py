"""Контроллер Webots: цель по эллипсу + слежение pan/tilt.

Шар TARGET_BALL движется в горизонтальной плоскости по эллипсу;
турель постоянно наводится на него (Supervisor + RotationalMotor).

Размеры (как в PanTiltTurret.proto):
  Lx_cam = 0.07, L_beam = 0.35
  высота эллипса = 10 * L_beam
  полуоси эллипса = 10 * L_beam и 7 * L_beam
  диаметр шара = 1 * Lx_cam

Углы моторов — радианы от центра (0 = «Arduino 90°»).
"""

import math

from controller import Supervisor

# --- Геометрия сцены (согласовано с PROTO) ---
_CAM_LENGTH = 0.07
_BEAM_LENGTH = 0.35

_BALL_RADIUS = _CAM_LENGTH / 2.0  # диаметр = 1× длина камеры
_ELLIPSE_Z = 10.0 * _BEAM_LENGTH  # высота плоскости
_ELLIPSE_A = 10.0 * _BEAM_LENGTH  # полуось по X
_ELLIPSE_B = 7.0 * _BEAM_LENGTH  # полуось по Y

# Приблизительный оптический центр при pan=tilt=0 (FLU, Z вверх).
_CAM_PIVOT = (0.0, 0.0, 0.15)

# Полный оборот шара по эллипсу, секунды.
_ORBIT_PERIOD_SEC = 20.0

_PAN_LIMIT = 1.5708
_TILT_LIMIT = 1.5708


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _look_at_angles(target, pivot=_CAM_PIVOT):
    """Pan (yaw вокруг Z) и tilt (pitch вокруг Y) из вектора на цель.

    При (pan, tilt) = (0, 0) камера смотрит вдоль +X.
    Положительный pan — к +Y; положительный tilt-мотор — нос вниз,
    поэтому команда tilt = −atan2(dz, r).
    """
    dx = target[0] - pivot[0]
    dy = target[1] - pivot[1]
    dz = target[2] - pivot[2]
    horizontal = math.hypot(dx, dy)
    pan = math.atan2(dy, dx)
    tilt = -math.atan2(dz, horizontal) if horizontal > 1e-6 else 0.0
    return (
        _clamp(pan, -_PAN_LIMIT, _PAN_LIMIT),
        _clamp(tilt, -_TILT_LIMIT, _TILT_LIMIT),
    )


def main() -> None:
    robot = Supervisor()
    timestep = int(robot.getBasicTimeStep())

    pan = robot.getDevice('pan')
    tilt = robot.getDevice('tilt')
    pan_sensor = robot.getDevice('pan_sensor')
    tilt_sensor = robot.getDevice('tilt_sensor')
    pan_sensor.enable(timestep)
    tilt_sensor.enable(timestep)

    ball = robot.getFromDef('TARGET_BALL')
    if ball is None:
        print('[pan_tilt_demo] ERROR: в мире нет DEF TARGET_BALL')
        return
    translation_field = ball.getField('translation')

    omega = 2.0 * math.pi / _ORBIT_PERIOD_SEC
    print(
        f'[pan_tilt_demo] ellipse a={_ELLIPSE_A:.2f} b={_ELLIPSE_B:.2f} '
        f'z={_ELLIPSE_Z:.2f}; ball r={_BALL_RADIUS:.3f}; T={_ORBIT_PERIOD_SEC:.0f}s'
    )

    while robot.step(timestep) != -1:
        t = robot.getTime()
        x = _ELLIPSE_A * math.cos(omega * t)
        y = _ELLIPSE_B * math.sin(omega * t)
        z = _ELLIPSE_Z
        translation_field.setSFVec3f([x, y, z])

        pan_cmd, tilt_cmd = _look_at_angles((x, y, z))
        pan.setPosition(pan_cmd)
        tilt.setPosition(tilt_cmd)


if __name__ == '__main__':
    main()
