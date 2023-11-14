from builtins import staticmethod
import os
import re
import math
import pandas as pd
import datetime as dt
from utils import Utils
from triplification import Triplifier, UtilsFunctions
from kg_loader import KnowledgeGraphLoader


UNIT_OF_MEASURES = None
DESCRIPTION_PAR = None


class Functions():

    @staticmethod
    def get_null(value):
        return (str(value) != '')

    @staticmethod
    def preserve_value(val):
        return val
       
    @staticmethod
    def coord_uri(coord):
        coord_str = str(coord)

        try:
            coord_int = coord_str.split('.')[0]
            coord_dec = coord_str.split('.')[1]
        except IndexError:
            return coord.replace('.', '')

        coord_int = coord_int.zfill(2)
        coord_dec = coord_dec.ljust(6, '0')

        return coord_int+coord_dec
    
    @staticmethod
    def get_point(long,lat):
        try:
            long = float(long)
            lat = float(lat)
        except TypeError:
            pass

        return ('POINT(%s %s)' % (long, lat))    


class BathwTriplifier(Triplifier):
    
    '''
        The following protected attributes are declared by the superclass Triplifier:
         - self._dataset -> the name of the dataset
         - self._rml_path -> the path to the RML mapping files
         - self._data_path -> the path to CSV data files.
    '''
    def __init__(self, year : int):
        
        functions_dictionary = {
            'get_null': Functions.get_null,
            'round_coord': Utils.round_coord,
            'getYearMonth': Utils.getYearMonth,
            'preserve_value': Functions.preserve_value,
            'coord_uri': Functions.coord_uri,
            'get_point': Functions.get_point,
            'title': Utils.title,
            'capitalize': Utils.capitalize,
            'lower': Utils.lower,
            'upper': Utils.upper,
            'label_it': Utils.label_it,
            'label_en': Utils.label_en,
            'replace': Utils.replace,
            'identity': Utils.identity,
            'po_assertion_uuid': UtilsFunctions.po_assertion_uuid,
            'digest': UtilsFunctions.short_uuid
            }
        
        super().__init__('bathw', functions_dictionary)
        self._dirty_data_path = os.path.join('data', 'bathw', 'v2', 'dirtydata')
        self._data_path = os.path.join('data', 'bathw', 'v2', 'data')

        self._conf_vars.update({"year": year})
        
        
    def _dataset_initialisation(self, dirty_data_path: str, data_path: str) -> None:
        print("Bathing Waters preprocessing...")
        
        KnowledgeGraphLoader.convert_utf8(dirty_data_path, data_path)

    def get_graph_iri(self):
        return 'https://w3id.org/italia/env/ld/bathw'
    
