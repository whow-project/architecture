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
        if (int(istat) in df_mc['PROV_CODE'].values):
            istat = (str(df_mc['MC_CODE'][df_mc['PROV_CODE']==int(istat)].values[0]))
    except:
        return istat

    return istat

def istat_normaliser(df):
    
    fields_length_dict = {"PRO_COM": 6, 
                          "COD_PROV": 3, 
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


def place_code(istat, field):

    length = 0
    istat = str(istat)
    field = str(field)

    if field == "IdOST_Origine":
        _length = len(istat)
        if _length > 3 and _length < 6:
            length = 6

    elif field == "PRO_COM":
        length = 6
    elif field == "COD_PROV":
        length = 3
    elif field == "COD_REG":
        length = 2
    elif field == "COD":
        length = 1
        
    else:
        return None
   
    while len(istat) < length:
        istat = str(0) + istat

    if field == "COD_PROV" and istat in metropolitan_cities:
            istat.replace("0","2",1)
  
    return "%s"%(istat)


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
        if self.place_code(istat,field).startswith("2"):
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


def place_id(istat, field, istat_only):
    
    length = 0
    if field == "PRO_COM" or field == "IdOST_Origine":
        length = 6
        type = "municipality"
    elif field == "COD_PROV":
        length = 3
        if istat.startswith("2"):
            type = "metropolitancity"
        else:
            type = "province"
    elif field == "COD_REG":
        length = 2
        type = "region"
    elif field == "COD":
        length = 1
        type = "country"
        
    else:
        return None
        
    while len(istat) < length:
        istat = str(0) + istat
        
    if istat_only:
        return istat
    else:
        return "%s/%s"%(type, istat)


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
            'place_id': place_id,
            'place_code': place_code,
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

        utf8_converter = UTF8Converter(self._dirty_data_path, self._data_path)
        utf8_converter.convert()
        

        files = [ file for file in os.listdir(self._data_path) if file.endswith(".csv") and file.lower() != 'info.csv']

        for file in files:
            print ("ISTAT ID normalizer for", file)
            df = pd.read_csv(os.path.join(self._data_path, file), sep=None, engine='python', iterator=True)
            sep = df._engine.data.dialect.delimiter
            df.close()
            df = pd.read_csv(os.path.join(self._data_path, file), sep=sep)
            df_istat = istat_normaliser(df)
            if 'soilc' in str(self._data_path):
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
        return 'https://dati.isprambiente.it/ld/' + key_name
    