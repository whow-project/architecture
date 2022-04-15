import os, csv

import clevercsv
from jinja2 import Environment, FileSystemLoader, Template
from rdflib.parser import StringInputSource

from pyrml.pyrml import TermUtils, RMLConverter
from triplification import Triplifier, UtilsFunctions
from typing import Dict, Callable
import re
from utf8_converter import UTF8Converter
import pandas as pd
from builtins import staticmethod
import shortuuid


UNIT_OF_MEASURES = None

def metric (metric):
    if row["METRIC"] and isinstance(row["METRIC"], str):
        return "https://dati.isprambiente.it/ld/common/metric/" + row["METRIC"].lower()
    else:
        return None

def broader_metric (row):
    if row["BROADER"] and isinstance(row["BROADER"], str):
        return "https://dati.isprambiente.it/ld/common/metric/" + row["BROADER"].lower()
    else:
        return None

def indicator_entity (row, dataset):
    if row["METRIC"] and isinstance(row["METRIC"], str):
        return "https://dati.isprambiente.it/ld/" + dataset + "/" + row["COD_PLACE"] + "_" + row["METRIC"].lower()+ "_" + row["YEAR"]
    else:
        return None

def indicator_collection_entity (row, dataset):
    if row["METRIC"] and isinstance(row["METRIC"], str):
        return "https://dati.isprambiente.it/ld/" + dataset + "/" + row["COD_PLACE"] + "_" + row["METRIC"].lower()
    else:
        return None

def unit_entity (row):
    if row["UNIT_URI"] and isinstance(row["UNIT_URI"], str):
        return "https://dati.isprambiente.it/ld/common/unitofmeasure/" + row["UNIT_URI"].lower()
    else:
        return None

def __istat_normaliser(istat, length):
    metropolitan_cities = ["001", "010", "015", "027", "037", "048", "058", "063", "072", "080", "082", "083", "087", "092"]
    while len(istat) < length:
        istat = str(0) + istat
        
    if istat in metropolitan_cities:
        istat = str(2) + istat[1:]
    return istat

def istat_normaliser(df):
    
    fields_length_dict = {"PRO_COM": 6, 
                          "IdOST_Origine": 6, 
                          "COD_PRO": 3, 
                          "COD_REF": 2, 
                          "Nazione": 1}
    
    for key in fields_length_dict.keys():
        if key in df.columns:
            df[key] = df[key].apply(lambda x: __istat_normaliser(str(x), fields_length_dict[key]))
        
    return df


def get_unit_of_measure(metric, lang, iri=False):
    
    if iri:
        return TermUtils.irify(UNIT_OF_MEASURES[UNIT_OF_MEASURES["Campo"] == metric]["Unit_EN"].values[0].lower())
    elif lang == 'symbol':
        return UNIT_OF_MEASURES[UNIT_OF_MEASURES["Campo"] == metric]["Unit"].values[0]
    elif lang == 'it':
        return UNIT_OF_MEASURES[UNIT_OF_MEASURES["Campo"] == metric]["Unit_IT"].values[0]
    else:
        return UNIT_OF_MEASURES[UNIT_OF_MEASURES["Campo"] == metric]["Unit_EN"].values[0]

def get_value(indicator_value):
    try:
        value = round(float(indicator_value), 2)
    except ValueError:
        value = indicator_value
        
    return str(value)
    
    

def place_type(istat):
    
    if len(istat) == 3:
        if istat.startswith("2"):
            _type = "metropolitancity"
        else:
            _type = "province"
    elif len(istat) == 2:
        _type = "region"
    elif len(istat) == 1:
        _type = "country"
    elif len(istat) > 3 and len(istat) <= 6:
        _type = "municipality"
    else:
        _type = None
        
    return _type

def place_id(istat):
    istat = istat.strip()
    _length = len(istat)
    while _length > 3 and _length < 6:
        istat = str(0) + istat
        _length += 1
        
    return istat
    

class UrbanTriplifier(Triplifier):
    
    '''
        The following protected attributes are declared by the superclass Triplifier:
         - self._dataset -> the name of the dataset
         - self._rml_path -> the path to the RML mapping files
         - self._data_path -> the path to CSV data files.
    '''
    def __init__(self, year : int):
        
        functions_dictionary = {
            'metric': metric,
            'broader_metric': broader_metric,
            'indicator_entity': indicator_entity,
            'indicator_collection_entity': indicator_collection_entity,
            'unit_entity': unit_entity,
            'place_type': place_type,
            'place_id': place_id,
            'get_unit_of_measure': get_unit_of_measure,
            'round': round,
            'get_value': get_value,
            'po_assertion_uuid': UtilsFunctions.po_assertion_uuid
            }
        
        super().__init__('urban', functions_dictionary)
        self._dirty_data_path = os.path.join('urban', 'v2', 'dirtydata')
        
        self._conf_vars.update({"year": year})
        
    def _dataset_initialisation(self) -> None:
        print("Urban preprocessing...")
        print("UFT8zer")
        
        utf8_converter = UTF8Converter(self._dirty_data_path, self._data_path)
        utf8_converter.convert()
        
        
        files = [ file for file in os.listdir(self._data_path) if file.endswith(".csv") and file.lower() != 'info.csv']
        
        for file in files:
            df = pd.read_csv(os.path.join(self._data_path, file), sep=None, engine='python', iterator=True)
            sep = df._engine.data.dialect.delimiter
            df.close()
            df = pd.read_csv(os.path.join(self._data_path, file), sep=sep, dtype=str)
            df.set_index(df.columns[0], inplace=True)
            df = istat_normaliser(df)
            df.to_csv(os.path.join(self._data_path, file), sep=sep)
            
            
        df = pd.read_csv(os.path.join(self._data_path, "Descrizione_campi.csv"), sep=None, engine='python', iterator=True)
        separator = df._engine.data.dialect.delimiter
        df.close()
        
        global UNIT_OF_MEASURES
        UNIT_OF_MEASURES = pd.read_csv(os.path.join(self._data_path, "Descrizione_campi.csv"), sep=sep)[["Campo", "Unit_EN", "Unit_IT", "Unit"]]
        print(UNIT_OF_MEASURES)
            
        
        '''
        files = [ file for file in os.listdir(self._dirty_data_path) if file.endswith(".csv") and file.lower() != 'info.csv']
        
        for file in files:
            if "descrizione_campi" in file.lower():
                metric_csv = os.path.join(self._dirty_data_path, file)
                break
        
        for file in files:
            
            preprocessing(self._dataset, self._dirty_data_path, self._data_path, file, metric_csv, ';')
            
        '''
        print("\t preprocessing completed.")
        
    
    def get_graph_iri(self):
        return 'https://dati.isprambiente.it/ld/urban'
        
