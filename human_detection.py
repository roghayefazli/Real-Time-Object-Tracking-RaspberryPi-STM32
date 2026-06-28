import cv2
import numpy as np
import serial
import time
from picamera2 import Picamera2
import mediapipe as mp

# ۱. تنظیمات مربوط به محاسبه فاصله (کالیبراسیون فرضی)
# برای دقیق شدن فاصله، باید این اعداد را با تست واقعی تنظیم کنید.
KNOWN_WIDTH = 50.0  # عرض تقریبی شانه یا بدن یک انسان متوسط به سانتی‌متر
FOCAL_LENGTH = 500.0 # طول کانونی دوربین بر حسب پیکسل (نیاز به کالیبراسیون دارد)

# ۲. راه‌اندازی پورت سریال UART روی رزبری پای ۵
try:
    ser = serial.Serial('/dev/ttyAMA0', baudrate=115200, timeout=1)
    print("Serial port initialized successfully.")
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit()

# ۳. راه‌اندازی دوربین رزبری پای
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)
picam2.start()

# ۴. راه‌اندازی مدل تشخیص انسان MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

print("Human Tracking started. Sending R, L, C, S to STM32. Press 'q' to quit.")

try:
    while True:
        frame_rgb = picam2.capture_array()
        hsv_frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)
        
        # تبدیل به BGR برای نمایش در OpenCV
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        h, w, _ = frame_bgr.shape

        # پردازش تصویر برای یافتن انسان
        results = pose.process(frame_rgb)

        # رسم خطوط نواحی چپ، راست و وسط
        cv2.line(frame_bgr, (213, 0), (213, 480), (255, 0, 0), 1)
        cv2.line(frame_bgr, (426, 0), (426, 480), (255, 0, 0), 1)

        human_detected = False

        if results.pose_landmarks:
            human_detected = True
            landmarks = results.pose_landmarks.landmark
            
            # پیدا کردن مختصات شانه‌ها برای تخمین مرکز و عرض بدن
            # Landmark 11: شانه چپ | Landmark 12: شانه راست
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            
            # تبدیل مختصات نسبی (0 تا 1) به مختصات پیکسلی تصویر
            ls_x, ls_y = int(left_shoulder.x * w), int(left_shoulder.y * h)
            rs_x, rs_y = int(right_shoulder.x * w), int(right_shoulder.y * h)
            
            # ۱. محاسبه نقطه وسط انسان (مرکز بین دو شانه)
            center_x = (ls_x + rs_x) // 2
            center_y = (ls_y + rs_y) // 2
            
            # ۲. محاسبه عرض ظاهری انسان در تصویر (بر حسب پیکسل) برای تخمین فاصله
            pixel_width = abs(ls_x - rs_x)
            if pixel_width == 0: pixel_width = 1 # جلوگیری از خطای تقسیم بر صفر
            
            # ۳. محاسبه فرمول فاصله
            distance = (KNOWN_WIDTH * FOCAL_LENGTH) / pixel_width
            
            # تعیین جهت حرکت (Logic قبلی شما)
            if center_x < 213:
                position_text = "LEFT"
                serial_cmd = b'L'
            elif center_x > 426:
                position_text = "RIGHT"
                serial_cmd = b'R'
            else:
                position_text = "CENTER"
                serial_cmd = b'C'

            # ارسال فرمان به STM32
            ser.write(serial_cmd)
            print(f"Sent: {serial_cmd.decode()} ({position_text}) | Distance: {distance:.2f} cm")

            # رسم نقطه وسط انسان
            cv2.circle(frame_bgr, (center_x, center_y), 8, (0, 0, 255), -1) 
            
            # رسم خط بین دو شانه برای مشخص شدن محدوده محاسباتی
            cv2.line(frame_bgr, (ls_x, ls_y), (rs_x, rs_y), (0, 255, 0), 3)
            
            # نمایش متن فاصله و جهت روی تصویر
            cv2.putText(frame_bgr, f"Dist: {distance:.1f} cm", (center_x - 50, center_y - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(frame_bgr, f"Sending: {serial_cmd.decode()}", (center_x - 50, center_y - 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        if not human_detected:
            # اگر انسانی پیدا نشد -> ارسال فرمان S
            ser.write(b'S')
            print("Sent: S (No Human Target)")
        
        # نمایش تصویر زنده
        cv2.imshow("Pi5 Human Tracker & Distance Finder", frame_bgr)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # تمیزکاری و بستن پورت‌ها
    print("\nClosing serial port, camera and model...")
    ser.close()
    picam2.stop()
    pose.close()
    cv2.destroyAllWindows()