from builtins import staticmethod
import os
import re
import datetime as dt
from kg_loader import KnowledgeGraphLoader
from pyrml import TermUtils
from triplification import Triplifier
from utils import Utils

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
            'round_coord': Utils.round_coord,
            'getYearMonth': Utils.getYearMonth,
            'preserve_value': Functions.preserve_value
            }
        
        super().__init__('rmn', functions_dictionary)
        
        
    def _dataset_initialisation(self) -> None:
        print("RMN preprocessing...")
        
        KnowledgeGraphLoader.convert_utf8(self._dirty_data_path, self._data_path)
                
        print("\t preprocessing completed.")
        
    
    def get_graph_iri(self):
        return 'https://w3id.org/italia/env/ld/rmn'
    
