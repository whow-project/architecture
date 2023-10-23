# USAGE: python3 aggregate_info.py <dataset>

import os, sys, csv, glob
import numpy as np
import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

def get_summary_list(dataset):

    output_folder = os.path.join('data', dataset, 'v2', 'dirtydata')

    df_fields = pd.read_csv(os.path.join(output_folder, 'Descrizione_campi.csv'), sep=';', skiprows=range(1,7))
    
    type_list = ['Nazionale', 'Regioni', 'Province', 'Comuni']

    for item in type_list:

        df_collection = pd.DataFrame()

        print ('Processing', item)
        for file in (glob.glob(os.path.join(output_folder, item+'*'))):
            if ('static' in file):
                continue
            print (file)
            df_year = pd.read_csv(file, sep=';', dtype=str)
    
            #keep only necessary information
            for col in df_year.columns:
                if col in list(df_fields['Campo']):
                    #df_year.drop([col], axis=1, inplace=True)
                    df_year.loc[:, col] = np.nan

            if (df_collection.empty):
                df_collection = df_year.copy()
            else:
                df_collection = pd.concat([df_collection, df_year], axis=0, ignore_index=True)

            del df_year

        df_collection.drop_duplicates(inplace=True)
        df_collection.reset_index(drop=True, inplace=True)

        newcsvfile = os.path.join(output_folder, item + '_static.csv')
        df_collection.to_csv(newcsvfile, sep=';', index=None, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

        del df_collection


if __name__ == '__main__':

    dset = sys.argv[1]
    get_summary_list(dset)