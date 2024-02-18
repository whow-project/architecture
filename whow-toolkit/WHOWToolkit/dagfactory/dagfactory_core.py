from api.api import Configuration, DAGFactory, DAGFactoryInput
from jinja2 import Environment, FileSystemLoader
import uuid
import os
import glob
import json

import logging

from typing import Dict


from rdflib import Graph, Dataset
from pelix.ipopo.decorators import ComponentFactory, Instantiate, Validate, Provides, Requires, Property

from slugify import slugify

@ComponentFactory("dag-factory")
@Property('_dags_folder', 'dags.folder', '')
@Property('_http_endpoint', 'http.endpoint', '')
@Provides("dagfactory")
@Instantiate("airflow-dagfactory")
class AirflowDAGFactory(DAGFactory):
    
    def __init__(self):
        self._dags_folder = None
        self._http_endpoint = None
    
    @Validate
    def validate(self, context):
        
        
        
        self.__conf = Configuration('./dagfactory/conf/props.json')
        
        self._dags_folder = self.__conf.get_property('dags.folder')
        self._http_endpoint = self.__conf.get_property('http.endpoint')
        
        logging.info(f'DAGS folder is configured to {self._dags_folder}')
        if not os.path.exists(self._dags_folder):
            os.makedirs(self._dags_folder)
            
        dag_confs_path = os.path.join(self._dags_folder, 'configs')
        
        if not os.path.exists(dag_confs_path):
            os.makedirs(dag_confs_path) 
            
        print('DAGFactory is active!')
        
        
    
    '''
    input:
    
        {"data": [
            {"id": "some_id", 
             "filename": "soma_file_name",
             "uri": "some_file_uri"}]
        "rml_refs": [list_or_rml_uris]
        }
    
    '''
    def do_job(self, input: DAGFactoryInput, *args, **kwargs):
        
        
        
        graphs = []
        try:
            if not os.path.exists(self._dags_folder):
                os.makedirs(self._dags_folder)

            dag_id = input.dag_id
            graph_uri = input.graph_uri
            
            templates_searchpath = "./dag_template"
            file_loader = FileSystemLoader(templates_searchpath)
            env = Environment(loader=file_loader)
            template = env.get_template('dagfactoryV2.tpl')
            dag = template.render(graph_uri=graph_uri)
            
            # to save the results
            with open(f'{self._dags_folder}/{dag_id}.py', "w") as fh:
                fh.write(output_from_parsed_template)
            
        except Error as e:
            logging.info(f'Error {e}')
            raise e
        return True
    
    
    def create_dag(self, dag_id: str, dag: Graph):
        if os.path.exists(self._dags_folder):
            out_file = f'{self._dags_folder}/{dag_id}.ttl'
            dag.serialize(out_file, 'text/turtle')
            logging.info(f'Saving DAG {dag_id}.')
            configs_folder = os.path.join(self._dags_folder, 'configs', dag_id)
            
            if not os.path.exists(configs_folder):
                os.makedirs(configs_folder)
                logging.info(f'Created missing folder for dag configs {configs_folder}: {os.path.exists(configs_folder)}.')
                
            return True
        return False
    
    def dags(self) -> Graph:
        if os.path.exists(self._dags_folder):
            dags = Graph()
            dag_files = glob.glob(f'{self._dags_folder}/*.ttl')
            
            for dag_file in dag_files:
                dag = Graph()
                dag.parse(dag_file, format='text/turtle')
                dags += dag
                
            return dags
        return None
    
    def dag_configs(self, id: str) -> Graph:
        
        dag_folder = os.path.join(self._dags_folder, 'configs', id)
        logging.info(f'Loading dag configs from {dag_folder}:  {os.path.exists(dag_folder)}.')
        
        if os.path.exists(dag_folder):
            configs = []
            json_configs = glob.glob(f'{dag_folder}/*.json')
            for json_config in json_configs:
                with open(json_config, 'r') as f:
                    config = json.loads(f.read())
                    metadata = config['metadata']
                    
                    configs.append(metadata)
            return configs
        else:
            return None
        
    def add_dag_config(self, dag_id: str, json_config: dict) -> dict:
        
        folder = os.path.join(self._dags_folder, 'configs', dag_id)
                
        if os.path.exists(folder):
            if 'metadata' in json_config:
                metadata = json_config['metadata']
                if 'id' in metadata:
                    id = metadata['id']
                    
                    id = slugify(id)
                    
                    
                    conffile = os.path.join(folder, f'{id}.json')
                    
                    with open(conffile, 'w') as f:
                        json.dump(json_config, f)
                        
                    return {'status': 'success', 'explanation': 'OK'}
                    
                        
                else:
                    return {'status': 'error', 'explanation': 'Missing required key "id" in the metadata of the JSON provided as input.'}
            else:
                return {'status': 'error', 'explanation': 'Missing required key "metadata" in the JSON provided as input.'}
        else:
            return None
        
    def get_dag_config(self, dag_id: str, config_id: str) -> dict:
        
        
        id = slugify(config_id)
        config_path = os.path.join(self._dags_folder, 'configs', dag_id, f'{id}.json')
                
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                json_obj = json.load(f)
                        
            return json_obj
        else:
            return None
        
        
    def get_dag(self, dag_id: str) -> Graph:
        
        logging.info(f'Loading DAG {dag_id}.')
        dag_file = os.path.join(self._dags_folder, f'{dag_id}.ttl')
        if os.path.exists(dag_file):
            dag = Graph()
            dag.parse(dag_file, format='text/turtle')
            
            return dag
        else:
            return None
    
    