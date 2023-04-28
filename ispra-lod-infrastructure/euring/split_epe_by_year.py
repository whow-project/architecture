# USAGE: python3 split_epe_by_year.py <path/csv_file.csv>

import csv
import sys
import pandas as pd
from tqdm import tqdm

def split_epe_by_year(csv_file):
    print ('Reading', csv_file.name, '...')
    df_csv_large = pd.read_csv(csv_file.name, delimiter=';')
    csv_data_name = (csv_file.name.split('/')[-1]).split('.')[0]
    year_cols = [col for col in df_csv_large.columns if 'YEAR' in col]

    
    for yy in (range(1900, 2022)):
        df_years = df_csv_large[df_csv_large[year_cols[0]] == yy]
        if (not(df_years.empty)):
            print ('Processing year', yy, '...')
            df_years.to_csv('data/euring/v2/dirtydata/' + csv_data_name + '_' + str(yy) + '.csv', index=None, sep=';')
        del df_years


if __name__ == '__main__':
    CSVFile = open(str(sys.argv[1]))
    split_epe_by_year(CSVFile)
    



