"""
DESCRIPTION:
Class-based Hardware Driver for a Piezo Buzzer using PWM.
Designed for Cytron MOTION 2350 Pro (Default Pin: GP22).
Adapted for MicroPython compatibility.
"""

from machine import Pin, PWM
import time

# --- Default Configuration ---
DEFAULT_BUZZER_PIN = 22


class Buzzer:
    def __init__(self, pin_num=DEFAULT_BUZZER_PIN):
        """
        Initializes the Buzzer using Hardware PWM.
        """
        self.pwm = PWM(Pin(pin_num))
        self.stop()

    def play_tone(self, frequency, duration_s):
        """
        Plays a single tone at a specific frequency for a given duration.
        
        :param frequency: Frequency in Hz (e.g., 262 for Middle C). If 0, it acts as a rest.
        :param duration_s: Duration to play the tone in seconds.
        """
        if frequency <= 0:
            # Frequency of 0 means silence (rest)
            self.stop()
            time.sleep(duration_s)
        else:
            self.pwm.freq(int(frequency))
            self.pwm.duty_u16(32768)  # 50% duty cycle for maximum square wave volume
            time.sleep(duration_s)
            self.stop()

    def play_melody(self, notes, durations):
        """
        Plays a sequence of notes.
        
        :param notes: List of frequencies in Hz.
        :param durations: List of durations in seconds.
        """
        length = min(len(notes), len(durations))
        for i in range(length):
            self.play_tone(notes[i], durations[i])

    def stop(self):
        """Stops the buzzer output."""
        self.pwm.duty_u16(0)

    def run_test(self):
        """
        Continuous test loop for standalone execution.
        Plays the startup melody, then simulates button press sounds.
        """
        print(f"--- Testing Piezo Buzzer on GP{DEFAULT_BUZZER_PIN} ---")
        
        # Happy Birthday / Standard Startup Melody
        melody_notes = [392, 392, 440, 392, 523, 494, 392, 392, 440, 392, 587, 523]
        melody_durations = [0.3, 0.1, 0.4, 0.4, 0.4, 0.8, 0.3, 0.1, 0.4, 0.4, 0.4, 0.8]
        
        print("Playing startup melody...")
        self.play_melody(melody_notes, melody_durations)
        time.sleep(1)
        
        print("\nPlaying button tone sequence 1...")
        self.play_tone(262, 0.1)
        self.play_tone(659, 0.15)
        self.play_tone(784, 0.2)
        time.sleep(1)
        
        print("Playing button tone sequence 2...")
        self.play_tone(784, 0.2)
        self.play_tone(659, 0.15)
        self.play_tone(262, 0.1)
        
        print("\nTest completed.")
        self.deinit()

    def deinit(self):
        """Safely turns off the PWM and deinitializes the resource."""
        self.stop()
        self.pwm.deinit()


if __name__ == "__main__":
    # Self-test block: Runs directly when this script is executed
    buzzer = Buzzer()
    buzzer.run_test()