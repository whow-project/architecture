import os, csv
import clevercsv
from jinja2 import Environment, FileSystemLoader, Template
from rdflib.parser import StringInputSource
from kg_loader import KnowledgeGraphLoader
from pyrml import TermUtils, RMLConverter
from triplification import Triplifier, UtilsFunctions
from typing import Dict, Callable
import re
import pandas as pd
from utils import round_coord


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
    
    fields_length_dict = {"cod_com_istat": 6,
                          "COD_PRO": 3,
                          "COD_REG": 2,
                          "Nazione": 1}
    
    for key in fields_length_dict.keys():
        if key in df.columns:
            df[key] = df[key].apply(lambda x: __istat_normaliser(str(x), fields_length_dict[key]))
        
    return df


def get_point(long, lat):
    return 'POINT('+str(long)+' '+str(lat)+')'


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
    elif field == "COD_PRO":
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
            'get_value': get_value,
            'place_type': place_type,
            'get_point': get_point,
            'digest': UtilsFunctions.short_uuid
            }
        
        super().__init__('epe', functions_dictionary)
        self._dirty_data_path = os.path.join('epe', 'v2', 'dirtydata')
        
        self._conf_vars.update({"year": year})
        
        
    def _dataset_initialisation(self) -> None:
        print("Starting preprocessing ...")

        KnowledgeGraphLoader.convert_utf8(self._dirty_data_path, self._data_path)
        

        files = [ file for file in os.listdir(self._data_path) if file.endswith(".csv") ]

        for file in files:
            if ('istat' in file or 'Regioni' in file):
                print ("ISTAT ID normalizer for", file)
                df = pd.read_csv(os.path.join(self._data_path, file), sep=None, engine='python', iterator=True)
                sep = df._engine.data.dialect.delimiter
                df.close()
                df = pd.read_csv(os.path.join(self._data_path, file), sep=sep)
                df_istat = istat_normaliser(df)
                df_istat.to_csv(os.path.join(self._data_path, file), sep=sep, index=None)
                del df_istat, df

        df = pd.read_csv(os.path.join(self._data_path, "Descrizione_campi.csv"), sep=None, engine='python', iterator=True)
        separator = df._engine.data.dialect.delimiter
        df.close()
        
        global UNIT_OF_MEASURES
        
        
        units_df = pd.read_csv(os.path.join(self._data_path, "Descrizione_campi.csv"), sep=sep)[["Campo", "Unit_EN", "Unit_IT", "Unit"]].set_index('Campo')
        UNIT_OF_MEASURES = units_df.to_dict(orient="index")
        
        print("\t preprocessing completed.")
        
    
    def get_graph_iri(self):
        return 'https://w3id.org/italia/env/ld/' + 'epe'
    