from maix import camera, display, image, nn, app, peripheral, uart, time

# 1. Инициализируем модель и камеру
detector = nn.YOLOv5(model="/root/models/yolov5s.mud", dual_buff = True)
cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

# 2. Инициализируем UART ОДИН РАЗ вне цикла
device = "/dev/ttyS0"
serial = uart.UART(device, 9600)

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    screen_center_x = img.width() / 2
    screen_center_y = img.height() / 2

    for obj in objs:            
        if (detector.labels[obj.class_id] == 'mouse'):
            img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_BLUE)    
            x_center = obj.x + obj.w / 2
            y_center = obj.y + obj.h / 2
            
            # Логика для отрисовки на экране
            msg_screen = f'{detector.labels[obj.class_id]}: '
            msg_screen += "right" if x_center > screen_center_x else "left"
            img.draw_string(obj.x, obj.y, msg_screen, color = image.COLOR_BLUE)
            
            # 3. ОТПРАВКА ДАННЫХ
            # Формируем строку и добавляем \n ОБЯЗАТЕЛЬНО
            out_data = f"{obj.x},{obj.y}\n"
            
            print(f"Sending: {out_data.strip()}") # Отладка в консоль камеры
            
            # Отправляем через encode() для надежности
            serial.write(out_data.encode()) 
            
        else:
            img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)    
            msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
            img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)

    disp.show(img)
