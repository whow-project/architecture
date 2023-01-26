import os, csv

import clevercsv
from jinja2 import Environment, FileSystemLoader, Template
from rdflib.parser import StringInputSource

from pyrml import TermUtils, RMLConverter
from triplification import Triplifier, UtilsFunctions
from typing import Dict, Callable
import re
from kg_loader import KnowledgeGraphLoader
import pandas as pd


UNIT_OF_MEASURES = None

def metric (metric):
    if row["METRIC"] and isinstance(row["METRIC"], str):
        return "https://w3id.org/italia/env/ld/common/metric/" + row["METRIC"].lower()
    else:
        return None

def broader_metric (row):
    if row["BROADER"] and isinstance(row["BROADER"], str):
        return "https://w3id.org/italia/env/ld/common/metric/" + row["BROADER"].lower()
    else:
        return None

def indicator_entity (row, dataset):
    if row["METRIC"] and isinstance(row["METRIC"], str):
        return "https://w3id.org/italia/env/ld/" + dataset + "/" + row["COD_PLACE"] + "_" + row["METRIC"].lower()+ "_" + row["YEAR"]
    else:
        return None

def indicator_collection_entity (row, dataset):
    if row["METRIC"] and isinstance(row["METRIC"], str):
        return "https://w3id.org/italia/env/ld/" + dataset + "/" + row["COD_PLACE"] + "_" + row["METRIC"].lower()
    else:
        return None

def unit_entity (row):
    if row["UNIT_URI"] and isinstance(row["UNIT_URI"], str):
        return "https://w3id.org/italia/env/ld/common/unitofmeasure/" + row["UNIT_URI"].lower()
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
    
    fields_length_dict = {"IdOST_Origine": 6,
                          "PRO_COM": 6, 
                          "COD_PRO": 3, 
                          "COD_REG": 2, 
                          "Nazione": 1}
    
    for key in fields_length_dict.keys():
        if key in df.columns:
            df[key] = df[key].apply(lambda x: __istat_normaliser(str(x), fields_length_dict[key]))
        
    return df

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


def place_type(istat, field):

    istat = str(istat)
    field = str(field)
  
    if field == "IdOST_Origine":
        if len(istat) == 3:
            if istat.startswith("2"):
                type = "metropolitancity"
            else:
                type = "province"
        elif len(istat) == 2:
            type = "region"
        elif len(istat) == 1:
            type = "country"
        elif len(istat) > 3 and len(istat) <= 6:
            type = "municipality"
        else:
            type = None       
        return "%s"%(type)

    elif field == "PRO_COM":
        type = "municipality"
    elif field == "COD_PROV":
        if istat.startswith("2"):
            type = "metropolitancity"
        else:
            type = "province"
    elif field == "COD_REG":
        type = "region"
    elif field == "COD":
        type = "country"
        
    else:
        return None

    return "%s"%(type)


def label_it(dset):
    dset = str(dset)
    if (dset == "soilc"):
        return str("consumo del suolo")
        #return TermUtils.irify("consumo del suolo")
    elif (dset == "urban"):
        return str("aree urbane")
    else:
        return None

def label_en(dset):
    dset = str(dset)
    if (dset == "soilc"):
        return str("soil consumption")
    elif (dset == "urban"):
        return str("urban areas")
    else:
        return None


class LandTriplifier(Triplifier):
    
    '''
        The following protected attributes are declared by the superclass Triplifier:
         - self._dataset -> the name of the dataset
         - self._rml_path -> the path to the RML mapping files
         - self._data_path -> the path to CSV data files.
    '''
    def __init__(self, key_name : str, year : int):
        
        functions_dictionary = {
            'metric': metric,
            'broader_metric': broader_metric,
            'indicator_entity': indicator_entity,
            'indicator_collection_entity': indicator_collection_entity,
            'unit_entity': unit_entity,
            'place_type': place_type,
            'label_it': label_it,
            'label_en': label_en,
            'get_unit_of_measure': get_unit_of_measure,
            'round': round,
            'get_value': get_value
            }
        
        super().__init__(key_name, functions_dictionary)
        self._dirty_data_path = os.path.join(key_name, 'v2', 'dirtydata')
        
        self._conf_vars.update({"year": year})
        
        
    def _dataset_initialisation(self) -> None:
        print("Starting preprocessing ...")

        KnowledgeGraphLoader.convert_utf8(self._dirty_data_path, self._data_path)
        

        files = [ file for file in os.listdir(self._data_path) if file.endswith(".csv") and file.lower() != 'info.csv']

        for file in files:
            print ("ISTAT ID normalizer for", file)
            df = pd.read_csv(os.path.join(self._data_path, file), sep=None, engine='python', iterator=True)
            sep = df._engine.data.dialect.delimiter
            df.close()
            df = pd.read_csv(os.path.join(self._data_path, file), sep=sep)
            if ('soilc' in self._data_path or 'Comuni' in file):
                df_istat = istat_normaliser(df)
                df_istat.to_csv(os.path.join(self._data_path, file), sep=sep, index=None)
            
        df = pd.read_csv(os.path.join(self._data_path, "Descrizione_campi.csv"), sep=None, engine='python', iterator=True)
        separator = df._engine.data.dialect.delimiter
        df.close()
        
        global UNIT_OF_MEASURES
        
        
        units_df = pd.read_csv(os.path.join(self._data_path, "Descrizione_campi.csv"), sep=sep)[["Campo", "Unit_EN", "Unit_IT", "Unit"]].set_index('Campo')
        UNIT_OF_MEASURES = units_df.to_dict(orient="index")
        
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
        return 'https://w3id.org/italia/env/ld/' + key_name
    