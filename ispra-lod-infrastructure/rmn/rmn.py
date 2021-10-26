from builtins import staticmethod
import os
import re

from pyrml.pyrml import TermUtils
from triplification import Triplifier
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
        
    
class RMNTriplifier(Triplifier):
    
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
            'preserve_value': Functions.preserve_value
            }
        
        super().__init__('rmn', functions_dictionary)
        self._dirty_data_path = os.path.join('rmn', 'v2', 'dirtydata')
        
        
    def _dataset_initialisation(self) -> None:
        print("RMN preprocessing...")
        
        utf8_converter = UTF8Converter(self._dirty_data_path, self._data_path)
        utf8_converter.convert()
        
        print("\t preprocessing completed.")
        
    
    def get_graph_iri(self):
        return 'https://dati.isprambiente.it/ld/rmn'
    
