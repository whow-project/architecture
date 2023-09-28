from builtins import staticmethod
import os, gzip

import pandas as pd
from pyrml import RMLConverter, FunctionAlreadyRegisteredException


from abc import ABC, abstractclassmethod
import json
from kg_loader import KnowledgeGraphLoader, KnowledgeGraph
from typing import List, Dict, Callable
import hashlib

from rdflib import Graph, graph

from jinja2 import Environment, FileSystemLoader

import traceback
import shortuuid

class MalfofmedConfigJsonException(Exception):
    def __init__(self, message="The JSON configuration file misses some mandatory attributes. Those can be 'dataset', 'data_folder', 'rml_folder', and 'mappings'."):
        self.message = message
        super().__init__(self.message)
        
class MissingDataFolderException(Exception):
    def __init__(self, folder):
        self.message = "The data folder specified into the JSON configuration file (cf. 'data_folder' attribute) does not exist in the local filesystem: %s"%(folder)
        super().__init__(self.message)
        
class TriplificationException(Exception):
    def __init__(self, rml, files):
        self.message = "An error occurred while processing the RML {0}".format(rml)
        super().__init__(self.message)


class MappingData():
    
    def __init__(self, identifier : str, file_name : str):
        self.__id = identifier
        self.__file_name = file_name
        
    def get_id(self) -> str:
        return self.__id
    
    def get_file_name(self) -> str:
        return self.__file_name

class MappingVariable():
    
    def __init__(self, identifier : str, value):
        self.__id = identifier
        self.__value = value
        
    def get_id(self) -> str:
        return self.__id
    
    def get_value(self):
        return self.__value

class Mapping():
    
    def __init__(self, rml_file : str, input_files : List[MappingData], variables : List[MappingVariable]):
        self.__rml_file = rml_file
        self.__input_files = input_files
        self.__variables = variables
        
    def get_rml_file(self) -> str:
        return self.__rml_file
    
    def get_input_files(self) -> List[MappingData]:
        return self.__input_files
    
    def get_variables(self) -> List[MappingVariable]:
        return self.__variables
    
    def to_dict(self) -> Dict[str,str]:
        
        mapping_dict = dict()
        for mapping_data in self.__input_files:
            mapping_dict.update({mapping_data.get_id(): mapping_data.get_file_name()})
            
        for mapping_variable in self.__variables:
            mapping_dict.update({mapping_variable.get_id(): mapping_variable.get_value()})
            
        return mapping_dict
    
class RDFOutputConfiguration():
    
    def __init__(self, graph_iri, rdf_file_name, rdf_file_serialisation):
        self.__graph_iri = graph_iri
        self.__rdf_file_name = rdf_file_name
        self.__rdf_file_serialisation = rdf_file_serialisation
        
    def get_graph_iri(self):
        return self.__graph_iri
    
    def get_rdf_file_name(self):
        return self.__rdf_file_name
    
    def get_rdf_file_serialisation(self):
        return self.__rdf_file_serialisation

