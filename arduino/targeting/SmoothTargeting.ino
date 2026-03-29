#include <Servo.h>
#include <SoftwareSerial.h>

// 1. Определение типа через typedef (чтобы компилятор не ругался)
typedef struct {
  int x;
  int y;
  bool isValid;
} CoordinatePair;

// 2. Объявление объектов и переменных
SoftwareSerial cameraSerial(2, 3);
Servo myServo;

String dataBuffer = "";
float currentAngle = 90.0;
unsigned long framesSkipped = 0;

// Максимальный размер буфера
const int MAX_BUFFER_SIZE = 300;
// Параметры кадра камеры
const int CAM_WIDTH = 320;
const int CENTER_X = 160;
// Зона нечувствительности
const int DEADZONE = 15;
// Коэффициент сглаживания
const float SMOOTHING = 0.1;
// Шаг поворота сервопривода
const int STEP = 5;

// 3. ЯВНЫЕ ПРОТОТИПЫ МЕТОДОВ (обязательно для Wokwi)
void fillBuffer();
CoordinatePair getLatest();
void processMovement(CoordinatePair pair);

void setup() {
  Serial.begin(9600);
  cameraSerial.begin(9600);
  myServo.attach(9);
  myServo.write(90);
  Serial.println(F("--- Full System Online ---"));
}

void loop() {
  fillBuffer();
  CoordinatePair pair = getLatest();
  processMovement(pair);
  delay(15);
}

// --- РЕАЛИЗАЦИЯ МЕТОДОВ (внизу) ---

void fillBuffer() {
  while (Serial.available() > 0) {
    if (dataBuffer.length() < MAX_BUFFER_SIZE) dataBuffer += (char)Serial.read();
    else dataBuffer = "";
  }
  while (cameraSerial.available() > 0) {
    if (dataBuffer.length() < MAX_BUFFER_SIZE) dataBuffer += (char)cameraSerial.read();
    else dataBuffer = "";
  }
}

/**
 * @brief Получение последнего кадра из буфера
 * @return CoordinatePair - пара координат (x, y) с флагом isValid, если кадр валидный
 */
CoordinatePair getLatest() {
  CoordinatePair pair = {0, 0, false};
  int lastComma = dataBuffer.lastIndexOf(',');
  if (lastComma == -1) return pair;

  int endIdx = lastComma + 1;
  while (endIdx < dataBuffer.length() && isDigit(dataBuffer[endIdx])) endIdx++;

  if (endIdx == lastComma + 1) {
    lastComma = dataBuffer.lastIndexOf(',', lastComma - 1);
    if (lastComma == -1) return pair;
    endIdx = lastComma + 1;
    while (endIdx < dataBuffer.length() && isDigit(dataBuffer[endIdx])) endIdx++;
  }

  int startIdx = lastComma - 1;
  while (startIdx >= 0 && isDigit(dataBuffer[startIdx])) startIdx--;
  startIdx++;

  String sx = dataBuffer.substring(startIdx, lastComma);
  String sy = dataBuffer.substring(lastComma + 1, endIdx);

  if (sx.length() > 0 && sy.length() > 0) {
    long valX = sx.toInt();
    if (valX >= 0 && valX <= CAM_WIDTH) {
      pair.x = (int)valX;
      pair.y = sy.toInt();
      pair.isValid = true;
      dataBuffer = ""; // Чистим буфер после нахождения актуального кадра
    }
  }
  return pair;
}

void processMovement(CoordinatePair pair) {
  if (!pair.isValid) return;

  float targetAngle = currentAngle;
  if (pair.x < (CENTER_X - DEADZONE)) targetAngle += STEP;
  else if (pair.x > (CENTER_X + DEADZONE)) targetAngle -= STEP;

  // Экспоненциальное сглаживание
  currentAngle = (currentAngle * (1.0 - SMOOTHING)) + (targetAngle * SMOOTHING);
  currentAngle = constrain(currentAngle, 0, 180);

  myServo.write((int)currentAngle);

  // Диагностика раз в секунду
  static unsigned long lastLog = 0;
  if (millis() - lastLog > 1000) {
    Serial.print(F("X: ")); Serial.print(pair.x);
    Serial.print(F(" | Angle: ")); Serial.println((int)currentAngle);
    lastLog = millis();
  }
}
