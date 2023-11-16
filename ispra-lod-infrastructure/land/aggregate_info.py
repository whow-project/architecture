# USAGE: python3 aggregate_info.py <dataset>

import os, sys, csv, glob, math
import numpy as np
import pandas as pd
import warnings
from pandas.errors import SettingWithCopyWarning

warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
warnings.simplefilter(action='ignore', category=FutureWarning)

def get_summary_list(dataset):

    output_folder = os.path.join('data', dataset, 'v2', 'dirtydata')

    skiprange=[]
    if (dataset == 'soilc'):
        skiprange = range(1,7)
    
    df_fields = pd.read_csv(os.path.join(output_folder, 'Descrizione_campi.csv'), sep=';', skiprows=skiprange)
    
    type_list = ['Nazionale', 'Regioni', 'Province', 'Comuni', 'Citta metropolitana']
    type_dict_soilc = {'Nazionale': 'COD', 'Regioni': 'COD_REG', 'Province': 'COD_PRO', 'Comuni': 'PRO_COM'}

    for item in type_list:

        df_collection_temp = pd.DataFrame()

        filelist = glob.glob(os.path.join(output_folder, item+'*'))
        if len(filelist) == 0: continue

        print ('Processing', item)
        for file in filelist:
            if ('static' in file):
                continue
            print (file)
            df_year = pd.read_csv(file, sep=';', dtype=str)
            #keep only necessary information
            for col in df_year.columns:
                if col in list(df_fields['Campo']):
                    #df_year.drop([col], axis=1, inplace=True)
                    for ii in range(len(df_year[col])):
                        if not pd.isna(df_year[col][ii]):
                            df_year.loc[ii, col] = 1 #Flag for not nan value
 
            if (df_collection_temp.empty):
                df_collection_temp = df_year.copy()
            else:
                df_collection_temp = pd.concat([df_collection_temp, df_year], axis=0, ignore_index=True, sort=False)

            del df_year

        if df_collection_temp.empty:
            continue
        
        df_collection = pd.DataFrame()
        
        keyfieldname = 'IdOST_Origine'
        if (dataset == 'soilc'):
            keyfieldname = type_dict_soilc[item]

        #If one value at least is non nan, keep it
        for istatcode in df_collection_temp[keyfieldname].unique():
            df_temp = df_collection_temp[df_collection_temp[keyfieldname] == istatcode]
            for col in df_temp.columns:
                if col in list(df_fields['Campo']):
                    if df_temp[col].notnull().values.any():
                        df_temp.loc[:, col] = 1
            df_temp = df_temp.drop_duplicates()
            df_temp.reset_index(drop=True, inplace=True)

            if (df_collection.empty):
                    df_collection = df_temp.copy()
            else:
                df_collection = pd.concat([df_collection, df_temp], axis=0, ignore_index=True, sort=False)
            #df_collection.drop_duplicates(inplace=True)
            df_collection.reset_index(drop=True, inplace=True)

            del df_temp

        newcsvfile = os.path.join(output_folder, item + '_static.csv')
        df_collection.to_csv(newcsvfile, sep=';', index=None, quotechar='"', quoting=csv.QUOTE_NONNUMERIC, encoding='utf-8-sig')

        del df_collection


if __name__ == '__main__':

    dset = sys.argv[1]
    get_summary_list(dset)