class MappingConfiguration():
    
    def __init__(self, dataset : str, graph_iri : str, rml_folder : str, dest_address : str, dest_folder : str, username : str, passwd : str, dbuser: str, dbpasswd: str, data_folder :str, dirty_data_folder: str, mappings : List[Mapping], rdf_output_configuration : RDFOutputConfiguration, year : int = None):
        self.__dataset = dataset
        self.__graph_iri = graph_iri
        self.__rml_folder = rml_folder
        self.__dest_address = dest_address
        self.__dest_folder = dest_folder
        self.__username = username
        self.__passwd = passwd
        self.__dbuser = dbuser
        self.__dbpasswd = dbpasswd
        self.__data_folder = data_folder
        self.__dirty_data_folder = dirty_data_folder
        self.__mappings = mappings
        self.__rdf_output_configuration = rdf_output_configuration
        self.__year = year
        
    def get_dataset(self):
        return self.__dataset

    def get_graph_iri(self):
        return self.__graph_iri
    
    def get_rml_folder(self):
        return self.__rml_folder

    def get_dest_address(self):
        return self.__dest_address

    def get_dest_folder(self):
        return self.__dest_folder

    def get_username(self):
        return self.__username

    def get_passwd(self):
        return self.__passwd
    
    def get_dbuser(self):
        return self.__dbuser
    
    def get_dbpasswd(self):
        return self.__dbpasswd
    
    def get_data_folder(self):
        return self.__data_folder
    
    def get_dirty_data_folder(self):
        return self.__dirty_data_folder
    
    def get_mappings(self):
        return self.__mappings 
    
    def get_rdf_output_configuration(self):
        return self.__rdf_output_configuration
    
    @staticmethod
    def columns_as_tuple(file, column_num=0):
        df = pd.read_csv(file, sep=None, engine='python', iterator=True)
        sep = df._engine.data.dialect.delimiter
        df.close()
        df = pd.read_csv(file, sep=sep)
        df.set_index(df.columns[0], inplace=True)
        ret = tuple(df.columns[column_num:])
        print(ret)
        return ret
    
    
    @staticmethod
    def load(config_file_path : str, template_vars: Dict[str, str] = dict()):
        
        mapping_configuration = None
        
        if os.path.isabs(config_file_path):
            templates_searchpath = "/"
        else:
            templates_searchpath = "."
        file_loader = FileSystemLoader(templates_searchpath)
        
        env = Environment(loader=file_loader)
        template = env.get_template(config_file_path)
        json_conf = template.render(template_vars)
        
        mapping_conf = json.loads(json_conf)

        if "dataset" in mapping_conf \
            and "graph_iri" in mapping_conf \
            and "data_folder" in mapping_conf \
            and "dirty_data_folder" in mapping_conf \
            and "rml_folder" in mapping_conf \
            and "mappings" in mapping_conf \
            and "rdf_dump_file_name" in mapping_conf \
            and "rdf_dump_file_serialisation" in mapping_conf:

            dataset = mapping_conf["dataset"]
            graph_iri = mapping_conf["graph_iri"]

            rml_path = mapping_conf["rml_folder"]
            global dest_ip
            dest_ip = mapping_conf["dest_address"]
            global dest_path
            dest_path = mapping_conf["dest_folder"]
            global user_str
            user_str = mapping_conf["username"]
            global pass_str
            pass_str = mapping_conf["passwd"]
            global dbuser_str
            dbuser_str = mapping_conf["dbuser"]
            global dbpass_str
            dbpass_str = mapping_conf["dbpasswd"]
            data_path = mapping_conf["data_folder"]
            dirty_data_path = mapping_conf["dirty_data_folder"]
            
            mappings = mapping_conf["mappings"]
            
            if "year" in mapping_conf:
                year = mapping_conf["year"]
            else:
                year = None
            
            rdf_output_configuration = RDFOutputConfiguration(mapping_conf["graph_iri"], mapping_conf["rdf_dump_file_name"], mapping_conf["rdf_dump_file_serialisation"])
            
            maps = []
            for mapping in mappings:
                rml = mapping["rml"]
                
                
                input_files = []
                
                variables = [MappingVariable('dataset', dataset.lower())]
                
                rml_file = os.path.join(rml_path, rml)
                if os.path.exists(rml_file):
                    
                    data = mapping["data"]
                    
                    for file_conf in data:
                        identifier = file_conf["id"]
                        filename = file_conf["file"]
                
                        file_path = os.path.join(data_path, filename)
                        if os.path.exists(file_path):
                            input_files.append(MappingData(identifier, file_path))
                            
                        else:
                            #raise MissingDataFolderException(file_path)
                            print("Missing file {0}".format(file_path))
                            
                    
                    if "variables" in mapping and mapping["variables"]:         
                        _vars = mapping["variables"]
                        
                        for var in _vars:
                            parameter = var["id"]
                            value = var["value"]
                    
                            if parameter and value:
                                try:
                                    variables.append(MappingVariable(parameter, eval(value)))
                                except:
                                    print("Warning: an error occurred while evaluating {0}".format(value))
        
                
                maps.append(Mapping(rml_file, input_files, variables))
            
            mapping_configuration = MappingConfiguration(dataset, graph_iri, rml_path, dest_ip, dest_path, user_str, pass_str, dbuser_str, dbpass_str, data_path, dirty_data_path, maps, rdf_output_configuration, year)
        else:
            raise MalfofmedConfigJsonException()
        
        return mapping_configuration
    
class TriplificationResult():
    
    def __init__(self, graph : Graph, mapping_configuration : MappingConfiguration):
        self.__graph = graph
        self.__mapping_configuration = mapping_configuration
        
    def get_graph(self):
        return self.__graph
    
    def get_mapping_configuration(self):
        return self.__mapping_configuration
        
