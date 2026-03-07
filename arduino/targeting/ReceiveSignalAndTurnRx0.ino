#include <Servo.h>

Servo myServo;
const int CENTER_X = 112; // Половина ширины входного изображения YOLOv5 (224/2)

void setup() {
  // Скорость должна совпадать с настройкой в Python (9600)
  Serial.begin(9600); 
  myServo.attach(9);
  myServo.write(90); // Ставим в среднее положение
  Serial.println("Система запущена. Ожидание данных от Maix Cam...");
}

void loop() {
  if (Serial.available() > 0) {
    // Читаем строку до символа переноса \n
    String data = Serial.readStringUntil('\n');
    
    Serial.print("Получено от камеры: ");
    Serial.println(data);

    // Ищем запятую
    int commaIndex = data.indexOf(',');
    if (commaIndex != -1) {
      // Извлекаем X
      int x = data.substring(0, commaIndex).toInt();
      
      // Логика управления:
      if (x < (CENTER_X - 20)) {
        myServo.write(120); // Поворот в одну сторону
      } 
      else if (x > (CENTER_X + 20)) {
        myServo.write(60);  // Поворот в другую сторону
      } 
      else {
        myServo.write(90);  // Стоп/Центр, если объект посередине
      }
    }
  }
}
