import shapefile
import zipfile
from os import listdir, path
from pyproj import Proj,Transformer
from shapely.ops import transform
from shapely.geometry import shape
import csv

class place_maker:

    def __init__(self, local_path):
        # data from https://www.istat.it/it/archivio/222527

        self.regions = dict()
        self.provinces = dict()
        self.cities = dict()

        self.project = Transformer.from_proj(
            Proj(init='epsg:32632'),  # source coordinate system
            Proj(init='epsg:4326'))

        zip_files = [path.join(local_path, f) for f in listdir(local_path) if f.endswith('.zip')]
        zip_files = sorted(zip_files, key=lambda x:x[-8:])


        for x in zip_files:
            print("\t Processing", x)
            year = x[:-4][-4:]
            with zipfile.ZipFile(x) as zip_file:
                # COMUNI
                self.COM = self.shp2dict(zip_file, "Com")

                # PROVINCE
                self.PRO = self.shp2dict(zip_file, "Prov")

                # REG
                self.REG = self.shp2dict(zip_file, "Reg")

            self.pack_info(year)


        self.csv_creator(self.regions, "COD_REG", "/data/places/v2/dirtydata/regions.csv")
        self.csv_creator(self.provinces, "COD_PROV", "/data/places/v2/dirtydata/provinces.csv")
        self.csv_creator(self.cities, "PRO_COM_T", "/data/places/v2/dirtydata/cities.csv")


    @staticmethod
    def shp2dict (zipfile, s):
        for member in zipfile.namelist():
            if not member.endswith('/') and s in member:
                if ".shp" in member:
                    shp_file = member
                if ".shx" in member:
                    shx_file = member
                if ".dbf" in member:
                    dbf_file = member
                if ".prj" in member:
                    prj_file = member

        r = shapefile.Reader(shp=zipfile.open(shp_file),
                             shx=zipfile.open(shx_file),
                             dbf=zipfile.open(dbf_file),
                             prj=zipfile.open(prj_file))

        fields = r.fields[1:]
        field_names = [field[0] for field in fields]
        dict_year = []
        for sr in r.shapeRecords():
            atr = dict(zip(field_names, sr.record))
            if s == "Reg":
                geom = ""
            else:
                geom = sr.shape.__geo_interface__

            dict_year.append(dict(geometry=geom, properties=atr))
        return dict_year


    def csv_creator(self, dictionary, key, path):
        listOfDict = list()
        for x in dictionary:
            new_dict= dict()
            new_dict[key] = x
            new_dict.update(dictionary[x])
            listOfDict.append(new_dict)

        with open(path, 'w', newline='',encoding="utf-8") as output_file:
            dict_writer = csv.DictWriter(output_file, listOfDict[0].keys(), delimiter='\t')
            dict_writer.writeheader()
            dict_writer.writerows(listOfDict)

    def pack_info(self, year):
        for x in self.REG:

            reg_cod = str(x['properties']['COD_REG'])
            if len(str(reg_cod)) == 1:
                reg_cod = "0" + str(reg_cod)
            reg_name = str(x['properties']['DEN_REG'])

            if reg_cod not in self.regions:
                self.regions[reg_cod] = dict()
            self.regions[reg_cod]["DEN_REG"] = reg_name


        for x in self.PRO:
            if "-" in x['properties']['DEN_PROV'] and len(x['properties']['DEN_PROV']) == 1:
                #Città metropolitana
                pro_name = str(x['properties']['DEN_CM'])
            else:
                pro_name = str(x['properties']['DEN_PROV'])
            reg_cod = str(x['properties']['COD_REG'])
            if len(str(reg_cod)) == 1:
                reg_cod = "0" + str(reg_cod)

            '''
            # Città metropolitana o provincia
            if str(x['properties']['COD_CM']).strip() != '0':
                pro_cod = str(x['properties']['COD_CM'])
            else:
                pro_cod = str(x['properties']['COD_PROV'])
            '''
            
            pro_cod = str(x['properties']['COD_PROV'])
            if len(str(pro_cod)) == 1:
                pro_cod = "00" + str(pro_cod)
            if len(str(pro_cod)) == 2:
                pro_cod = "0" + str(pro_cod)

            if pro_cod not in self.provinces:
                self.provinces[pro_cod] = dict()

            self.provinces[pro_cod]["YEAR_PROV"] = year

            prov_cen = transform(self.project.transform, shape(x["geometry"])).centroid.wkt
            self.provinces[pro_cod]["CENTROID_PROV"] = prov_cen
            self.provinces[pro_cod]["DEN_PROV"] = pro_name
            self.provinces[pro_cod]["COD_REG"] = reg_cod

        for x in self.COM:
            reg_cod = str(x['properties']['COD_REG'])
            if len(str(reg_cod)) == 1:
                reg_cod = "0" + str(reg_cod)
            prov_cod = str(x['properties']['COD_PROV'])
            if len(str(prov_cod)) == 1:
                prov_cod = "00" + str(prov_cod)
            if len(str(prov_cod)) == 2:
                prov_cod = "0" + str(prov_cod)
            com_cod = str(x['properties']['PRO_COM_T'])
            com_name = str(x['properties']['COMUNE'])

            if com_cod not in self.cities:
                self.cities[com_cod] = dict()
                self.cities[com_cod]["COMUNE_A"] = ""
                self.cities[com_cod]["LANGUAGE_A"] = ""

            self.cities[com_cod]["YEAR_COM"] = year
            poligon = transform(self.project.transform, shape(x["geometry"]))
            com_polygon = poligon.wkt
            com_cen = poligon.centroid.wkt
            self.cities[com_cod]["CENTROID_COM"] = com_cen
            self.cities[com_cod]["POLYGON_COM"] = com_polygon
            self.cities[com_cod]["COMUNE"] = com_name
            self.cities[com_cod]["COD_REG"] = reg_cod
            self.cities[com_cod]["COD_PROV"] = prov_cod
            if x['properties']['COMUNE_A']:
                alt_lang = None
                if reg_cod == "04":
                    alt_lang = "de"
                elif reg_cod == "06":
                    alt_lang = "sl"
                self.cities[com_cod]["COMUNE_A"] = x['properties']['COMUNE_A']
                self.cities[com_cod]["LANGUAGE_A"] = alt_lang

##to run script, uncomment row below and configure the input folder where zip file is placed
#place_maker("/data/")
