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
    csv_file = "data/place/v2/dirtydata/metropolitan_cities.csv"
    df_mc = pd.read_csv(csv_file, delimiter=';')

    while len(istat) < length:
        istat = str(0) + istat

    try:
        if (length == 3 and int(istat) in df_mc['PROV_CODE'].values):
            istat = (str(df_mc['MC_CODE'][df_mc['PROV_CODE']==int(istat)].values[0]))
    except:
        return istat

    return istat

def istat_normaliser(df):
    
    fields_length_dict = {"cod_com_istat": 6}
    
    for key in fields_length_dict.keys():
        if key in df.columns:
            df[key] = df[key].apply(lambda x: __istat_normaliser(str(x), fields_length_dict[key]))
        
    return df


def round_coord(coord):

    try:
        value = str(round(float(coord),5))
    
    except ValueError:
        value = str(coord)

    return value


def format_date(dd, mm, yy):

    date = format(int(yy), '04d') + format(int(mm), '02d') + format(int(dd), '02d')
    return date


def format_euring(euid):

    return format(int(euid), '05d')


def get_unit_of_measure(metric, lang, iri=False):
    
    
    if iri:
        return TermUtils.irify(UNIT_OF_MEASURES[metric]["Unit_EN"].lower())
    elif lang == 'symbol':
        return UNIT_OF_MEASURES[metric]["Unit"]
    elif lang == 'it':
        return UNIT_OF_MEASURES[metric]["Unit_IT"]
    else:
        return UNIT_OF_MEASURES[metric]["Unit_EN"]
    
    '''
    if iri:
        return TermUtils.irify(UNIT_OF_MEASURES[UNIT_OF_MEASURES["Campo"] == metric]["Unit_EN"].values[0].lower())
    elif lang == 'symbol':
        return UNIT_OF_MEASURES[UNIT_OF_MEASURES["Campo"] == metric]["Unit"].values[0]
    elif lang == 'it':
        return UNIT_OF_MEASURES[UNIT_OF_MEASURES["Campo"] == metric]["Unit_IT"].values[0]
    else:
        return UNIT_OF_MEASURES[UNIT_OF_MEASURES["Campo"] == metric]["Unit_EN"].values[0]
    '''

def get_value(indicator_value, iri=False):
    try:
        value = round(float(indicator_value), 2)
    except ValueError:
        value = indicator_value
    
    value = str(value)
    
    if iri:
        value = TermUtils.irify(value)
    
    return value


class EpeTriplifier(Triplifier):
    
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
            'istat_normaliser': istat_normaliser,
            'round_coord': round_coord,
            'format_date': format_date,
            'format_euring': format_euring,
            'get_unit_of_measure': get_unit_of_measure,
            'round': round,
            'get_value': get_value
            }
        
        super().__init__('epe', functions_dictionary)
        self._dirty_data_path = os.path.join('epe', 'v2', 'dirtydata')
        
        self._conf_vars.update({"year": year})
        
        
    def _dataset_initialisation(self) -> None:
        print("Starting preprocessing ...")

        utf8_converter = UTF8Converter(self._dirty_data_path, self._data_path)
        utf8_converter.convert()
        

        files = [ file for file in os.listdir(self._data_path) if file.endswith(".csv") ]

        for file in files:
            print ("ISTAT ID normalizer for", file)
            df = pd.read_csv(os.path.join(self._data_path, file), sep=None, engine='python', iterator=True)
            sep = df._engine.data.dialect.delimiter
            df.close()
            df = pd.read_csv(os.path.join(self._data_path, file), sep=sep)
            if ('soilc' in self._data_path or 'Comuni' in file):
                df_istat = istat_normaliser(df)
                df_istat.to_csv(os.path.join(self._data_path, file), sep=sep, index=None)
                del df_istat
            
            del df
        
        print("\t preprocessing completed.")
        
    
    def get_graph_iri(self):
        return 'https://dati.isprambiente.it/ld/' + 'epe'
    