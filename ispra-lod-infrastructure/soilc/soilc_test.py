import os, csv

import clevercsv
from jinja2 import Environment, FileSystemLoader, Template
from rdflib.parser import StringInputSource

from pyrml.pyrml import TermUtils, RMLConverter
from triplification import Triplifier, UtilsFunctions
from typing import Dict, Callable
import re
from indicatorsPreprocessing import preprocessing
from utf8_converter import UTF8Converter


def metric (row):
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
        return "https://dati.isprambiente.it/ld/" + dataset + "/" + row["COD_PLACE"] + "/" + row["METRIC"].lower()+ "/" + row["YEAR"]
    else:
        return None

def indicator_collection_entity (row, dataset):
    if row["METRIC"] and isinstance(row["METRIC"], str):
        return "https://dati.isprambiente.it/ld/" + dataset + "/" + row["COD_PLACE"] + "/" + row["METRIC"].lower()
    else:
        return None

def unit_entity (row):
    if row["UNIT_URI"] and isinstance(row["UNIT_URI"], str):
        return "https://dati.isprambiente.it/ld/common/mu/" + row["UNIT_URI"].lower()
    else:
        return None


class SoilcTriplifier(Triplifier):
    
    '''
        The following protected attributes are declared by the superclass Triplifier:
         - self._dataset -> the name of the dataset
         - self._rml_path -> the path to the RML mapping files
         - self._data_path -> the path to CSV data files.
    '''
    def __init__(self):
        
        functions_dictionary = {
            'metric': metric,
            'broader_metric': broader_metric,
            'indicator_entity': indicator_entity,
            'indicator_collection_entity': indicator_collection_entity,
            'unit_entity': unit_entity
            }
        
        super().__init__('soilc', functions_dictionary)
        self._dirty_data_path = os.path.join('soilc', 'v2', 'dirtydata')
        
        
        
        
    def _dataset_initialisation(self) -> None:
        print("Soilc preprocessing...")
        
        print("\t preprocessing completed.")
        
    
    def get_graph_iri(self):
        return 'https://dati.isprambiente.it/ld/soilc'
    
