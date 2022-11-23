from builtins import staticmethod
import os
import re
import datetime as dt
from pyrml.pyrml import TermUtils
from triplification import Triplifier, UtilsFunctions
from utf8_converter import UTF8Converter


class Functions():

    @staticmethod
    def measures_collection_title(row):
        return row["COLL_TYPE"].title()

    @staticmethod
    def station_model_uri(row, dataset):
        return "https://dati.isprambiente.it/ld/" + dataset + "/platformmodel/" + Functions.station_model_id(row, dataset)
    
    @staticmethod
    def station_model_id(row, dataset):
        if "STAT_CODE" in row and dataset == 'rmn':
            return TermUtils.irify(row["STAT_CODE"]) + "_" + TermUtils.irify(row["NETWORK"]) + "_" + TermUtils.irify(row["TYPE_EN"])
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
    def round_coord(coord):
        try:
            value = str(round(float(coord),5))
    
        except ValueError:
            value = str(coord)

        return value

    @staticmethod
    def getYearMonth(date):
        try:
            result = dt.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            result = dt.datetime(1300,1,1)

        result = (format(result.year, '04d') + '-' + format(result.month, '02d'))

        return result
    
class RONTriplifier(Triplifier):
    
    '''
        The following protected attributes are declared by the superclass Triplifier:
         - self._dataset -> the name of the dataset
         - self._rml_path -> the path to the RML mapping files
         - self._data_path -> the path to CSV data files.
    '''
    def __init__(self):
        
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
            'po_assertion_uuid': UtilsFunctions.po_assertion_uuid
            }
        
        super().__init__('ron', functions_dictionary)
        self._dirty_data_path = os.path.join('ron', 'v2', 'dirtydata')
        
        
    def _dataset_initialisation(self) -> None:
        print("RMN preprocessing...")
        
        utf8_converter = UTF8Converter(self._dirty_data_path, self._data_path)
        utf8_converter.convert()
        
        print("\t preprocessing completed.")
   
    def get_graph_iri(self):
        return 'https://dati.isprambiente.it/ld/ron'
    
