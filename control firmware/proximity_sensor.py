"""
DESCRIPTION:
Class-based Hardware Driver for a generic Digital Sensor 
(e.g., IR obstacle sensor, proximity sensor, limit switch).
Designed for Cytron MOTION 2350 Pro (Default Pin: GP26).
"""

from machine import Pin
import time

# --- Default Configuration ---
DEFAULT_SENSOR_PIN = 26


class DigitalSensor:
    def __init__(self, pin_num=DEFAULT_SENSOR_PIN, pull_mode=None, active_high=True):
        """
        Initializes the digital sensor pin.
        
        :param pin_num: GPIO pin number connected to the sensor.
        :param pull_mode: Pin.PULL_UP, Pin.PULL_DOWN, or None (default for active sensors).
        :param active_high: Set to True if the sensor outputs 1 when triggered.
                            Set to False if the sensor outputs 0 when triggered (common for IR sensors).
        """
        if pull_mode is not None:
            self.pin = Pin(pin_num, Pin.IN, pull_mode)
        else:
            self.pin = Pin(pin_num, Pin.IN)
            
        self.active_high = active_high

    def is_triggered(self):
        """
        Checks if the sensor is currently detecting/triggered,
        based on the active_high configuration.
        
        :return: True if triggered, False otherwise.
        """
        current_val = self.pin.value()
        if self.active_high:
            return current_val == 1
        else:
            return current_val == 0

    def run_test(self):
        """
        Continuous test loop for standalone execution.
        Prints the sensor status when it changes.
        """
        print(f"--- Testing Digital Sensor on GP{DEFAULT_SENSOR_PIN} ---")
        mode_str = "HIGH" if self.active_high else "LOW"
        print(f"Sensor configured as Active {mode_str}. Press Ctrl+C to stop.\n")
        
        last_state = None
        
        try:
            while True:
                current_state = self.is_triggered()
                
                # Print only when the state changes
                if current_state != last_state:
                    if current_state:
                        print("Status: TRIGGERED [Detected]")
                    else:
                        print("Status: CLEAR     [Not Detected]")
                    last_state = current_state
                    
                time.sleep_ms(50) # Small delay for stability
                
        except KeyboardInterrupt:
            print("\nDigital Sensor Test Stopped by User.")


if __name__ == "__main__":
    # Self-test block: Runs directly when this script is executed
    
    # Note: If your IR sensor turns off its light when detecting an object, 
    # it is likely Active LOW. You can test it by changing active_high to False:
    # sensor = DigitalSensor(active_high=False)
    
    sensor = DigitalSensor()
    sensor.run_test()