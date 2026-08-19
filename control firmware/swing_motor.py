"""
DESCRIPTION:
Class-based Hardware Driver for Brushed DC Motor (Swing Mode)
Designed for Cytron MOTION 2350 Pro (M1 Terminal: GP8 & GP9).

AUTHOR : Adapted for Lab Style Architecture
"""

from machine import Pin, PWM
import time

# --- Pin & Default Configurations ---
# If you want to change pin, you can call 'motor = SwingMotor(pin_a=14, pin_b=15)'
MOTOR_A_PIN = 8
MOTOR_B_PIN = 9

DEFAULT_POWER_PERCENT = 50
DEFAULT_PWM_FREQ_HZ = 20_000
DEFAULT_SWING_FREQ_HZ = 1.0
REVERSAL_DEAD_TIME_MS = 20 #Dead time before switch direction


class SwingMotor:
    def __init__(self, pin_a=MOTOR_A_PIN, pin_b=MOTOR_B_PIN, pwm_freq=DEFAULT_PWM_FREQ_HZ):
        """Initializes PWM channels for motor driver pins."""
        self.motor_a = PWM(Pin(pin_a, Pin.OUT))
        self.motor_b = PWM(Pin(pin_b, Pin.OUT))
        self.motor_a.freq(pwm_freq)
        self.motor_b.freq(pwm_freq)
        self.stop()

    @staticmethod
    def percent_to_duty(percent):
        """Converts percentage (0-100%) to 16-bit PWM duty cycle (0-65535)."""
        percent = max(0, min(100, percent))
        return percent * 65535 // 100

    def forward(self, percent=DEFAULT_POWER_PERCENT):
        """Drives the motor forward at specified power percentage."""
        duty = self.percent_to_duty(percent)
        self.motor_b.duty_u16(0)
        self.motor_a.duty_u16(duty)

    def reverse(self, percent=DEFAULT_POWER_PERCENT):
        """Drives the motor in reverse at specified power percentage."""
        duty = self.percent_to_duty(percent)
        self.motor_a.duty_u16(0)
        self.motor_b.duty_u16(duty)

    def stop(self):
        """Stops the motor completely."""
        self.motor_a.duty_u16(0)
        self.motor_b.duty_u16(0)

    def swing_cycle(self, power=DEFAULT_POWER_PERCENT, freq=DEFAULT_SWING_FREQ_HZ):
        """
        Executes ONE complete forward-reverse swing cycle.
        Useful when called from main loop without infinite locking.
        """
        half_period_ms = int(500 / freq)
        drive_time_ms = half_period_ms - REVERSAL_DEAD_TIME_MS
        
        if drive_time_ms <= 0:
            raise ValueError("Reversal dead-time is too long for this frequency")

        # Forward swing
        self.forward(power)
        time.sleep_ms(drive_time_ms)
        self.stop()
        time.sleep_ms(REVERSAL_DEAD_TIME_MS)

        # Reverse swing
        self.reverse(power)
        time.sleep_ms(drive_time_ms)
        self.stop()
        time.sleep_ms(REVERSAL_DEAD_TIME_MS)

    def run_test(self, power=DEFAULT_POWER_PERCENT, freq=DEFAULT_SWING_FREQ_HZ):
        """Continuous test loop for standalone execution."""
        print(f"--- Starting Motor Swing Test ---")
        print(f"Pins: GP{MOTOR_A_PIN} & GP{MOTOR_B_PIN}")
        print(f"Swing Frequency: {freq} Hz | Power: {power}%")
        print("Press Ctrl+C to stop.\n")

        try:
            while True:
                self.swing_cycle(power, freq)
        except KeyboardInterrupt:
            print("\nTest Stopped by User.")
        finally:
            self.deinit()

    def deinit(self):
        """Safely stops and releases hardware PWM resources."""
        self.stop()
        self.motor_a.deinit()
        self.motor_b.deinit()
        print("Motor Hardware Deinitialized.")


if __name__ == "__main__":
    # Self-test block: Runs directly when this script is executed
    motor = SwingMotor()
    motor.run_test()