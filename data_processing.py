from os import listdir, path
import pandas as pd
import numpy as py
from datetime import datetime, date

# headers
dates, time, triangulation, accuracy, elevation = 'Date', 'Time', 'Triangulation', 'Accuracy', 'Altitude'
elevation_gain = 'Elevation Gain'
time_change = 'Delta Time'
names = 'Name'
timestamp = 'Timestamp'


class Hike:
    def __init__(self, hike_name, highest_altitude=None):
        self.hike_name = hike_name
        self.highest_altitude = highest_altitude

    def read_hike(self):
        """Reads ACCURATE ALTIMETER app format and drops Triangulation and Accuracy columns"""
        headers = [dates, time, triangulation, accuracy, elevation]
        drop_cols = [triangulation, accuracy]
        df = pd.read_csv('./files/hike_trails/{}.csv'.format(self.hike_name), names=headers).drop(drop_cols, axis=1)
        df['Timestamp'] = pd.to_datetime(df[dates] + ' ' + df[time])
        df.insert(0, names, self.hike_name)
        return df

    @staticmethod
    def resample_df(df, minutes):
        """Resample data to specific timestamp
        :param df: dataframe to resample
        :param minutes: resample size in minutes
        """
        minutes_str = '{}T'.format(minutes)
        resample_df = df.resample(minutes_str).mean()
        return resample_df

    @staticmethod
    def calc_elevation_gain(df):
        """Calculates ['Elevation Gain'] column in dataframe"""
        initial_elevation = df.iloc[0][elevation]
        df[elevation_gain] = df[elevation] - initial_elevation
        return df

    @staticmethod
    def calc_time_change(df):
        """Calculates ['Time Change'] column in dataframe. Also converts [date] and [time] into datetime type"""
        initial_time = df.index.min()
        df[time_change] = df.index - initial_time
        df[time_change] = pd.to_datetime(df[time_change]).dt.strftime('%H:%M:%S')
        return df

    def corrected_elevation(self, df):
        """Calculates a corrected elevation value if a highest elevation point is provided"""
        if self.highest_altitude:
            print 'Correcting altitude values'
            max_elevation = df[elevation].max()
            df[elevation] = (self.highest_altitude - max_elevation) + df[elevation]
        else:
            print 'No corrected altitude provided for {}'.format(self.hike_name)
        return df

    def determine_name_date(self, df):
        """Extracts date of hike from CSV and returns dictionary"""
        unique_date = pd.unique(df[dates])
        date_dict = {'name': self.hike_name,
                     'date': unique_date
                     }
        return date_dict

    def read_fitbit(self, activity, date):
        """Reads CSV file from Fitbit's activities"""
        df = pd.read_csv('./files/fitbit_data/{0}_{1}.csv'.format(activity, date), index_col=0)
        df['Date'] = date
        df['Timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        return df

    def beg_end_time(self):
        """Finds beginning and end timestamps of df"""
        df = self.read_hike()
        # print df['Timestamp']# = pd.to_datetime(df['Timestamp'])
        beg_time = df['Timestamp'].min()
        end_time = df['Timestamp'].max()
        return beg_time, end_time

    @staticmethod
    def filter_boundaries(df, bound1, bound2):
        """Filters datatime by boundaries"""
        return_df = df.loc[bound1 < df['Timestamp']]
        return_df = return_df.loc[df['Timestamp'] < bound2]
        return return_df


def files_directory():
    """Creates a list of all files in directory and returns the name for all hikes in ./files/hike_trails"""
    path_dir = './files/hike_trails'
    hikes_list = listdir(path_dir)
    new_list = []
    for hikes in hikes_list:
        hike_name = path.splitext(hikes)[0]
        new_list.append(hike_name)
    return new_list


def concat_dataframes(*args):
    """Concatenates all dataframes into one df"""
    result_df = pd.concat(args, sort=False).reset_index(drop=True)
    return result_df


def main():
    all_hikes_list = files_directory()
    result_df = pd.DataFrame()
    for hike in all_hikes_list:
        print('Processing: {}'.format(hike))
        H = Hike(hike)

        #New try
        headers = [dates, time, triangulation, accuracy, elevation]
        drop_cols = [triangulation, accuracy]
        hike_df = pd.read_csv('./files/hike_trails/{}.csv'.format(hike), names=headers).drop(drop_cols, axis=1)
        hike_df['Timestamp'] = pd.to_datetime(hike_df[dates] + ' ' + hike_df[time])
        resample_df = hike_df.set_index(hike_df['Timestamp']).resample('5T').mean()
        resample_df = H.corrected_elevation(resample_df)
        resample_df = H.calc_elevation_gain(resample_df)
        resample_df = H.calc_time_change(resample_df)
        resample_df.insert(0, names, hike)

        # #Hikes data formatting
        # df = init_hike.read_hike()
        # cols = df.columns.tolist()
        # cols.insert(0, cols.pop(cols.index('Timestamp')))
        # df = df.reindex(columns=cols).set_index(df['Timestamp']).resample('5T').mean()
        # print df
        # df = init_hike.corrected_elevation(df)
        # df = init_hike.calc_elevation_gain(df)
        # df = init_hike.calc_time_change(df)

        # #Fitbit data formatting
        # activity = 'steps'
        # hike_date = '2018-04-11'
        # date_dict = init_hike.determine_name_date(df)
        # fitbit_df = init_hike.read_fitbit(activity, hike_date)
        # beg_time, end_time = init_hike.beg_end_time()
        # fitbit_df = init_hike.filter_boundaries(fitbit_df, beg_time, end_time)

        result_df = result_df.append(resample_df)
    file_name = 'complete_hikes_list'
    save_path = './files/{}.csv'.format(file_name)
    print("Saving complete list to '{}'".format(save_path))
    result_df.to_csv(save_path)
    # print result_df

main()
