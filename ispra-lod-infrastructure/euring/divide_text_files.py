# USAGE: divide_text_files <path/csv_file.csv> <N>

import sys
import numpy as np
import pandas as pd

def divide_text_files(csv_file, N):
    print ('Reading', csv_file.name, '...')
    df_csv_large = pd.read_csv(csv_file.name, delimiter=';')
    #csv_data_path = csv_file.name.replace(csv_file.name.split('/')[-1],'')
    arr_df = np.array_split(df_csv_large,N)
    nn = 0

    for df_N in arr_df:
        df_N.to_csv('data/euring/v2/dirtydata/epe_organism_' + str(nn+1) + '.csv', index=None, sep=';')
        nn += 1
        del df_N


if __name__ == '__main__':
    CSVFile = open(str(sys.argv[1]))
    divide_text_files(CSVFile, int(sys.argv[2]))
    



