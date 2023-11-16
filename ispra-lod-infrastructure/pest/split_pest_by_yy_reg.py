# USAGE: python3 split_pest_by_yy_reg.py <path/csv_file.csv>

import os, sys, csv, glob
import numpy as np
import pandas as pd

def split_by_year_and_region(csv_file, output_folder):
    print ('Reading', csv_file.name, '...')
    df_csv_large = pd.read_csv(csv_file.name, delimiter=';', dtype=str)
    csv_data_name = (csv_file.name.split('/')[-1]).split('.')[0]
    year_cols = [col for col in df_csv_large.columns if 'anno' in col]

    regions = np.unique(df_csv_large['regione'])

    with open(os.path.join("pest", "regions.txt"), "w") as regout:
        for reg in regions:
            print (reg.replace(' ','').replace('/','').replace("'",""), file=regout)

    for yy in (range(1900, 2022)):
        df_years = df_csv_large[df_csv_large[year_cols[0]] == str(yy)]
        if (not(df_years.empty)):
            print ('Processing year', yy, '...')
            for reg in regions:
                df_reg = df_years[df_years['regione']==reg]
                if (not(df_reg.empty)):
                    print ('Processing region', reg, '...')
                    regname = reg.replace(' ','').replace('/','').replace("'","")
                    df_reg.to_csv(output_folder + csv_data_name + '_' + regname + '_' + str(yy) + '.csv', index=None, quoting=csv.QUOTE_NONNUMERIC, quotechar='"', sep=';', encoding='utf-8-sig')
                del df_reg
        del df_years



if __name__ == '__main__':

    outdir = "data/pest/v2/dirtydata/"

    CSVFile = open(str(sys.argv[1]))
    split_by_year_and_region(CSVFile, outdir)





