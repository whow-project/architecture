import os
import pandas as pd
import geopandas as gpd
import contextily as cx
from matplotlib import pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar

def aggregate_files(dpath, foutput):

	'''
	Aggregate regional csv files into a single csv file
	'''
	print ('Aggregating csv files ...')
	df_sample = pd.DataFrame()
	for file in os.listdir(dpath):
		print ('Reading', file)
		df_sample = pd.concat([df_sample,pd.read_csv(os.path.join(dpath,file), skiprows=[1], sep=';')], axis=0)
	df_sample = df_sample.loc[:, ~df_sample.columns.str.contains('^Unnamed')]
	df_sample = df_sample.rename(columns=lambda x: x.strip())
	df_sample.to_csv(foutput, sep=';', index=None)


def associate_istat_and_seas(file_istat, file_seas, file_samples):

	'''
	Associate each sampling with the ISTAT code of the nearest city
	'''

	#Read ISTAT shapefile
	zipfile = file_istat+"!Limiti01012020/Com01012020/Com01012020_WGS84.shp"
	gdf_shf = gpd.read_file(zipfile)
	gdf_shf = gdf_shf.to_crs(epsg=32632)

	#Read Med Sea file
	medzipfile = file_seas+"!med_only.shp"
	gdf_sea = gpd.read_file(medzipfile)
	gdf_sea_ita = gdf_sea[gdf_sea['Country']=='IT']
	gdf_sea_ita = gdf_sea_ita.to_crs(epsg=32632)
	sea_dict = {'MAD': 'Adriatic Sea', 'MIC': 'Ionian Sea', 'MWE': 'Western Mediterranean Sea'}
	gdf_sea_ita['Seaname'] = gdf_sea_ita['Subregion'].map(sea_dict)

	#Read samples file
	df_sample = pd.read_csv(file_samples, sep=';')
	gdf_sample = gpd.GeoDataFrame(df_sample, crs=4326, geometry=gpd.points_from_xy(df_sample.LONG, df_sample.LAT))
	gdf_sample = gdf_sample.to_crs(epsg=32632)

	print ('Associating records to ISTAT code ...')
	#Join ISTAT and samples geodataframes according to min distance
	gdf_joined=gpd.sjoin_nearest(gdf_sample, gdf_shf)
	try:
		gdf_joined= gdf_joined.drop(['index_right','COD_RIP', 'COD_REG', 'COD_PROV', 'COD_CM', 'COD_UTS', 'PRO_COM', 'COMUNE', 'COMUNE_A', 'CC_UTS', 'Shape_Area', 'Shape_Leng', 'geometry'], axis=1)
	except KeyError:
		gdf_joined= gdf_joined.drop(['index_right','COD_RIP', 'COD_REG', 'COD_PROV', 'COD_CM', 'COD_UTS', 'PRO_COM', 'COMUNE', 'COMUNE_A', 'CC_UTS', 'SHAPE_AREA','SHAPE_LENG', 'SHAPE_LEN', 'geometry'], axis=1)
	diff_record = int(len(df_sample)) - int(len(gdf_joined))
	if (diff_record != 0):
		print ("I'm missing", diff_record, 'records!')
	foutname = file_samples.split('.')[0]+'_withISTATcode.csv'
	gdf_joined.to_csv(foutname, sep=';', index=None)
	print ('Created', foutname)


	print ('Associating records to Seas ...')
	#Join Seas and joined geodataframes according to min distance
	gdf_joined.reset_index(inplace=True)
	gdf_joined = gpd.GeoDataFrame(gdf_joined, crs=4326, geometry=gpd.points_from_xy(gdf_joined.LONG, gdf_joined.LAT))
	gdf_joined = gdf_joined.to_crs(epsg=32632)
	#Join geodataframes according to min distance
	gdf_joined_sea=gpd.sjoin_nearest(gdf_joined, gdf_sea_ita)
	gdf_joined_sea= gdf_joined_sea.drop(['Country', 'Area_km2', 'Type', 'geometry', 'index_right', 'Subregion'], axis=1)
	diff_record = int(len(gdf_joined)) - int(len(gdf_joined_sea))
	if (diff_record != 0):
		print ("I'm missing", diff_record, 'records!')
	foutname = file_samples.split('.')[0]+'_withISTATcode_withSeas.csv'
	gdf_joined_sea.to_csv(foutname, sep=';', index=None)
	print ('Created', foutname)

	#Plot map
	gdf_shf['coords'] = gdf_shf['geometry'].apply(lambda x: x.representative_point().coords[:])
	gdf_shf['coords'] = [coords[0] for coords in gdf_shf['coords']]
	fig, ax = plt.subplots(figsize=[10,10])
	#To show cities polygons:
	#gdf_shf.plot(ax=ax,facecolor='gray',alpha=.2,edgecolor='black',lw=2)
	#To show ISTAT codes inside polygons:
	#gdf_shf.apply(lambda x: ax.annotate(text=x['PRO_COM'], xy=x.geometry.centroid.coords[0], ha='center'), axis=1);
	gdf_sample.plot(ax=ax, label='Sampling points', color='blue')
	cx.add_basemap(ax, crs=gdf_shf.crs, source=cx.providers.Stamen.TonerLite, zoom=6)
	#Scale bar
	ax.add_artist(ScaleBar(dx=1, location='lower right', color='white', sep=10, font_properties={'size': 0},
						box_color='white', box_alpha=0.0, length_fraction=0.2))
	ax.add_artist(ScaleBar(dx=1, location='lower right', color='black', sep=10, font_properties={'size': 0},
						box_color='white', box_alpha=0.0, length_fraction=0.1))
	ax.add_artist(ScaleBar(dx=1, location='lower right', color=None, sep=10, height_fraction=0.001,
						box_color='white', box_alpha=0.0, length_fraction=0.2))
	ax.tick_params(labelsize=0)
	ax.set_yticklabels([])
	ax.set_xticklabels([])
	ax.grid(True)
	plt.legend(loc='upper right')
	plt.draw()
	plt.show()
	plt.savefig('ostreopsis/map.png')


if __name__ == '__main__':

	#Modify these paths according to file location and desired output
	data_path = 'data/ostreopsis/csv' #path with original csv files
	file_output = 'data/ostreopsis/v2/dirtydata/Ostreopsis_Ovata_AllRegions.csv'
	file_comuni_istat = 'istat/Limiti01012020.zip'
	file_mari = 'ostreopsis/med_only.zip'

	aggregate_files(data_path, file_output)
	associate_istat_and_seas(file_comuni_istat, file_mari, file_output)