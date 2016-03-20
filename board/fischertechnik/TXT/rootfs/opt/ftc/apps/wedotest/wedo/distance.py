from bisect import bisect_left, bisect_right

# data from distance sensor -> real measure in cms under ideal conditions (no side object, perpendicular wall)
RAW_MEASURES = {
    210: 46,
    208: 39,
    207: 34,
    206: 32,
    205: 30.5,
    204: 29,
    203: 27,
    202: 26,
    201: 25,
    200: 24.5,
    199: 23.5,
    198: 22.5,
    197: 22,
    196: 21.5,
    195: 20,
    194: 19.5,
    193: 18,
    192: 17.5,
    191: 17,
    180: 15,
    170: 13,
    160: 12.5,
    150: 11,
    140: 10.5,
    130: 10,
    120: 9.5,
    100: 7.5,
    71: 6.5,
    70: 6,
    69: 5.3,
    68: 0}

RAW_MEASURES_KEYS = sorted(list(RAW_MEASURES))


def interpolate_distance_data(raw):
    left_index = bisect_left(RAW_MEASURES_KEYS, raw) - 1
    if left_index < 0:
        left_index = 0
    right_index = left_index if left_index == len(RAW_MEASURES_KEYS) - 1 else left_index + 1

    left = RAW_MEASURES_KEYS[left_index]
    if left > raw:
        return RAW_MEASURES[RAW_MEASURES_KEYS[left_index]]

    right = RAW_MEASURES_KEYS[right_index]
    mright = RAW_MEASURES[right]
    mleft = RAW_MEASURES[left]
    addup = ((raw - left) / (right - left)) * (mright - mleft) if mright != mleft else 0
    return mleft + addup
