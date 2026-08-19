"""
DESCRIPTION:
Class-based Hardware Driver for a Stepper Motor.
Designed for Cytron MOTION 2350 Pro.
"""

from machine import Pin
import time

# --- Default Configuration ---
DEFAULT_STEP_PIN = 0
DEFAULT_DIR_PIN = 1
DEFAULT_EN_PIN = 28


class StepperMotor:
    def __init__(self, step_pin=DEFAULT_STEP_PIN, dir_pin=DEFAULT_DIR_PIN, en_pin=DEFAULT_EN_PIN):
        """
        Initializes the stepper motor driver pins.
        The Enable (EN) pin is typically Active LOW for stepper drivers.
        """
        self.step_pin = Pin(step_pin, Pin.OUT)
        self.dir_pin = Pin(dir_pin, Pin.OUT)
        self.en_pin = Pin(en_pin, Pin.OUT)
        
        # Ensure the motor is disabled at startup for safety
        self.disable()
        
        # Ensure step pin starts LOW
        self.step_pin.value(0)
        self.current_direction = 0
        self.dir_pin.value(self.current_direction)

    def enable(self):
        """Enables the stepper motor driver (Active LOW)."""
        self.en_pin.value(0)

    def disable(self):
        """Disables the stepper motor driver (HIGH)."""
        self.en_pin.value(1)

    def set_direction(self, direction):
        """
        Sets the rotation direction.
        
        :param direction: 0 or 1.
        """
        self.current_direction = direction
        self.dir_pin.value(self.current_direction)
        # Small delay to ensure the driver registers the direction change
        time.sleep_us(10)

    def step_once(self, delay_us=10):
        """
        Executes a single step pulse.
        
        :param delay_us: Delay in microseconds for the pulse width and interval.
        """
        self.step_pin.value(1)
        time.sleep_us(delay_us)
        self.step_pin.value(0)
        time.sleep_us(delay_us)

    def move_steps(self, steps, direction=None, delay_us=10):
        """
        Moves the motor a specific number of steps.
        
        :param steps: Number of steps to move.
        :param direction: 0 or 1. If None, uses current direction.
        :param delay_us: Speed control (lower is faster, but requires higher current).
        """
        if direction is not None:
            self.set_direction(direction)
            
        self.enable()
        for _ in range(steps):
            self.step_once(delay_us)

    def run_test(self):
        """
        Continuous test loop for standalone execution.
        Replicates the original logic: continuous steps, changing direction every 3 seconds.
        """
        print(f"--- Testing Stepper Motor (STEP:{DEFAULT_STEP_PIN}, DIR:{DEFAULT_DIR_PIN}, EN:{DEFAULT_EN_PIN}) ---")
        print("Motor will change direction every 3 seconds. Press Ctrl+C to stop.\n")
        
        STEP_DELAY_US = 20    
        DIRECTION_TIME_MS = 3000
        
        self.enable()
        self.set_direction(0)
        last_direction_change = time.ticks_ms()
        
        try:
            while True:
                self.step_once(delay_us=STEP_DELAY_US)
                
                current_time = time.ticks_ms()
                
                # Check if it's time to change direction
                if time.ticks_diff(current_time, last_direction_change) >= DIRECTION_TIME_MS:
                    new_direction = not self.current_direction
                    self.set_direction(new_direction)
                    last_direction_change = current_time
                    
        except KeyboardInterrupt:
            print("\nStepper motor test stopped by user.")
        finally:
            self.deinit()

    def deinit(self):
        """Safely disables the motor upon exit."""
        self.step_pin.value(0)
        self.disable()


if __name__ == "__main__":
    # Self-test block: Runs directly when this script is executed
    stepper = StepperMotor()
    stepper.run_test()