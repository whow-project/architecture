# USAGE: python3 split_epe_by_year.py <path/csv_file.csv>

import csv
import sys
import pandas as pd
from tqdm import tqdm

def split_epe_by_year(csv_file):
    print ('Reading', csv_file.name, '...')
    df_csv_large = pd.read_csv(csv_file.name, delimiter=';')
    #csv_data_path = csv_file.name.replace(csv_file.name.split('/')[-1],'')
    
    for yy in tqdm(range(1900, 2022)):
        #print ('Processing year', yy, '...')
        df_years = df_csv_large[df_csv_large['YEAR'] == yy]
        if (not(df_years.empty)):
            df_years.to_csv('data/euring/v2/dirtydata/epe_token_' + str(yy) + '.csv', index=None, sep=';')
        del df_years


if __name__ == '__main__':
    CSVFile = open(str(sys.argv[1]))
    split_epe_by_year(CSVFile)
    



