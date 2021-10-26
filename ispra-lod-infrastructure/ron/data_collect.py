import os

from io import StringIO

import pandas as pd
import numpy as np

from SPARQLWrapper import SPARQLWrapper, CSV, SELECT, POST, POSTDIRECTLY


def fix_sensor_type(x, field):
    if x[field] == x[field]:
        if 'Termometer' in x[field]:
            return x[field].replace('Termometer', 'Thermometer')
        elif 'WaveGauge' in x[field]:
            return x[field].replace('WaveGauge', 'Wave gauge')
        else:
            return x[field]
    
def add_sensor_type_same_as(x, dataset):
    sensor_type = x['TYPE_EN']
    
    
    sameas = np.nan
    if sensor_type in sensor_types_sameas:
        same_ases = sensor_types_sameas[sensor_type]
        if same_ases:
            if dataset in same_ases:
                sameas = same_ases[dataset]
                
    return sameas
            
                
    
            
    
        
term_dict = {
    'Thermometer': 'Termometro',
    'Air Thermometer': 'Termometro dell\'aria',
    'Anemometer': 'Anemometro',
    'Barometer': 'Barometro',
    'Hygrometer': 'Igrometro',
    'Water Thermometer': 'Termometro dell\'acqua',
    'Solid-state sensor': 'Sensore a stato solido',
    'Stabilized platform sensor': 'Sensore a piattaforma stabilizzata',
    'Wave gauge': 'Indicatore ondametrico'
    }

sensor_types_sameas = {
    'Thermometer': {'dbpedia': 'http://dbpedia.org/resource/Thermometer', 'wikidata': 'http://www.wikidata.org/entity/Q646'},
    'Anemometer': {'dbpedia': 'http://dbpedia.org/resource/Anemometer', 'wikidata': 'http://www.wikidata.org/entity/Q175029'},
    'Barometer': {'dbpedia': 'http://dbpedia.org/resource/Barometer', 'wikidata': 'http://www.wikidata.org/entity/Q79757'},
    'Hygrometer': {'dbpedia': 'http://dbpedia.org/resource/Hygrometer', 'wikidata': 'http://www.wikidata.org/entity/Q183173'},
    }



class QueryException(Exception):
    pass


def get_sparql_dataframe(endpoint, query, post=False):
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    if sparql.queryType != SELECT:
        raise QueryException("Only SPARQL SELECT queries are supported.")

    if post:
        sparql.setOnlyConneg(True)
        sparql.addCustomHttpHeader("Content-type", "application/sparql-query")
        sparql.addCustomHttpHeader("Accept", "text/csv")
        sparql.setMethod(POST)
        sparql.setRequestMethod(POSTDIRECTLY)

    sparql.setReturnFormat(CSV)
    results = sparql.query().convert()
    _csv = StringIO(results.decode('utf-8'))
    return pd.read_csv(_csv, sep=",", dtype=str)

    
def translate(x, field):
    if x[field] in term_dict:
        return term_dict[x[field]]
    else:
        return x[field]

if __name__ == '__main__':
    
    query_folder = os.path.join('v2', 'queries')
    data_folder = os.path.join('v2', 'dirtydata')
    
    df = pd.read_csv(os.path.join(data_folder, 'indicators.csv'), sep=';')
    
    df['UNIT_IT'] = df['UNIT'].apply(lambda x: 'gradi' if x=='degrees' else 'metri')
    df['UNIT_SYMBOL'] = df['UNIT'].apply(lambda x: 'deg' if x=='degrees' else 'm')
    df.to_csv(os.path.join(data_folder, 'indicators.csv'), sep=';')

    endpoint = 'http://dati.isprambiente.it/sparql'
    with open(os.path.join(query_folder, 'sensors.txt'), "r") as f:
        sparql = f.read()
        print(sparql)
        
        df = get_sparql_dataframe(endpoint, sparql)
        print(df.columns)
        #df['TYPE_EN'] = df.apply(lambda x: fix_sensor_type(x, 'TYPE_EN'), axis=1)
        df['SENS_TYPE_EN'] = df.apply(lambda x: fix_sensor_type(x, 'SENS_TYPE_EN'), axis=1)
        
        #df['TYPE_IT'] = df.apply(lambda x: translate(x, 'TYPE_EN'), axis=1)
        df['SENS_TYPE_IT'] = df.apply(lambda x: translate(x, 'SENS_TYPE_EN'), axis=1)
        
        df['PERIOD_UNIT'] = df.apply(lambda x: 'H', axis=1)
        
        df.set_index("STAT_CODE", inplace=True)
        
        
        df.to_csv(os.path.join(data_folder, 'sensors.csv'), sep=';')
        
    with open(os.path.join(query_folder, 'sensor_narrower_types.txt'), "r") as f:
        sparql = f.read()
        print(sparql)
        
        df = get_sparql_dataframe(endpoint, sparql)
        print(df.columns)
        #df['TYPE_EN'] = df.apply(lambda x: fix_sensor_type(x, 'TYPE_EN'), axis=1)
        df['SENS_TYPE_EN'] = df.apply(lambda x: fix_sensor_type(x, 'SENS_TYPE_EN'), axis=1)
        df['TYPE_EN'] = df.apply(lambda x: fix_sensor_type(x, 'TYPE_EN'), axis=1)
        
        #df['TYPE_IT'] = df.apply(lambda x: translate(x, 'TYPE_EN'), axis=1)
        df['SENS_TYPE_IT'] = df.apply(lambda x: translate(x, 'SENS_TYPE_EN'), axis=1)
        
        df.set_index("SENS_TYPE_EN", inplace=True)
        
        df.to_csv(os.path.join(data_folder, 'sensor_narrower_types.csv'), sep=';')
        
    with open(os.path.join(query_folder, 'sensor_broader_types.txt'), "r") as f:
        sparql = f.read()
        print(sparql)
        
        df = get_sparql_dataframe(endpoint, sparql)
        print(df.columns)
        #df['TYPE_EN'] = df.apply(lambda x: fix_sensor_type(x, 'TYPE_EN'), axis=1)
        df['TYPE_EN'] = df.apply(lambda x: fix_sensor_type(x, 'TYPE_EN'), axis=1)
        
        #df['TYPE_IT'] = df.apply(lambda x: translate(x, 'TYPE_EN'), axis=1)
        df['TYPE_IT'] = df.apply(lambda x: translate(x, 'TYPE_EN'), axis=1)
        
        df['DBPEDIA'] = df.apply(lambda x: add_sensor_type_same_as(x, 'dbpedia'), axis=1)
        df['WIKIDATA'] = df.apply(lambda x: add_sensor_type_same_as(x, 'wikidata'), axis=1)
        
        df.set_index("TYPE_EN", inplace=True)
        
        df.to_csv(os.path.join(data_folder, 'sensor_broader_types.csv'), sep=';')
        
    with open(os.path.join(query_folder, 'observations.txt'), "r") as f:
        sparql = f.read()
        print(sparql)
        
        df = get_sparql_dataframe(endpoint, sparql)
        df.set_index("DATA", inplace=True)
        
        df.to_csv(os.path.join(data_folder, 'observations.csv'), sep=';')
        
    