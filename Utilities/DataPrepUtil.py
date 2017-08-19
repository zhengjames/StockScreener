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
    i = 1
    while i < len(data_frame):
        # breaks descending order
        recent_point = data_frame.x[i - 1]
        old_point = data_frame.x[i]

        # more recent points should be reaching toward 0 for first two points
        if not a_closer_to_zero_than_b(recent_point, old_point):
            if i == 1 or i < min_num_previous_data:
                return INVALID_EXTRACTION

        # if ASC both should be negative  or if DESC both should be positive
        if not ((pattern == CONSTANT.ASCENDING
                 and recent_point <= 0 and old_point <= 0 )
                or (pattern == CONSTANT.DESCENDING
                    and recent_point >= 0 and old_point >= 0 )):
            #no progress, going wrong direction, will not follow desired direction to predict
            if i == 1:
                return INVALID_EXTRACTION
            break
        i += 1
    # this is the cutoff segment used for fitting
    x = data_frame.x[:i]
    y = data_frame.y[:i]
    return x, y


'''lower case because it matches python naming standards...'''
def normalize_col_names(df):
    #first column is always renamed to 'date'
    df_list = df.columns.tolist()
    df_list[0] = 'date'
    df.columns = df_list
    #to lower case all column names
    df.rename(columns = lambda col_name: col_name.lower(), inplace=True)

'''quandl returns date in asc format like
    2017-07-01
    2017-07-02
    2017-07-03
    but this function makes it in desc order
    2017-07-03
    2017-07-02
    2017-07-01'''
def make_asc_date_order_quandl(df):
    return pd.DataFrame(df.values[::-1], df.index, df.columns)

def segmentate_df_by_ticker(df):
    ''' {FB: 1; FB:2; TSLA:1; TSLA:2}
        to
        {
            FB: {1,2}
            TSLA: {1,2}
        }
    '''
    tickers_to_df_dict = {}
    #strategy iterate through each row
    if df is None or len(df.index) < 2:
        return df


    groupby_ticker = df.groupby('ticker')
    for a_group in groupby_ticker:
        #0th index is the group by 'ticker' and 1st index is the dataframe
        #reset index turns 140,141,142 to 0,1,2...
        tickers_to_df_dict[a_group[0]] = a_group[1].reset_index(drop=True)

    return tickers_to_df_dict