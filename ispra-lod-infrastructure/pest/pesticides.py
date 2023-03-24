from builtins import staticmethod
import os
import re
import pandas as pd
import datetime as dt
from pyrml import TermUtils
from triplification import Triplifier, UtilsFunctions
from kg_loader import KnowledgeGraphLoader


UNIT_OF_MEASURES_STAZ = None
UNIT_OF_MEASURES_IND = None


class Functions():

    @staticmethod
    def measures_collection_title(row):
        return row["COLL_TYPE"].title()

    @staticmethod
    def station_model_uri(row, dataset):
        return "https://w3id.org/italia/env/ld/" + dataset + "/platformmodel/" + Functions.station_model_id(row, dataset)
    
    @staticmethod
    def station_model_id(row, dataset):
        if dataset == 'rmn':
            if "STAT_CODE" in row: 
                return TermUtils.irify(row["STAT_CODE"]) + "_" + TermUtils.irify(row["NETWORK"]) + "_" + TermUtils.irify(row["TYPE_EN"])
            elif "MODEL" in row:
                return TermUtils.irify(row["MODEL"]) + "_" + TermUtils.irify(row["NETWORK"]) + "_" + TermUtils.irify(row["TYPE_EN"])
        else:
            return TermUtils.irify(row["MODEL"]) + "_" + TermUtils.irify(row["TYPE_EN"])
        
    @staticmethod    
    def time_interval(row):
        return re.sub("[^0-9]", "", row["START"]) + "_" + re.sub("[^0-9]", "", row["END"])
    
    @staticmethod
    def preserve_value(val):
        return val;
    
    @staticmethod
    def is_primary(value, mode=None):
        if mode:
            if mode=='it':
                return 'Sensore Primario' if value=='1' else 'Sensore Secondario (backup)'
            elif mode=='wmo':
                return 'http://codes.wmo.int/bufr4/codeflag/0-08-015/1' if value=='1' else 'http://codes.wmo.int/bufr4/codeflag/0-08-015/2'
            else:
                return None
        else:
            return 'Primary Sensor' if value=='1' else 'Secondary Sensor (backup)'
        
    @staticmethod
    def get_unit_of_measure(unit_of_measure):
        if unit_of_measure == "meters":
            return "meter"
        elif unit_of_measure == "degrees":
            return "degree"
        else:
            return unit_of_measure

    @staticmethod    
    def get_unit_of_measure_wmo(unit_of_measure):
        if unit_of_measure == "meters":
            return "http://codes.wmo.int/common/unit/m"
        elif unit_of_measure == "degrees":
            return "http://codes.wmo.int/common/unit/degrees_true"
        else:
            return None
        
    @staticmethod
    def replace(find, rep, string):
        s = string.replace(find, rep)
        return s
    
    @staticmethod
    def cod_place(row):
        if len(str(row["CODE_PLACE"])) == 5:
            return "0" + str(row["CODE_PLACE"])
        else:
            return str(row["CODE_PLACE"])
        
    @staticmethod
    def coord_uri(coord):
        coord_str = str(coord)

        try:
            coord_int = coord_str.split('.')[0]
            coord_dec = coord_str.split('.')[1]
        except IndexError:
            return coord.replace('.', '')

        coord_int = coord_int.zfill(2)
        coord_dec = coord_dec.ljust(6, '0')

        return coord_int+coord_dec
    
    @staticmethod
    def get_point(long,lat):
        long = float(long)
        lat = float(lat)

        return ('POINT(%s %s)' % (long, lat))

    @staticmethod
    def round_coord(coord):
        try:
            value = str(round(float(coord),5))
    
        except ValueError:
            value = str(coord)

        return value
    
    @staticmethod
    def capitalize(s):
        return str(s).capitalize()

    @staticmethod
    def getYearMonth(date):
        try:
            result = dt.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            result = dt.datetime(1300,1,1)

        result = (format(result.year, '04d') + '-' + format(result.month, '02d'))

        return result


    @staticmethod
    def get_unit_of_measure_staz(metric, lang, iri=False):

        if iri:
            return TermUtils.irify(UNIT_OF_MEASURES_STAZ[metric]["Unit_EN"].lower())
        elif lang == 'symbol':
            return UNIT_OF_MEASURES_STAZ[metric]["Unit"]
        elif lang == 'it':
            return UNIT_OF_MEASURES_STAZ[metric]["Unit_IT"]
        else:
            return UNIT_OF_MEASURES_STAZ[metric]["Unit_EN"]
        

    @staticmethod
    def get_unit_of_measure_ind(metric, lang, iri=False):

        if iri:
            return TermUtils.irify(UNIT_OF_MEASURES_IND[metric]["Unit_EN"].lower())
        elif lang == 'symbol':
            return UNIT_OF_MEASURES_IND[metric]["Unit"]
        elif lang == 'it':
            return UNIT_OF_MEASURES_IND[metric]["Unit_IT"]
        else:
            return UNIT_OF_MEASURES_IND[metric]["Unit_EN"]
    

