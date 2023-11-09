# USAGE: python3 split_bathw_by_yy.py <path/csv_file.csv>

import os, sys, csv
import numpy as np
import pandas as pd
import geopandas as gpd

def split_by_year(csv_file, output_folder):
    print ('Reading', csv_file.name, '...')
    df_csv_large = pd.read_csv(csv_file.name, delimiter=';', dtype=str)
    csv_data_name = (csv_file.name.split('/')[-1]).split('.')[0]
    year_cols = [col.replace('quality','') for col in df_csv_large.columns if 'quality' in col]
    noyears_cols = [col for col in df_csv_large.columns if all(yy not in col for yy in year_cols)]

    df_static = df_csv_large[[col for col in noyears_cols]]
    df_static.to_csv(output_folder + csv_data_name + '_static.csv', index=None, quoting=csv.QUOTE_NONNUMERIC, quotechar='"', sep=';')
    del df_static


    for yy in year_cols:
        print ('Found', yy)
        df_year = pd.DataFrame()
        for col in df_csv_large.columns:
            #bool_year = ('quality' not in col) and ('monitoringCalendar' not in col) and ('management' not in col)
            if ('bathingWaterIdentifier' in col):
                df_year = pd.concat([df_year,df_csv_large[col]], axis=1)
            elif (yy in col):
                df_year = pd.concat([df_year,df_csv_large[col]], axis=1)
                df_year.rename(columns={col:col.replace(yy,'')}, inplace=True)


        df_year.to_csv(output_folder + csv_data_name + '_' + str(yy) + '.csv', index=None, quoting=csv.QUOTE_NONNUMERIC, quotechar='"', sep=';')
        del df_year

def associate_istat_code(file_istat, file_samples):
    '''
	Associate each sampling with the ISTAT code of the nearest city
	'''

    #Read ISTAT shapefile
    print ('Reading ISTAT shapefile ...')
    zipfile = file_istat+"!Limiti01012023/Com01012023/Com01012023_WGS84.shp"
    gdf_shf = gpd.read_file(zipfile)
    gdf_shf = gdf_shf.to_crs(epsg=32632)

    #Read samples file
    df_sample = pd.read_csv(file_samples, sep=';')
    gdf_sample = gpd.GeoDataFrame(df_sample, crs=4326, geometry=gpd.points_from_xy(df_sample.lon, df_sample.lat))
    gdf_sample = gdf_sample.to_crs(epsg=32632)

    print ('Associating records to ISTAT code ...')
	#Join ISTAT and samples geodataframes according to min distance
    gdf_joined = gpd.sjoin_nearest(gdf_sample, gdf_shf)
    gdf_joined = gdf_joined[["countryCode","bathingWaterIdentifier","groupIdentifier","nameText","specialisedZoneType","geographicalConstraint","lon","lat","bwProfileUrl","PRO_COM_T","COMUNE"]]
    diff_record = int(len(df_sample)) - int(len(gdf_joined))
    if (diff_record != 0):
        print ("I'm missing", diff_record, 'records!')
    gdf_joined.rename(columns={"PRO_COM_T": "Istatcode", "COMUNE": "Istatname"}, inplace=True)
    foutname = file_samples.split('.')[0]+'_withISTATcode.csv'
    gdf_joined.to_csv(foutname, sep=';', index=None)
    print ('Created', foutname)


if __name__ == '__main__':

    outdir = os.path.join("data","bathw","v2","dirtydata")
    file_comuni_istat = 'istat/Limiti01012023.zip'

    CSVFile = str(sys.argv[1])
    split_by_year(open(CSVFile), outdir)
    file_output = os.path.join(outdir, CSVFile.split('/')[-1].split('.')[0]+'_static.csv')
    associate_istat_code(file_comuni_istat, file_output)





