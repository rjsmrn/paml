import cv2
import numpy as np

class Camera:
    def __init__(self, camera_id=0, blur_threshold=100.0):
        """
        Initialize camera settings
        :param camera_id: Camera ID (0 for primary camera, 1 for USB camera)
        :param blur_threshold: Threshold value for detecting image blur
        """
        self.camera_id = camera_id
        self.blur_threshold = blur_threshold
        self.cap = None
        
        # Center of the camera frame (Target for the object to stop)
        self.frame_center_x = 0
        self.frame_center_y = 0

        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=50, detectShadows=False)

    def connect(self):
        """Open camera connection and retrieve image dimensions"""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            print(f"[Error] Cannot open camera ID: {self.camera_id}")
            return False
        
        # Calculate the center of the camera (Center of Frame)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_center_x = width // 2
        self.frame_center_y = height // 2
        
        print(f"[Success] Camera opened successfully! Resolution: {width}x{height}")
        print(f"[Info] Screen Center (Now 0,0) is at pixel: ({self.frame_center_x}, {self.frame_center_y})")
        return True

    def get_focus_score(self, gray_frame):
        """Calculate image sharpness (Laplacian Variance)"""
        return cv2.Laplacian(gray_frame, cv2.CV_64F).var()

    def find_object_center(self, frame):
        """
        [MOG2 Version] Find the center of ANY moving/new object on the conveyor.
        """
        fg_mask = self.bg_subtractor.apply(frame)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            
            if cv2.contourArea(largest_contour) > 1000: 
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    # ค่า cx, cy ที่ได้ตรงนี้ ยังเป็นพิกัดดั้งเดิมของจอภาพ (0,0 อยู่ซ้ายบน)
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    return cx, cy, largest_contour
                    
        return None, None, None

    def process_frame(self):
        """Read frame to calculate Focus Score and draw UI"""
        ret, frame = self.cap.read()
        if not ret:
            return False, None
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        focus_score = self.get_focus_score(gray)
        is_focused = focus_score >= self.blur_threshold
        
        color = (0, 255, 0) if is_focused else (0, 0, 255)
        status_text = "Focused" if is_focused else "Blurry!"
        text = f"Focus Score: {focus_score:.2f} [{status_text}]"
        
        cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)
        
        # วาดเป้า (Crosshair) ตรงกลางจอ ซึ่งตอนนี้คือพิกัด (0,0)
        cv2.line(frame, (self.frame_center_x, self.frame_center_y - 20), (self.frame_center_x, self.frame_center_y + 20), (255, 0, 0), 2)
        cv2.line(frame, (self.frame_center_x - 20, self.frame_center_y), (self.frame_center_x + 20, self.frame_center_y), (255, 0, 0), 2)
        # พิมพ์บอกว่าตรงนี้คือ (0,0)
        cv2.putText(frame, "(0, 0)", (self.frame_center_x + 5, self.frame_center_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        # ค้นหาวัตถุ
        obj_x, obj_y, obj_contour = self.find_object_center(frame)
        
        if obj_x is not None:
            # 1. วาดกรอบสี่เหลี่ยมตามพิกัดหน้าจอปกติ
            x, y, w, h = cv2.boundingRect(obj_contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.circle(frame, (obj_x, obj_y), 5, (0, 0, 255), -1)
            
            # --- [NEW] 2. แปลงพิกัดให้ 0,0 อยู่ตรงกลางหน้าจอ ---
            # Center X = 0 (ขวาเป็นบวก, ซ้ายเป็นลบ)
            centered_x = obj_x - self.frame_center_x
            # Center Y = 0 (บนเป็นบวก, ล่างเป็นลบ แบบกราฟคณิตศาสตร์)
            centered_y = self.frame_center_y - obj_y 
            
            # 3. แสดงข้อความพิกัดใหม่ที่แปลงแล้ว
            coord_text = f"Object ({centered_x}, {centered_y})"
            cv2.putText(frame, coord_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return True, frame

    def disconnect(self):
        """Close camera connection"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("[Info] Camera closed successfully.")

    def run_test(self):
        """
        Continuous test loop for standalone execution.
        """
        print(f"--- Testing USB Camera (ID: {self.camera_id}) ---")
        
        if not self.connect():
            print("Failed to start camera test.")
            return

        print("Camera test started! Press 'q' in the video window to stop.")
        
        try:
            while True:
                ret, frame = self.process_frame()
                if not ret:
                    print("Unable to receive frame from the camera.")
                    break

                cv2.imshow('Conveyor Vision System - Center 0,0', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nUSB Camera Test Stopped by User.")
                    break
                    
        except KeyboardInterrupt:
            print("\nUSB Camera Test Stopped by KeyboardInterrupt.")
        finally:
            self.disconnect()

if __name__ == "__main__":
    camera = Camera(camera_id=1, blur_threshold=100.0)
    camera.run_test()