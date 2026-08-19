"""
DESCRIPTION:
Class-based Hardware Driver for a single Indicator LED.
Designed for Cytron MOTION 2350 Pro / MicroPython RP2350.
"""

from machine import Pin
import time

# --- Default Configuration ---
# Default to GP25 (standard onboard LED pin for Pico/RP2350, adjustable as needed)
DEFAULT_LED_PIN = 0


class LED:
    def __init__(self, pin_num=DEFAULT_LED_PIN):
        """
        Initializes the LED GPIO pin as output.
        Ensures the LED starts in the OFF state.
        """
        self.pin = Pin(pin_num, Pin.OUT)

    def on(self):
        """Turns the LED on."""
        self.pin.value(1)

    def off(self):
        """Turns the LED off."""
        self.pin.value(0)

    def toggle(self):
        """Toggles the current state of the LED."""
        self.pin.value(not self.pin.value())

    def is_on(self):
        """Returns True if the LED is currently ON, False otherwise."""
        return self.pin.value() == 1

    def blink(self, count=3, delay_ms=200):
        """
        Blinks the LED for a specified number of times.
        
        :param count: Number of blink cycles.
        :param delay_ms: On/Off duration in milliseconds.
        """
        for _ in range(count):
            self.on()
            time.sleep_ms(delay_ms)
            self.off()
            time.sleep_ms(delay_ms)

    def run_test(self):
        """
        Continuous test loop for standalone execution.
        Toggles the LED state every 500 ms.
        """
        print(f"--- Testing LED on Pin {self.pin} ---")
        print("Toggling LED state. Press Ctrl+C to stop.\n")

        try:
            while True:
                self.toggle()
                state_str = "ON" if self.is_on() else "OFF"
                print(f"LED State: {state_str}")
                time.sleep_ms(500)
        except KeyboardInterrupt:
            print("\nLED Test Stopped by User.")
        finally:
            self.deinit()

    def deinit(self):
        """Safely turns off the LED upon exit."""
        self.off()


if __name__ == "__main__":
    # Self-test block: Runs directly when this script is executed
    led = LED()
    led.run_test()
