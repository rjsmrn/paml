"""
DESCRIPTION:
Class-based Hardware Driver for Encoder
Designed for Cytron MOTION 2350 Pro (Terminal: GP16 & GP17).

AUTHOR : Adapted for Lab Style Architecture
"""
from machine import Pin
import machine
import time
import sys

# Attempt to import the PIO Encoder driver 
# Ensure your library file is named 'QEnc_Pio_4.py' on the board
try:
    from QEnc_Pio_4 import QEnc_Pio_4
except ImportError:
    print("FATAL ERROR: QEnc_Pio_4.py (Encoder Library) not found.")
    sys.exit()
    
# Encoder Pins (for PIO)
ENCODER_A_PIN = 16   # (A Phase)
ENCODER_B_PIN = 17   # (B Phase)

DEFUALT_WHEEL_DIAMETER_CM = 6.5 #wheel diameter (cm) for distance calculation
DEFUALT_PPR = 360 #Pulses Per Revolution

class Encoder:
    def __init__(self, pin_a_num=ENCODER_A_PIN, pin_b_num=ENCODER_B_PIN, sm_id=0, ppr=DEFUALT_PPR, wheel_diameter_cm=DEFUALT_WHEEL_DIAMETER_CM):

        self.pin_a = Pin(pin_a_num, Pin.IN, Pin.PULL_UP)
        self.pin_b = Pin(pin_b_num, Pin.IN, Pin.PULL_UP)
        self.ppr = ppr
        self.wheel_diameter_cm = wheel_diameter_cm
        
        try:
            self.encoder_pio = QEnc_Pio_4((self.pin_a, self.pin_b), sm_id=sm_id, freq=machine.freq())
        except Exception as e:
            print(f"ERROR Initializing QEnc_Pio_4: {e}")
            self.encoder_pio = None

    def read_pulses(self):
        """Read the current pulse count (Integer)."""
        if self.encoder_pio:
            return self.encoder_pio.read()
        return 0

    def reset_count(self):
        """Reset the pulse count back to 0 (if supported by the library)."""
        if hasattr(self.encoder_pio, 'reset'):
            self.encoder_pio.reset()

    def read_distance_cm(self):
        """Convert pulse count to distance (in centimeters)."""
        pulses = self.read_pulses()
        circumference = 3.14159 * self.wheel_diameter_cm
        distance = (pulses / self.ppr) * circumference
        return distance

    def run_test(self):
        """Standalone Test Loop"""
        print(f"--- Testing Encoder on GP{ENCODER_A_PIN} / GP{ENCODER_B_PIN} ---")
        try:
            while True:
                pulses = self.read_pulses()
                dist = self.read_distance_cm()
                print(f"Pulses: {pulses:<8} | Distance: {dist:.2f} cm")
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopped")
        finally:
            self.deinit()

    def deinit(self):
        if self.encoder_pio:
            if hasattr(self.encoder_pio, 'deinit'):
                self.encoder_pio.deinit()
            elif hasattr(self.encoder_pio, 'qenc'):
                self.encoder_pio.qenc.active(0)
                
if __name__ == "__main__":
    Encoder().run_test()