class PesticidesTriplifier(Triplifier):
    
    '''
        The following protected attributes are declared by the superclass Triplifier:
         - self._dataset -> the name of the dataset
         - self._rml_path -> the path to the RML mapping files
         - self._data_path -> the path to CSV data files.
    '''
    def __init__(self, year : int):
        
        functions_dictionary = {
            'measures_collection_title': Functions.measures_collection_title,
            'station_model_uri': Functions.station_model_uri,
            'station_model_id': Functions.station_model_id,
            'time_interval': Functions.time_interval,
            'round_coord': Functions.round_coord,
            'getYearMonth': Functions.getYearMonth,
            'preserve_value': Functions.preserve_value,
            'is_primary': Functions.is_primary,
            'get_unit_of_measure': Functions.get_unit_of_measure,
            'get_unit_of_measure_wmo': Functions.get_unit_of_measure_wmo,
            'replace': Functions.replace,
            'cod_place': Functions.cod_place,
            'coord_uri': Functions.coord_uri,
            'get_point': Functions.get_point,
            'capitalize': Functions.capitalize,
            'get_unit_of_measure_staz': Functions.get_unit_of_measure_staz,
            'get_unit_of_measure_ind': Functions.get_unit_of_measure_ind,
            'po_assertion_uuid': UtilsFunctions.po_assertion_uuid,
            'digest': UtilsFunctions.short_uuid
            }
        
        super().__init__('pesticides', functions_dictionary)
        self._dirty_data_path = os.path.join('pesticides', 'v2', 'dirtydata')

        self._conf_vars.update({"year": year})
        
        
    def _dataset_initialisation(self) -> None:
        print("Pesticides preprocessing...")
        
        KnowledgeGraphLoader.convert_utf8(self._dirty_data_path, self._data_path)

        df = pd.read_csv(os.path.join(self._data_path, "Descrizione_campiPesticidiStazioni.csv"), sep=None, engine='python', iterator=True)
        sep = df._engine.data.dialect.delimiter
        df.close()

        global UNIT_OF_MEASURES_STAZ

        units_df = pd.read_csv(os.path.join(self._data_path, "Descrizione_campiPesticidiStazioni.csv"), sep=sep)[["Campo", "Unit_EN", "Unit_IT", "Unit"]].set_index('Campo')
        UNIT_OF_MEASURES_STAZ = units_df.to_dict(orient="index")
        del units_df

        global UNIT_OF_MEASURES_IND
        
        units_df = pd.read_csv(os.path.join(self._data_path, "Descrizione_campiPesticidiStazioniSostanze.csv"), sep=sep)[["Campo", "Unit_EN", "Unit_IT", "Unit"]].set_index('Campo')
        UNIT_OF_MEASURES_IND = units_df.to_dict(orient="index")
        
        print("\t preprocessing completed.")
   
    def get_graph_iri(self):
        return 'https://w3id.org/italia/env/ld/pesticides'
    