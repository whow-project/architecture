# USAGE: python3 aggregate_info.py

import os, csv, glob
import pandas as pd


def get_subst_list(output_folder):

    regions = []
    with open('regions.txt') as file:
        for line in file:
           regions.append(line) 

    for reg in regions:
        '''
        Collects stations and substances from all years and makes a unique stat-subst csv
        '''
        print ('Getting subs list for', reg.strip(), '...')

        df_collection = pd.DataFrame()

        reg_key = "stazioni_sostanze*"+ reg.strip() + "*"

        for file in sorted(glob.glob(output_folder+reg_key)):

            print (file)
            df_year = pd.read_csv(file, sep=';', dtype=str)
            if (df_collection.empty):
                df_collection = df_year.copy()
            else:
                df_collection = pd.concat([df_collection, df_year], axis=0, ignore_index=True)

            del df_year

        df_collection = df_collection.drop(list(df_collection.columns[11:]), axis=1)
        df_collection = df_collection.drop(['anno'], axis=1)
        df_collection.drop_duplicates(inplace=True)
        df_collection.reset_index(drop=True, inplace=True)

        newcsvfile = os.path.join(output_folder, 'subst_static_' + reg.strip() + '.csv')
        df_collection.to_csv(newcsvfile, sep=';', index=None, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

        del df_collection


def get_staz_list(output_folder):

    regions = []
    with open('regions.txt') as file:
        for line in file:
           regions.append(line) 

    for reg in regions:
        '''
        Collects stations and substances from all years and makes a unique stat-subst csv
        '''
        print ('Getting stat list for', reg.strip(), '...')

        df_collection = pd.DataFrame()

        reg_key = "stazioni*"+ reg.strip() + "*"

        for file in sorted(glob.glob(output_folder+reg_key)):

            if 'sostanze' in file:
                continue

            print (file)
            df_year = pd.read_csv(file, sep=';', dtype=str)
            if (df_collection.empty):
                df_collection = df_year.copy()
            else:
                df_collection = pd.concat([df_collection, df_year], axis=0, ignore_index=True)

            del df_year

        df_collection = df_collection.drop(list(df_collection.columns[11:]), axis=1)
        df_collection = df_collection.drop(['anno'], axis=1)
        df_collection.drop_duplicates(inplace=True)
        df_collection.reset_index(drop=True, inplace=True)

        newcsvfile = os.path.join(output_folder, 'stat_static_' + reg.strip() + '.csv')
        df_collection.to_csv(newcsvfile, sep=';', index=None, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

        del df_collection



if __name__ == '__main__':

    outdir = "data/pest/v2/dirtydata/"
    get_staz_list(outdir)    
    get_subst_list(outdir)    