import cv2
import numpy as np
import serial
import time
from picamera2 import Picamera2

# 1. Initialize UART Serial Port on Raspberry Pi 5
# /dev/ttyAMA0 is the default hardware serial port on Pi 5 GPIO pins 8 & 10
try:
    ser = serial.Serial('/dev/ttyAMA0', baudrate=115200, timeout=1)
    print("Serial port initialized successfully.")
except Exception as e:
    print(f"Error opening serial port: {e}")
    exit()

# 2. Initialize the Raspberry Pi Camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)
picam2.start()

print("Tracking started. Sending R, L, C to STM32. Press 'q' to quit.")

try:
    while True:
        frame_rgb = picam2.capture_array()
        hsv_frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)
        
        # Wide green color range for #00e300
        lower_green = np.array([35, 70, 50])
        upper_green = np.array([85, 255, 255])
        green_mask = cv2.inRange(hsv_frame, lower_green, upper_green)
        
        # Noise cleanup
        kernel = np.ones((5, 5), np.uint8)
        green_mask = cv2.erode(green_mask, kernel, iterations=1)
        green_mask = cv2.dilate(green_mask, kernel, iterations=2)

        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        blacked_out_frame = cv2.bitwise_and(frame_bgr, frame_bgr, mask=green_mask)

        # Draw zone lines
        cv2.line(blacked_out_frame, (213, 0), (213, 480), (100, 100, 100), 1)
        cv2.line(blacked_out_frame, (426, 0), (426, 480), (100, 100, 100), 1)

        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best_contour = None
        max_area = 0
        best_box_coords = None

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500: 
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                
                if 0.75 <= aspect_ratio <= 1.25:
                    if area > max_area:
                        max_area = area
                        best_contour = contour
                        best_box_coords = (x, y, w, h)

        # 3. Decision & Transmission Logic
        if best_contour is not None:
            x, y, w, h = best_box_coords
            center_x = x + (w // 2)
            
            # Determine Zone and the specific character byte to send
            if center_x < 213:
                position_text = "LEFT"
                serial_cmd = b'L'
            elif center_x > 426:
                position_text = "RIGHT"
                serial_cmd = b'R'
            else:
                position_text = "CENTER"
                serial_cmd = b'C'

            # Send the single character byte to STM32
            ser.write(serial_cmd)
            print(f"Sent: {serial_cmd.decode()} ({position_text})")

            # Visual overlay
            cv2.rectangle(blacked_out_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(blacked_out_frame, f"Sending: {serial_cmd.decode()}", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        else:
            # No valid green square found -> Send 'S' for Stop/Searching
            ser.write(b'S')
            print("Sent: S (No Target)")
        
        cv2.imshow("Pi5 to STM32 Tracker", blacked_out_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Clean up and safely close serial port
    print("\nClosing serial port and camera...")
    ser.close()
    picam2.stop()
    cv2.destroyAllWindows()