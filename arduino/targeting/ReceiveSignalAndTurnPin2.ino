#include <Servo.h>
#include <SoftwareSerial.h>

// Создаем виртуальный порт: RX на пине 2, TX на пине 3
SoftwareSerial cameraSerial(2, 3); 

Servo myServo;
const int CENTER_X = 112; // Центр для модели 224x224

void setup() {
  // Инициализация порта для монитора порта (компьютер)
  Serial.begin(9600);
  // Инициализация порта для камеры
  cameraSerial.begin(9600);
  
  myServo.attach(9);
  myServo.write(90);
  
  Serial.println("Система запущена. Ожидание данных от Maix Cam...");
}

void loop() {
  // Проверяем данные от камеры
  if (cameraSerial.available() > 0) {
    // Читаем строку до символа переноса
    String data = cameraSerial.readStringUntil('\n');
    data.trim(); // Удаляем лишние пробелы/символы
    
    // ОТЛАДКА: Выводим «сырые» данные в монитор порта (USB)
    Serial.print("Получено от камеры: ");
    Serial.println(data);
    
    int commaIndex = data.indexOf(',');
    if (commaIndex != -1) {
      int x = data.substring(0, commaIndex).toInt();
      int y = data.substring(commaIndex + 1).toInt(); // Парсим Y для полноты
      
      // Отладка распарсенных значений
      Serial.print("Распознано -> X: "); Serial.print(x);
      Serial.print(" Y: "); Serial.println(y);

      // Логика управления серво
      if (x < (CENTER_X - 30)) {
        myServo.write(120); 
        Serial.println("Действие: Поворот ВЛЕВО");
      } 
      else if (x > (CENTER_X + 30)) {
        myServo.write(60);  
        Serial.println("Действие: Поворот ВПРАВО");
      } 
      else {
        myServo.write(90);  
        Serial.println("Действие: ЦЕНТР");
      }
    } else {
      Serial.println("Ошибка: Неверный формат строки (нет запятой)");
    }
    Serial.println("---"); 
  }
}
