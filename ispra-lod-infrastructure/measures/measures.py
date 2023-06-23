from builtins import staticmethod
import os, re, csv
import pandas as pd
import datetime as dt
from pyrml import TermUtils
from triplification import Triplifier, UtilsFunctions
from kg_loader import KnowledgeGraphLoader
from utils import Utils


class Functions():

    @staticmethod
    def measures_collection_title(row):
        return row["COLL_TYPE"].title()

    @staticmethod    
    def time_interval(row):
        return re.sub("[^0-9]", "", row["START"]) + "_" + re.sub("[^0-9]", "", row["END"])
    
    @staticmethod
    def preserve_value(val):
        return val
    
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

    
class MeasuresTriplifier(Triplifier):
    
    '''
        The following protected attributes are declared by the superclass Triplifier:
         - self._dataset -> the name of the dataset
         - self._rml_path -> the path to the RML mapping files
         - self._data_path -> the path to CSV data files.
    '''
    def __init__(self, key_name : str):
        
        functions_dictionary = {
            'measures_collection_title': Functions.measures_collection_title,
            'time_interval': Functions.time_interval,
            'round_coord': Utils.round_coord,
            'getYearMonth': Utils.getYearMonth,
            'label_it': Utils.label_it,
            'label_en': Utils.label_en,
            'preserve_value': Functions.preserve_value,
            'is_primary': Functions.is_primary,
            'get_unit_of_measure': Functions.get_unit_of_measure,
            'get_unit_of_measure_wmo': Functions.get_unit_of_measure_wmo,
            'replace': Functions.replace,
            'cod_place': Functions.cod_place,
            'po_assertion_uuid': UtilsFunctions.po_assertion_uuid
            }
        
        super().__init__(key_name, functions_dictionary)
        self._dirty_data_path = os.path.join('data', key_name, 'v2', 'dirtydata')
        self._data_path = os.path.join('data', key_name, 'v2', 'data')

        self._dataset_initialisation(key_name)
        

    def _dataset_initialisation(self, dataset) -> None:
        print("RMN preprocessing...")
        self.__preprocess(dataset)
        KnowledgeGraphLoader.convert_utf8(self._dirty_data_path, self._data_path)
        print("\t preprocessing completed.")
        
    
    def get_graph_iri(self, key_name : str):
        return 'https://w3id.org/italia/env/ld/' + key_name
    

    def __preprocess(self, dset) -> None:
        '''
        Split the original csvs according to network and saves new files into corresponding dirs
        '''
        print ('Splitting input files ...')
        dirtydatafolder = "data/measures/v2/dirtydata"
        #loop on csvs
        for file in os.listdir(dirtydatafolder):
            csvfile = os.path.join(dirtydatafolder, file)
            
            df_tosplit = pd.read_csv(csvfile, sep=';', dtype=str)
            #loop on networks
            try:
                netws = [s for s in df_tosplit['NETWORK'].unique()]
            except KeyError:
                newfolder = os.path.join("data", dset ,"v2", "dirtydata")
                newcsvfile = os.path.join(newfolder, file)
                df_tosplit.to_csv(newcsvfile, sep=';', index=None, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                continue

            for netw in netws:
                df_sel = df_tosplit[df_tosplit['NETWORK'] == netw]
                #df_sel = df_sel.dropna(axis=1, how='all')

                newfolder = os.path.join("data", netw.lower() ,"v2", "dirtydata")
                newcsvfile = os.path.join(newfolder, file)
                df_sel.to_csv(newcsvfile, sep=';', index=None, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

                del df_sel

            del df_tosplit