/**
 * Hello World для ROS2 serial_bridge: два серво, строка "$PAN,TILT\n" или "PAN,TILT\n".
 * PAN → серво на пине 9, TILT → пин 10. Скорость USB Serial: 9600 (как в узле).
 *
 * Новичкам: Orange Pi по USB шлёт текстовые строки; Uno читает их как раньше в Serial Monitor.
 * Серво получает угол 0…180° (ширина импульса PWM формирует библиотека Servo).
 */
#include <Servo.h>

Servo panServo;
Servo tiltServo;

void setup() {
  // Та же скорость, что baud_rate у узла ROS2 на Pi (должны совпадать).
  Serial.begin(9600);
  panServo.attach(9);
  tiltServo.attach(10);
  // Стартовая нейтральная позиция (середина хода типичного серво 0…180).
  panServo.write(90);
  tiltServo.write(90);
  Serial.println(F("Ros2PanTiltHello: ready. Expect $PAN,TILT lines."));
}

void loop() {
  // Пока нет данных от USB — не блокируемся: loop() крутится дальше.
  if (Serial.available() <= 0) {
    return;
  }

  // Читаем одну строку до символа newline (ROS2 шлёт \n в конце кадра).
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) {
    return;
  }

  // Опциональный маркер начала кадра — проще отличить полезную строку от мусора.
  if (line.startsWith("$")) {
    line = line.substring(1);
  }

  int comma = line.indexOf(',');
  if (comma <= 0) {
    Serial.println(F("skip: no comma"));
    return;
  }

  int pan = line.substring(0, comma).toInt();
  int tilt = line.substring(comma + 1).toInt();
  // Защита: вне диапазона не отправляем на серво (избегаем странных положений).
  pan = constrain(pan, 0, 180);
  tilt = constrain(tilt, 0, 180);

  panServo.write(pan);
  tiltServo.write(tilt);

  // Отладка в Serial Monitor: можно смотреть, что реально распарсилось.
  Serial.print(F("ok pan="));
  Serial.print(pan);
  Serial.print(F(" tilt="));
  Serial.println(tilt);
}
