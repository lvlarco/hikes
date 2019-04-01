import pandas as pd
import numpy as py
from datetime import datetime, date

# headers
dates, time, triangulation, accuracy, elevation = 'Date', 'Time', 'Triangulation', 'Accuracy', 'Altitude'
elevation_gain = 'Elevation Gain'
time_change = 'Delta Time'


class Hike:
    def __init__(self, hike_name, highest_altitude=None):
        self.hike_name = hike_name
        self.highest_altitude = highest_altitude

    def read_df(self):
        """Reads ACCURATE ALTIMETER app format and drops Triangulation and Accuracy columns"""
        headers = [dates, time, triangulation, accuracy, elevation]
        drop_cols = [triangulation, accuracy]
        df = pd.read_csv('./files/hike_trails/{}.csv'.format(self.hike_name), names=headers).\
            drop(drop_cols, axis=1)
        return df

    @staticmethod
    def calc_elevation_gain(df):
        """Calculates ['Elevation Gain'] column in dataframe"""
        initial_elevation = df.iloc[0][elevation]
        df[elevation_gain] = df[elevation] - initial_elevation
        return df

    @staticmethod
    def calc_time_change(df):
        """Calculates ['Time Change'] column in dataframe. Also converts [date] and [time] into datetime type"""
        df[time] = pd.to_datetime(df[time])
        initial_time = df[time].iloc[0]
        df[time_change] = df[time] - initial_time
        df[time] = df[time].dt.time
        df[dates] = pd.to_datetime(df[dates]).dt.date
        return df

    def corrected_elevation(self, df):
        """Calculates a corrected elevation value if a highest elevation point is provided"""
        if self.highest_altitude:
            print 'Correcting altitude values'
            max_elevation = df[elevation].max()
            df[elevation] = (self.highest_altitude - max_elevation) + df[elevation]
        return df


def main():
    hike_name1 = 'Blood Mountain'
    hike_name2 = 'East Palisades'

    hike1 = Hike(hike_name1, highest_altitude=1355)
    df1 = hike1.read_df()
    df1 = hike1.corrected_elevation(df1)
    df1 = hike1.calc_elevation_gain(df1)
    hike1.calc_time_change(df1)
    print(df1)

    hike2 = Hike(hike_name2)
    df2 = hike2.read_df()
    df2 = hike2.calc_elevation_gain(df2)

    frames = [df1, df2]
    results = pd.concat(frames, sort=False).reset_index(drop=True)

    # print(results)

main()
