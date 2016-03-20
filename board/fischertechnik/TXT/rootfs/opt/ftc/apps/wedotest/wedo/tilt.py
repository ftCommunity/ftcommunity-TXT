FLAT, TILT_FORWARD, TILT_LEFT, TILT_RIGHT, TILT_BACK = range(5)

def process_tilt(raw_tilt_value):
    """Use a series of elif/value-checks to process the tilt
    sensor data."""
    if 10 <= raw_tilt_value <= 40:
        return TILT_BACK
    elif 60 <= raw_tilt_value <= 90:
        return TILT_RIGHT
    elif 170 <= raw_tilt_value <= 190:
        return TILT_FORWARD
    elif 220 <= raw_tilt_value <= 240:
        return TILT_LEFT
    return FLAT