class Triplifier(ABC):
    
    def __init__(self, dataset, functions_dictionary : Dict[str, Callable] = dict()):
        self._dataset = dataset.lower()
        self._functions_dictionary = functions_dictionary
    
        self._mapping_conf = os.path.join(dataset, 'conf.json')
        
        self._conf_vars : Dict[str, str] = dict()
        
    @abstractclassmethod
    def _dataset_initialisation(self):
        pass
    
    def set_mapping_conf(self, json_config_path: str):
        self._mapping_conf = json_config_path
    
    def triplify(self) -> TriplificationResult:
        
        self._dataset_initialisation()
        
        print(f'The triplifier {type(self)} is using the configuration provided in {self._mapping_conf}.')
        mapping_configuration = MappingConfiguration.load(self._mapping_conf, self._conf_vars)
        
        self._graph_iri = mapping_configuration.get_graph_iri()
        self._rml_path = mapping_configuration.get_rml_folder()
        self._dest_ip = mapping_configuration.get_dest_address()
        self._dest_path = mapping_configuration.get_dest_folder()
        self._user_str = mapping_configuration.get_username()
        self._pass_str = mapping_configuration.get_passwd()
        self._dbuser_str = mapping_configuration.get_dbuser()
        self._dbpass_str = mapping_configuration.get_dbpasswd()
        self._data_path = mapping_configuration.get_data_folder()
        self._dirty_data_path = mapping_configuration.get_dirty_data_folder()
        
        g = None
        
        
        for mapping in mapping_configuration.get_mappings():
            try:
                files = [file.get_file_name() for file in mapping.get_input_files()]
                print("Processing mapping %s to files %s."%(mapping.get_rml_file(), files))
                rml_converter = RMLConverter.get_instance()
                
                for function_name in self._functions_dictionary:
                    try:
                        rml_converter.register_function(function_name, self._functions_dictionary[function_name])
                    except FunctionAlreadyRegisteredException as e:
                        print(f'Warning: The function {function_name} has been already registered. It will be not replaced.')
        
                g_tmp = rml_converter.convert(mapping.get_rml_file(), False, mapping.to_dict())
                
                if g:
                    g = KnowledgeGraph.add_all(g, g_tmp)
                    #g += g_tmp
                else:
                    g = g_tmp
                
                rml_converter.reset()
                
				
            except Exception as e:
                print("An error occurred while p mapping %s to files %s."%(mapping.get_rml_file(), files))
                print( "EXCEPTION FORMAT PRINT:\n{}".format( e ) )
                print( "EXCEPTION TRACE  PRINT:\n{}".format( "".join(traceback.format_exception(type(e), e, e.__traceback__))))
                                
        return TriplificationResult(g, mapping_configuration)
    
class TriplificationManager():
    
    def __init__(self, triplifier : Triplifier, kg_loader : KnowledgeGraphLoader = None, path_to_json_config:str = None):
        
        self.__triplifier = triplifier
        
        if path_to_json_config:
            self.__triplifier.set_mapping_conf(path_to_json_config)    
        
        self.__kg_loader = kg_loader
        
        
    #def do_triplification(self):
    def do_triplification(self, bool_upload, bool_update):
        try:
            result = self.__triplifier.triplify()
            
            print(f'The RDF graph contains {len(result.get_graph())} triples')
        except MissingDataFolderException as e:
            print("MissingDataFolderException error: {0}".format(e))
            result = None
             
        if result and self.__kg_loader:
            rdf_output_configuration = result.get_mapping_configuration().get_rdf_output_configuration()
            #self.__kg_loader.toLoad_toDelete(result.get_graph(), rdf_output_configuration.get_rdf_file_name(), result.get_mapping_configuration().get_dataset().lower())
            file_triple, file_load, file_delete = self.__kg_loader.toLoad_toDelete_2(result.get_graph(), rdf_output_configuration.get_rdf_file_name(), result.get_mapping_configuration().get_dataset().lower())


            dataset_name = str(result.get_mapping_configuration().get_dataset().lower())
            graph_name = str(result.get_mapping_configuration().get_graph_iri().lower())
            
            if bool_upload:
                self.__kg_loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_triple), os.path.join(str(dest_path),str(file_triple.replace(file_triple.split('/')[-1],''))))

                if os.path.exists(file_load):
                    self.__kg_loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_load), os.path.join(str(dest_path),str(file_load.replace(file_load.split('/')[-1],''))))
                
                if os.path.exists(file_delete):
                    self.__kg_loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_delete), os.path.join(str(dest_path),str(file_delete.replace(file_delete.split('/')[-1],''))))

            if bool_update:
                #check if load file is not empty
                if os.path.exists(file_load):
                    with gzip.open(file_load, 'r') as f:
                        read_f = f.read()
                    if len(read_f) != 1:
                        sql_load = self.__kg_loader.sparql_bulk_load(str(dest_ip), str(dbuser_str), str(dbpass_str), str(file_load),str(dest_path),graph_name,run_load=False)

                        self.__kg_loader.remote_isql(str(dest_ip),str(user_str),str(pass_str),str(dbuser_str),str(dbpass_str),sql_load,str(dest_path))


                #check if del file is not empty
                if os.path.exists(file_delete):
                    with gzip.open(file_delete, 'r') as f:
                        read_f = f.read()
                    if len(read_f) != 1:
                        sql_del = self.__kg_loader.sparql_delete(str(dest_ip), str(dbuser_str), str(dbpass_str),str(file_delete),graph_name,run_load=False)

                        self.__kg_loader.remote_isql(str(dest_ip),str(user_str),str(pass_str),str(dbuser_str),str(dbpass_str),sql_del,str(dest_path))
           
        

class UtilsFunctions():

    @staticmethod
    def digest(s):
        hash = hashlib.md5(s.encode())
        return hash.hexdigest()
    
    @staticmethod
    def short_uuid(string: str):
    
        return shortuuid.uuid(string)[:8]

    @staticmethod
    def po_assertion_uuid(predicate: str, _object: str):
    
        return UtilsFunctions.short_uuid(predicate + _object)
    
