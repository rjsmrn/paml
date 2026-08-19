import cv2
import serial
import time
from camera import Camera # อ้างอิงจากคลาส Camera ที่มีอยู่

# --- Configurations ---
SERIAL_PORT = 'COM8'  # เปลี่ยนตาม Port จริงที่เชื่อมต่อกับ 2350 Pro
BAUD_RATE = 115200
PIXELS_PER_CM = 35.0  # ค่า K (Calibration): ต้องปรับจูนตามระยะเลนส์จริง

def main():
    # 1. เชื่อมต่อ Serial
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[{time.strftime('%H:%M:%S')}] [PC] Serial connected on {SERIAL_PORT}")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] [PC] Serial Error: {e}")
        return

    # 2. เริ่มต้นใช้งานกล้อง
    cam = Camera(camera_id=1) #
    if not cam.connect():
        print(f"[{time.strftime('%H:%M:%S')}] [PC] Camera connection failed.")
        return

    print(f"[{time.strftime('%H:%M:%S')}] [PC] System Ready. Waiting for signals from board...")

    try:
        while True:
            # รับคำสั่งจากบอร์ด
            if ser.in_waiting > 0:
                msg = ser.readline().decode('utf-8').strip()
                
                if msg == "STATE:SENSOR_HIT":
                    print(f"[{time.strftime('%H:%M:%S')}] [PC] Sensor triggered! Processing image...")
                    time.sleep(0.5) # รอให้วัตถุนิ่งสนิทและกล้องโฟกัส

                    # อ่านภาพและหาศูนย์กลาง (ใช้ MOG2)
                    ret, frame = cam.process_frame() 
                    
                    if ret:
                        obj_x, obj_y, _ = cam.find_object_center(frame) #
                        
                        if obj_y is not None:
                            # คำนวณ Error Position
                            error_pixels = cam.frame_center_y - obj_y #
                            distance_cm = error_pixels / PIXELS_PER_CM
                            
                            print(f"[{time.strftime('%H:%M:%S')}] [PC] Object at {obj_y}, Center at {cam.frame_center_y}")
                            print(f"[{time.strftime('%H:%M:%S')}] [PC] Error: {error_pixels} px -> Moving: {distance_cm:.2f} cm")
                            
                            # ส่งคำสั่งไปบอร์ด
                            ser.write(f"MOVE:{distance_cm:.2f}\n".encode('utf-8'))
                        else:
                            print(f"[{time.strftime('%H:%M:%S')}] [PC] ERROR: Object not found in frame. Retrying...")
                            # หากไม่เจอวัตถุ สั่งขยับ 0 cm เพื่อหลีกเลี่ยงการค้างของ State
                            ser.write(b"MOVE:0.0\n")
                            
            # (Optional) แสดงภาพระหว่างรอเพื่อ Monitor ระบบ
            ret, frame = cam.process_frame()
            if ret:
                cv2.imshow('Conveyor Monitor', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    except KeyboardInterrupt:
        # ใส่ \n ไว้หน้าสุดเพื่อให้เวลาแสดง ^C บน Terminal ไม่ทับกับข้อความ
        print(f"\n[{time.strftime('%H:%M:%S')}] [PC] System stopped by user.")
    finally:
        cam.disconnect() #
        ser.close()

if __name__ == "__main__":
    main()