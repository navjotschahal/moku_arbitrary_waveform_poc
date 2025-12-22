import time
from moku.instruments import LogicAnalyzer

from config_uitl import get_env_str

MOKU_IP = get_env_str("MOKU_IP", "169.254.77.89")   # your device ip address


# Connect Logic Analyzer / Pattern Generator
la = LogicAnalyzer(MOKU_IP, force_connect=True)

try:
    # --- Configure Pattern Generator 1 patterns ---
    # Pin 1 always HIGH, Pin 1 always LOW (we'll swap between these)
    pattern_high = [{"pin": 1, "pattern": [1] * 1024}]   # logic high
    pattern_low  = [{"pin": 1, "pattern": [0] * 1024}]   # logic low

    # Route digital pin 1 to Pattern Generator 1
    la.set_pin_mode(pin=1, state="PG1")   # PG1 = Pattern Generator 1 output

    # 1) Set pin HIGH
    la.set_pattern_generator(1, patterns=pattern_high, divider=8)
    print("Pin 1 = HIGH (3.3 V)")
    time.sleep(2)

    # 2) Set pin LOW
    la.set_pattern_generator(1, patterns=pattern_low, divider=8)
    print("Pin 1 = LOW (0 V)")
    time.sleep(2)

    # 3) Back to HIGH again
    la.set_pattern_generator(1, patterns=pattern_high, divider=8)
    print("Pin 1 = HIGH again")

    # Leave it high for a while
    time.sleep(5)

finally:
    la.relinquish_ownership()