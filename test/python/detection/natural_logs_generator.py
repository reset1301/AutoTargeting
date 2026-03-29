import random
import time

# Настройки
TOTAL_FRAMES = 1000
CENTER_X, CENTER_Y = 160, 120  # Идеальный центр
NOISE_LEVEL = 2                # Мелкое дрожание (пиксели)
DRIFT_LEVEL = 5                 # Медленное плавание (пиксели)

def generate_natural_logs(filename):
    curr_x, curr_y = CENTER_X, CENTER_Y
    
    with open(filename, 'w') as f:
        for i in range(TOTAL_FRAMES):
            # 1. Генерируем "дрейф" (медленное смещение центра)
            curr_x += random.uniform(-0.5, 0.5)
            curr_y += random.uniform(-0.5, 0.5)
            
            # Удерживаем дрейф в разумных пределах от идеального центра
            curr_x = max(CENTER_X - DRIFT_LEVEL, min(CENTER_X + DRIFT_LEVEL, curr_x))
            curr_y = max(CENTER_Y - DRIFT_LEVEL, min(CENTER_Y + DRIFT_LEVEL, curr_y))
            
            # 2. Добавляем резкий "шум" нейросети (дрожание рамки)
            final_x = int(curr_x + random.randint(-NOISE_LEVEL, NOISE_LEVEL))
            final_y = int(curr_y + random.randint(-NOISE_LEVEL, NOISE_LEVEL))
            
            # Записываем в формате, который понимает ваш скетч
            f.write(f"{final_x},{final_y}\n")
            
    print(f"Файл {filename} успешно создан! (1000 кадров)")

if __name__ == "__main__":
    generate_natural_logs("coordinates.txt")
