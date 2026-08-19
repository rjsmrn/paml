import sys
import select
import time
from proximity_sensor import DigitalSensor
from encoder_motor import EncoderMotor
from swing_motor import SwingMotor
from led import LED

# --- State Definitions ---
STATE_WAIT_OBJECT = 0       # สายพานวิ่งเรื่อยๆ รอเซนเซอร์ตรวจจับ
STATE_MOVING_TO_SENSOR = 1  # วัตถุแตะเซนเซอร์แล้ว กำลังเบรก
STATE_WAIT_CAMERA_CMD = 2   # รอคำสั่ง MOVE จาก PC
STATE_CENTERING_CAMERA = 3  # กำลังขยับ Encoder เพื่อจัดกึ่งกลาง

class MainController:
    def __init__(self):
        # สร้าง Instance จาก Class ที่มีอยู่
        # สมมติใช้ Active LOW หากเซนเซอร์ IR ส่งค่า 0 เมื่อเจอวัตถุ[cite: 8]
        self.sensor = DigitalSensor(pin_num=26, active_high=False) 
        self.EnBelt = EncoderMotor() #[cite: 5]
        self.belt = SwingMotor()
        
        self.state = STATE_WAIT_OBJECT
        self.poller = select.poll()
        self.poller.register(sys.stdin, select.POLLIN)

    def get_timestamp(self):
        """ดึงเวลาปัจจุบันมาจัดรูปแบบเป็น String YYYY-MM-DD HH:MM:SS"""
        t = time.localtime()
        # MicroPython time.localtime() จะคืนค่าเป็น tuple: (year, month, mday, hour, minute, second, weekday, yearday)
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4], t[5])

    def log_status(self, message):
        """ฟังก์ชันสำหรับเขียน Log ลงไฟล์ status.log"""
        timestamp = self.get_timestamp()
        log_line = f"[{timestamp}] {message}\n"
        
        try:
            # ใช้โหมด 'a' (Append) เพื่อเขียนต่อท้ายไฟล์
            with open("status.log", "a") as f:
                f.write(log_line)
        except Exception as e:
            pass # ป้องกันระบบล่มหากเขียนไฟล์ไม่ได้ (เช่น พื้นที่เต็ม)
        
    def read_serial_cmd(self):
        """อ่านคำสั่งจาก PC แบบ Non-blocking"""
        events = self.poller.poll(0)
        if events:
            return sys.stdin.readline().strip()
        return None

    def run(self):
        self.log_status("Entering STATE_WAIT_OBJECT...")
        print("Board Initialized. Entering STATE_WAIT_OBJECT...")
        
        try:
            while True:
                # --- STATE 0: วิ่งสายพานรอรับวัตถุ ---
                if self.state == STATE_WAIT_OBJECT:
                    # สั่งให้มอเตอร์เดินหน้าไปเรื่อยๆ (ขยับทีละนิดเพื่อไม่ให้ Block Loop)
                    self.belt.forward(40)
                    
                    # หาก Proximity Sensor ทำงาน[cite: 8]
                    if self.sensor.is_triggered(): 
                        self.belt.stop()
                        self.log_status("Sensor triggered! Conveyor stopped. Moving to STATE_WAIT_CAMERA_CMD.")
                        
                        print("STATE:SENSOR_HIT") # ส่งผ่าน Serial (print จะออกทาง stdout/UART)
                        self.state = STATE_WAIT_CAMERA_CMD
                        time.sleep(0.1) # Debounce
                        
                # --- STATE 2: รอการประมวลผลจากกล้อง ---
                elif self.state == STATE_WAIT_CAMERA_CMD:
                    cmd = self.read_serial_cmd()
                    if cmd and cmd.startswith("MOVE:"):
                        try:
                            # ดึงค่าระยะทางออกจาก String
                            distance = float(cmd.split(":")[1])
                            self.target_distance = distance
                            self.log_status(f"Received Camera CMD: MOVE {distance} cm. Moving to STATE_CENTERING_CAMERA.")
                            
                            self.state = STATE_CENTERING_CAMERA
                        except ValueError:
                            self.log_status(f"WARNING: Invalid command received: {cmd}")

                # --- STATE 3: จัดกึ่งกลางด้วย Encoder ---
                elif self.state == STATE_CENTERING_CAMERA:
                    if abs(self.target_distance) > 0.1:
                        # เรียกใช้ฟังก์ชันขยับระยะ[cite: 5] 
                        # ฟังก์ชันนี้เป็น Blocking แต่อยู่ในบริบทที่ปลอดภัยเพราะเป็นขั้นตอนสุดท้ายของรอบ
                        self.EnBelt.move_distance(target_cm=self.target_distance, power=30, tolerance_cm=0.2) 
                    
                    print("STATE:CENTERED")
                    time.sleep(2) # หยุดให้เห็นผลลัพธ์ว่ากลางแล้ว (ก่อนจำลองกลับไปเริ่มใหม่)
                    
                    # (Optional) หากต้องการให้ระบบทำงานต่ออัตโนมัติ ให้กลับไป State 0
                    # ในโปรเจกต์จริง อาจจะต้องรอคำสั่งจาก PC เพื่อวิ่งของออกไป
                    self.state = STATE_WAIT_OBJECT 
                    
                time.sleep(0.01) # ให้ CPU พัก ป้องกัน Loop รันเร็วกินทรัพยากรเกินไป

        except KeyboardInterrupt:
            self.log_status("System stopped by KeyboardInterrupt (User).")
            self.EnBelt.deinit() # เคลียร์ฮาร์ดแวร์ก่อนออก[cite: 5]
            self.belt.deinit()
            print("\nSystem Stopped.")

def log_error(exception):
    """ฟังก์ชันจัดการ Error แบบละเอียด"""
    try:
        t = time.localtime()
        timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4], t[5])
        
        # ใช้โหมด 'a' เพื่อไม่ให้ Error เก่าหายไป
        with open("error.log", "a") as f:
            f.write(f"\n[{timestamp}] --- SYSTEM CRASH ---\n")
            # ใช้ sys.print_exception เพื่อเขียน Traceback ลงไฟล์ (รองรับใน MicroPython)
            if hasattr(sys, 'print_exception'):
                sys.print_exception(exception, f)
            else:
                f.write(str(exception) + "\n")
    except:
        pass

if __name__ == "__main__":
    indicator = LED(pin_num=0) 
    
    # 1. แสดงสัญญาณไฟว่า main.py เริ่มรันแล้ว!
    indicator.blink(count=3, delay_ms=100)
    
    try:
        # ล้างไฟล์ status.log ของรอบเก่าทิ้ง (ลบส่วนนี้ออกถ้าอยากเก็บประวัติข้ามวัน)
        # เปิดไฟล์โหมด 'w' เพื่อเคลียร์ข้อมูลเดิมตอนบอร์ดเพิ่งเปิด
        with open("status.log", "w") as f:
            f.write("--- NEW SESSION START ---\n")
            
        # 2. เริ่มรันระบบหลัก
        controller = MainController()
        controller.run()
        
    except Exception as e:
        # 3. จัดการ Error
        indicator.on()
        log_error(e)