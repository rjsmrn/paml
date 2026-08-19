"""
DESCRIPTION:
Class-based Hardware Driver for NeoPixel RGB LEDs.
Designed for Cytron MOTION 2350 Pro (Default Pin: GP23, 2 LEDs).
"""

import machine
import neopixel
import time

# --- Default Configuration ---
DEFAULT_NEOPIXEL_PIN = 23
DEFAULT_NUM_PIXELS = 2


class Neopixel:
    # Predefined color constants (RGB decimal format)
    RED = (255, 0, 0)
    ORANGE = (255, 180, 0)
    YELLOW = (80, 80, 0)
    GREEN = (0, 255, 0)
    CYAN = (0, 255, 255)
    BLUE = (0, 0, 255)
    PURPLE = (180, 0, 255)
    WHITE = (100, 100, 100)
    BLACK = (0, 0, 0)  # Used for clearing the LEDs

    def __init__(self, pin_num=DEFAULT_NEOPIXEL_PIN, num_pixels=DEFAULT_NUM_PIXELS, default_brightness=0.5):
        """
        Initializes the NeoPixel driver.
        
        :param pin_num: GPIO pin connected to the NeoPixel data line.
        :param num_pixels: Total number of LEDs in the chain.
        :param default_brightness: Brightness scale from 0.0 to 1.0.
        """
        self.pin = machine.Pin(pin_num, machine.Pin.OUT)
        self.pixel = neopixel.NeoPixel(self.pin, num_pixels)
        self.num_pixels = num_pixels
        self.brightness = default_brightness
        
        # Turn off all LEDs upon initialization
        self.clear()

    def set_brightness(self, brightness):
        """
        Updates the global brightness level for future color sets.
        
        :param brightness: Float value between 0.0 (Off) and 1.0 (Full brightness).
        """
        self.brightness = max(0.0, min(brightness, 1.0))

    def _apply_brightness(self, color):
        """
        Internal method to scale RGB values based on current brightness.
        
        :param color: Tuple (R, G, B).
        :return: Scaled Tuple (R, G, B).
        """
        return (
            int(color[0] * self.brightness),
            int(color[1] * self.brightness),
            int(color[2] * self.brightness)
        )

    def fill(self, color):
        """
        Fills all NeoPixels with the specified color.
        
        :param color: Tuple (R, G, B).
        """
        adjusted_color = self._apply_brightness(color)
        self.pixel.fill(adjusted_color)
        self.pixel.write()

    def set_pixel(self, index, color):
        """
        Sets a specific NeoPixel to a given color.
        
        :param index: The index of the LED (0 to num_pixels - 1).
        :param color: Tuple (R, G, B).
        """
        if 0 <= index < self.num_pixels:
            self.pixel[index] = self._apply_brightness(color)
            self.pixel.write()

    def clear(self):
        """Turns off all NeoPixels."""
        self.pixel.fill(self.BLACK)
        self.pixel.write()

    def run_test(self):
        """
        Continuous test loop for standalone execution.
        Cycles through predefined colors continuously.
        """
        print(f"--- Testing NeoPixel on GP{DEFAULT_NEOPIXEL_PIN} ({self.num_pixels} LEDs) ---")
        print("Cycling colors. Press Ctrl+C to stop.\n")
        
        colors = [
            self.RED, self.ORANGE, self.YELLOW, self.GREEN, 
            self.CYAN, self.BLUE, self.PURPLE, self.WHITE
        ]
        
        try:
            while True:
                for color in colors:
                    self.fill(color)
                    time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nNeoPixel Test Stopped by User.")
        finally:
            self.deinit()

    def deinit(self):
        """Safely turns off the LEDs upon exit."""
        self.clear()


if __name__ == "__main__":
    # Self-test block: Runs directly when this script is executed
    rgb = Neopixel()
    rgb.set_brightness(0.05)
    rgb.run_test()