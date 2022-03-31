import os
import json
from jinja2 import Environment, FileSystemLoader, Template
from rdflib.parser import StringInputSource
#from load_delete import toLoad_toDelete
from kg_loader import KnowledgeGraphLoader
from pyrml import TermUtils, RMLConverter
from typing import Dict


def metropolitan_city(istat):
    metropolitan_cities = ["001", "010", "015", "027", "037", "048", "058", "063", "072", "080", "082", "083", "087", "092"]
    
    out = None
    if istat in metropolitan_cities:
        out = "metropolitancity/" + str(2) + istat[1:]
    else:
        out = "province/" + istat
    
    return out
        
def metropolitan_city_type(istat):
    metropolitan_cities = ["001", "010", "015", "027", "037", "048", "058", "063", "072", "080", "082", "083", "087", "092"]
        
    out = None
    if istat in metropolitan_cities:
        out = "MetropolitanCity"
    else:
        out = "Province"
    return out

def metropolitan_city_code(istat):
    metropolitan_cities = ["001", "010", "015", "027", "037", "048", "058", "063", "072", "080", "082", "083", "087", "092"]

    out = None
    if istat in metropolitan_cities:
        out = str(2) + istat[1:]
    else:
        out = istat

    return out

def placeRDF(config_file_path : str, bool_upload : bool):
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)

    loader = KnowledgeGraphLoader()

    template_vars : Dict[str, str] = dict()
    if os.path.isabs(config_file_path):
        templates_searchpath = "/"
    else:
        templates_searchpath = "."
    file_loader = FileSystemLoader(templates_searchpath)
    
    env = Environment(loader=file_loader)
    template = env.get_template(config_file_path)
    json_conf = template.render(template_vars)
    mapping_conf = json.loads(json_conf)

    dest_ip = mapping_conf["dest_address"]
    dest_path = mapping_conf["dest_folder"]
    user_str = mapping_conf["username"]
    pass_str = mapping_conf["passwd"]

    
    #regions
    template = env.get_template('place/regions_map.ttl')
    rml_mapping = template.render()
    
    rml_converter = RMLConverter()
    g = rml_converter.convert(StringInputSource(rml_mapping.encode('utf-8')))

    #toLoad_toDelete (g, "regions", "places")
    file_tripleR, file_loadR, file_deleteR = loader.toLoad_toDelete_2(g, "regions", "place")
    

    #provinces
    template = env.get_template('place/provinces_map.ttl')
    rml_mapping = template.render()

    rml_converter = RMLConverter()
    rml_converter.register_function("metropolitan_city", metropolitan_city)
    rml_converter.register_function("metropolitan_city_type", metropolitan_city_type)
    rml_converter.register_function("metropolitan_city_code", metropolitan_city_code)
    g = rml_converter.convert(StringInputSource(rml_mapping.encode('utf-8')))

    #toLoad_toDelete(g, "provinces", "places")
    file_tripleP, file_loadP, file_deleteP = loader.toLoad_toDelete_2(g, "provinces", "place")

    #municipalities
    template = env.get_template('place/municipalities_map.ttl')
    rml_mapping = template.render()

    rml_converter = RMLConverter()
    rml_converter.register_function("metropolitan_city", metropolitan_city)
    rml_converter.register_function("metropolitan_city_type", metropolitan_city_type)
    rml_converter.register_function("metropolitan_city_code", metropolitan_city_code)
    g = rml_converter.convert(StringInputSource(rml_mapping.encode('utf-8')))
    
    #toLoad_toDelete(g, "municipalities", "places")
    file_tripleM, file_loadM, file_deleteM = loader.toLoad_toDelete_2(g, "municipalities", "place")

    if bool_upload:
        loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_tripleR), os.path.join(str(dest_path),str(file_tripleR)))
        loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_tripleP), os.path.join(str(dest_path),str(file_tripleP)))
        loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_tripleM), os.path.join(str(dest_path),str(file_tripleM)))

        if os.path.exists(file_loadR):
            loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_loadR), os.path.join(str(dest_path), str(file_loadR)))
        if os.path.exists(file_loadP):
            loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_loadP), os.path.join(str(dest_path), str(file_loadP)))
        if os.path.exists(file_loadM):
            loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_loadM), os.path.join(str(dest_path), str(file_loadM)))
        if os.path.exists(file_deleteR):
            loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_deleteR), os.path.join(str(dest_path), str(file_deleteR)))
        if os.path.exists(file_deleteP):
            loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_deleteP), os.path.join(str(dest_path), str(file_deleteP)))
        if os.path.exists(file_deleteM):
            loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_deleteM), os.path.join(str(dest_path), str(file_deleteM)))