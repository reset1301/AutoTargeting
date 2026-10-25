"""Контроллер: шар по эллипсу + наведение pan/tilt через моторы.

Почему раньше «теряли» шар в одном месте:
  эллипс был вокруг начала координат → цель уходила в заднюю полусферу,
  а мотор pan ограничен ±90° (как hobby-серво). На упоре турель разворачивалась
  и ждала, пока шар снова появится спереди.

Почему сыпались ошибки supervisor:
  position сустава внутри PROTO — read-only для set_sf_float.
  Наведение только через RotationalMotor.setPosition().

Эллипс с теми же полуосями/высотой сдвинут вперёд (+X), целиком в зоне pan.
"""

import math

from controller import Supervisor

_BEAM_LENGTH = 0.35

_ELLIPSE_Z = 10.0 * _BEAM_LENGTH
_ELLIPSE_A = 10.0 * _BEAM_LENGTH  # полуось вдоль X (вперёд)
_ELLIPSE_B = 7.0 * _BEAM_LENGTH  # полуось вдоль Y (влево/вправо)
# Центр орбиты впереди турели: весь эллипс в x > 0 (pan ∈ ±90°).
# C > A  ⇒  минимальный x = C − A > 0.
_ELLIPSE_CENTER_X = _ELLIPSE_A + 1.5  # x ∈ [1.5 .. 2A+1.5]
_ELLIPSE_CENTER_Y = 0.0

# Ось tilt после поднятия пьедестала: pan@0.42 + tilt@0.06 ≈ 0.48 м.
_CAM_PIVOT = (0.0, 0.0, 0.48)
_ORBIT_PERIOD_SEC = 20.0

_PAN_LIMIT = 1.5708
_TILT_LIMIT = 1.5708


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _look_at_angles(target, pivot=_CAM_PIVOT):
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

    pan_motor = robot.getDevice('pan')
    tilt_motor = robot.getDevice('tilt')

    ball = robot.getFromDef('TARGET_BALL')
    if ball is None:
        print('[pan_tilt_demo] ERROR: в мире нет DEF TARGET_BALL')
        return
    translation_field = ball.getField('translation')

    omega = 2.0 * math.pi / _ORBIT_PERIOD_SEC
    x_min = _ELLIPSE_CENTER_X - _ELLIPSE_A
    x_max = _ELLIPSE_CENTER_X + _ELLIPSE_A
    print(
        f'[pan_tilt_demo] ellipse center=({_ELLIPSE_CENTER_X:.2f}, '
        f'{_ELLIPSE_CENTER_Y:.2f}, {_ELLIPSE_Z:.2f}) '
        f'a={_ELLIPSE_A:.2f} b={_ELLIPSE_B:.2f}; x∈[{x_min:.2f},{x_max:.2f}]'
    )

    while robot.step(timestep) != -1:
        t = robot.getTime()
        x = _ELLIPSE_CENTER_X + _ELLIPSE_A * math.cos(omega * t)
        y = _ELLIPSE_CENTER_Y + _ELLIPSE_B * math.sin(omega * t)
        z = _ELLIPSE_Z
        translation_field.setSFVec3f([x, y, z])

        pan_des, tilt_des = _look_at_angles((x, y, z))
        pan_motor.setPosition(pan_des)
        tilt_motor.setPosition(tilt_des)


if __name__ == '__main__':
    main()
