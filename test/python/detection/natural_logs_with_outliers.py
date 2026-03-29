import random

# Настройки
TOTAL_FRAMES = 1000
CENTER_X, CENTER_Y = 160, 120  # Идеальный центр
NOISE_LEVEL = 3                # Обычное дрожание (пиксели)
OUTLIER_CHANCE = 0.02          # Вероятность вылета (2% кадров)
OUTLIER_RANGE = (40, 80)       # Амплитуда ошибки нейросети

def generate_noisy_logs(filename):
    with open(filename, 'w') as f:
        for i in range(TOTAL_FRAMES):
            # Базовые координаты с легким шумом
            x = CENTER_X + random.randint(-NOISE_LEVEL, NOISE_LEVEL)
            y = CENTER_Y + random.randint(-NOISE_LEVEL, NOISE_LEVEL)
            
            # Добавляем редкий "вылет"
            if random.random() < OUTLIER_CHANCE:
                # Случайно выбираем направление вылета (влево/вправо/вверх/вниз)
                x += random.choice([-1, 1]) * random.randint(*OUTLIER_RANGE)
                y += random.choice([-1, 1]) * random.randint(*OUTLIER_RANGE)
            
            # Запись в файл
            f.write(f"{x},{y}\n")
            
    print(f"Готово! Создан файл {filename} с {TOTAL_FRAMES} кадрами и аномалиями.")

if __name__ == "__main__":
    generate_noisy_logs("coordinates_with_glitches.txt")
