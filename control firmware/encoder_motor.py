"""
DESCRIPTION:
High-Level Controller combining Motor Driver and Encoder Driver
for Closed-Loop Position & Distance Control.
"""

import time
from swing_motor import SwingMotor
from encoder import Encoder

class EncoderMotor:
    def __init__(self, motor=None, encoder=None):
        # Automatically instantiate if no existing instances are passed
        self.motor = motor if motor else SwingMotor()
        self.encoder = encoder if encoder else Encoder()
    
    def forward(self, percent=50):
        self.motor.forward(percent=percent)
        
    def reverse(self, percent=50):
        self.motor.reverse(percent=percent)
        
    def stop(self):
        self.motor.stop()
    
    def move_distance(self, target_cm, power=30, tolerance_cm=0.5):
        """
        Drive the motor to a specified distance (in centimeters).
        :param target_cm: Target distance, e.g., 2.0 or -2.0 cm
        :param power: Motor speed percentage (%)
        :param tolerance_cm: Acceptable error margin/tolerance in cm
        """
        print(f"Moving to target: {target_cm} cm at {power}% power...")
        
        start_dist = self.encoder.read_distance_cm()
        destination = start_dist + target_cm

        try:
            while True:
                current_dist = self.encoder.read_distance_cm()
                error = destination - current_dist
                print(current_dist)

                # Check if target destination is reached within tolerance
                if abs(error) <= tolerance_cm:
                    self.stop()
                    print(f"[ARRIVED] Target: {destination:.2f} cm | Actual: {current_dist:.2f} cm")
                    break

                # Control direction based on position error
                if error > 0:
                    self.forward(power)
                else:
                    self.reverse(power)

                time.sleep(0.01) # Loop delay for system stability
                
        except KeyboardInterrupt:
            self.stop()
            print("\nMotion Interrupted!")

    def deinit(self):
        self.motor.deinit()
        self.encoder.deinit()


if __name__ == "__main__":
    # Self-test: Command the motor to move forward 2000 cm and then backward 1000 cm
    smart_motor = EncoderMotor()
    smart_motor.move_distance(target_cm=2000.0, power=10, tolerance_cm=10)
    smart_motor.move_distance(target_cm=-1000.0, power = 50, tolerance_cm=10)
    smart_motor.deinit()