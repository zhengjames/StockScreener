import pandas as pd
from . import AllConstants as CONSTANT


def a_closer_to_zero_than_b(a, b):
    return abs(a) < abs(b)

'''
 extract most recent list of negative/positive numbers ascending/descending toward zero
 -1,-2,-3,9 ASCENDING will return -1,-2,-3 because it goes toward zero
 return ([], []) if criteria not match otherwise (x_array, y_array)
'''


def extract_most_recent_asc_desc_xy(data_frame, min_num_previous_data=2, pattern=CONSTANT.ASCENDING):

    INVALID_EXTRACTION = ([], [])
    # find longest ascending/descending value that is equal or fewer than num_previous_data
    # this ensures a proper fit for 1 degree linear fit
    for i in range(1, len(data_frame)):
        # breaks descending order
        recent_point = data_frame.x[i - 1]
        old_point = data_frame.x[i]

        # both should be negative if asc or both should be positive if desc
        if ((recent_point >= 0 or old_point >= 0) and pattern == CONSTANT.ASCENDING
                or (recent_point <= 0 or old_point <= 0) and pattern == CONSTANT.DESCENDING):
            return INVALID_EXTRACTION
        # more recent points should be reaching toward 0
        if not a_closer_to_zero_than_b(recent_point, old_point):
            if i == 1 or i < min_num_previous_data:
                return INVALID_EXTRACTION
            # this is the cutoff segment used for fitting
            x = data_frame.x[:i]
            y = data_frame.y[:i]
            return x, y

    return INVALID_EXTRACTION
