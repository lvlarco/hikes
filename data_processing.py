import pandas as pd
import numpy as py


class Hike:
    def __init__(self, hike_name):
        self.hike_name = hike_name

    def read_df(self):
        """Reads ACCURATE ALTIMETER app format and drops Triangulation and Accuracy columns"""
        headers = ['Date', 'Time', 'Triangulation', 'Accuracy', 'Value']
        drop_cols = ['Triangulation', 'Accuracy']
        df = pd.read_csv('./files/hike_trails/{}.csv'.format(self.hike_name), names=headers).\
            drop(drop_cols, axis=1)
        return df


def main():
    hike_name1 = 'Blood Mountain'
    hike_name2 = 'East Palisades'

    hike1 = Hike(hike_name1)
    df1 = hike1.read_df()

    hike2 = Hike(hike_name2)
    df2 = hike2.read_df()

    frames = [df1, df2]
    results = pd.concat(frames).reset_index(drop=True)

    print(results)

main()
