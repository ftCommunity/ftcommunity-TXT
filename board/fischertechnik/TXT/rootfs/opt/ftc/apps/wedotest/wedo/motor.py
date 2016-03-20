def processMotorValues(value):
    """Check to make sure motor values are sane."""
    if 0 < value <= 100:
        return value + 27
    elif -100 <= value < 0:
        return value - 27
    return 0
