# USAGE: python3 split_pest_by_year.py <path/csv_file.csv>

import sys, csv
import numpy as np
import pandas as pd

def split_by_year_and_region(csv_file):
    print ('Reading', csv_file.name, '...')
    df_csv_large = pd.read_csv(csv_file.name, delimiter=';', dtype=str)
    csv_data_name = (csv_file.name.split('/')[-1]).split('.')[0]
    year_cols = [col for col in df_csv_large.columns if 'anno' in col]

    regions = np.unique(df_csv_large['regione'].str.replace(' ','').str.replace('/','').str.replace("'",""))

    for yy in (range(1900, 2022)):
        df_years = df_csv_large[df_csv_large[year_cols[0]] == str(yy)]
        if (not(df_years.empty)):
            print ('Processing year', yy, '...')
            for reg in regions:
                df_reg = df_years[df_years['regione']==reg]
                df_reg.to_csv('data/pest/v2/dirtydata/' + csv_data_name + '_' + reg + '_' + str(yy) + '.csv', index=None, quoting=csv.QUOTE_NONNUMERIC, quotechar='"', sep=';')
                del df_reg
        del df_years


if __name__ == '__main__':
    CSVFile = open(str(sys.argv[1]))
    split_by_year_and_region(CSVFile)




