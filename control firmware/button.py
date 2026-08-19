"""
DESCRIPTION:
Class-based Hardware Driver for a Push Button.
Designed for Cytron MOTION 2350 Pro (Default Pin: GP28).
"""

from machine import Pin
import time

# --- Default Configuration ---
DEFAULT_BUTTON_PIN = 28


class Button:
    def __init__(self, pin_num=DEFAULT_BUTTON_PIN):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_DOWN)

    def is_pressed(self):
        """
        Reads the current state of the button.
        Returns:
            bool: True if the button is currently pressed, False otherwise.
        """
        return self.pin.value() == 1

    def wait_for_press(self, debounce_delay_ms=50):
        """
        Blocks the program execution until the button is pressed.
        Includes a simple delay for debouncing.
        """
        while not self.is_pressed():
            time.sleep_ms(10)
        
        # Debounce delay after the press is detected
        time.sleep_ms(debounce_delay_ms)
        
    def wait_for_release (self, debounce_delay_ms=50):
        """
        Blocks the program execution until the button is released.
        Includes a simple delay for debouncing.
        """
        while self.is_pressed():
            time.sleep_ms(10)
        
        # Debounce delay after the press is detected
        time.sleep_ms(debounce_delay_ms)

    def run_test(self):
        """
        Continuous test loop for standalone execution.
        Prints the button status when it changes.
        """
        print(f"--- Testing Push Button on GP{DEFAULT_BUTTON_PIN} ---")
        print("Press the button to see the status. Press Ctrl+C to stop.\n")
        
        last_state = False
        
        try:
            while True:
                if self.is_pressed():
                    print("Status: PRESSED  [1]")
                else:
                    print("Status: RELEASED [0]")
                
                time.sleep_ms(50)
                
        except KeyboardInterrupt:
            print("\nButton Test Stopped by User.")


if __name__ == "__main__":
    # Self-test block: Runs directly when this script is executed
    btn = Button()
    print("Wait for Press")
    btn.wait_for_press()
    btn.run_test()