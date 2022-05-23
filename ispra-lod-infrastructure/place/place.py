import os
import json
import gzip
import pandas as pd
from subprocess import Popen, run
from jinja2 import Environment, FileSystemLoader, Template
from rdflib import Graph
from rdflib.parser import StringInputSource
#from load_delete import toLoad_toDelete
from kg_loader import KnowledgeGraphLoader
from pyrml import TermUtils, RMLConverter
from utf8_converter import UTF8Converter
from typing import Dict


def metropolitan_city(istat):
    metropolitan_cities = ["001", "010", "015", "027", "037", "048", "058", "063", "072", "080", "082", "083", "087", "092"]
    
    out = None
    if istat in metropolitan_cities:
        out = "metropolitancity/" + str(2) + istat[1:]
    else:
        out = "province/" + istat
    
    return out

def metropolitan_city_code_2(istat, year):
    if int(year) < 2015:
        return istat

    csv_file = "data/place/v2/dirtydata/metropolitan_cities.csv"
    df_mc = pd.read_csv(csv_file, delimiter=';')
    mc_value = istat
    if (int(istat) in df_mc['PROV_CODE'].values):
        mc_value = (str(df_mc['MC_CODE'][df_mc['PROV_CODE']==int(istat)].values[0]))

    return mc_value
        
def metropolitan_city_type(istat, year):
    if int(year) < 2015:
        return "Province"

    csv_file = "data/place/v2/dirtydata/metropolitan_cities.csv"
    df_mc = pd.read_csv(csv_file, delimiter=';')
        
    out = None
    if (int(istat) in df_mc['PROV_CODE'].values):
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


def print_delete(file_toDel, file_update, cat):

    delG = Graph()

    str_graph = 'https://dati.isprambiente.it/ld/place/'

    graph_toDel = Graph()
    graph_update = Graph()

    print ('Reading toDel triples ...')
    with gzip.open(file_toDel, 'rb') as f:
        str_triple_todel = f.read()
    graph_toDel.parse(data=str_triple_todel, format='nt11')

    sql_file = 'del_list_' + cat + '.sql'

    if not len(graph_toDel):
        return sql_file
    #    print ('No triples to delete for ' + cat + '!')
    #    return 0

    print ('Reading updated triples ...')
    with gzip.open(file_update, 'rb') as f:
        str_triple_update = f.read()
    graph_update.parse(data=str_triple_update, format='nt11')


    print ('Parsing toDel graph ...')
    for s, p, o in graph_toDel:
        if (s, p, None) in graph_update:
            delG.add((s, p, o))

    with open(sql_file, 'w') as sql_del:
        print("DELETE FROM LOAD_LIST;", file=sql_del)
        for dd in (delG.serialize(format='nt11').splitlines()):
            if dd: print ('SPARQL DELETE DATA { GRAPH <' + str_graph + '> { ' + dd + '} } ;', file=sql_del)
        print("RDF_LOADER_RUN();", file=sql_del)
        print("CHECKPOINT;", file=sql_del)
        print("COMMIT WORK;", file=sql_del)
        print("CHECKPOINT;", file=sql_del)

    return sql_file


def placeRDF(config_file_path : str, bool_upload : bool, bool_update : bool):
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
    rml_converter.register_function("metropolitan_city_code_2", metropolitan_city_code_2)
    g = rml_converter.convert(StringInputSource(rml_mapping.encode('utf-8')))

    #toLoad_toDelete(g, "provinces", "places")
    file_tripleP, file_loadP, file_deleteP = loader.toLoad_toDelete_2(g, "provinces", "place")

    #municipalities
    utf8_converter = UTF8Converter('data/place/v2/dirtydata','data/place/v2/data')
    utf8_converter.convert_single_file('comuni_soppressi.csv')
    
    with open("data/place/v2/data/comuni_soppressi.csv","rt") as f:
        lines = f.readlines()
    lines[0] = lines[0].replace(' ','_') #remove empty spaces from header
    with open("data/place/v2/data/comuni_soppressi.csv","wt") as ff:
        ff.writelines(lines)

    template = env.get_template('place/municipalities_map.ttl')
    rml_mapping = template.render()

    rml_converter = RMLConverter()
    rml_converter.register_function("metropolitan_city", metropolitan_city)
    rml_converter.register_function("metropolitan_city_type", metropolitan_city_type)
    rml_converter.register_function("metropolitan_city_code", metropolitan_city_code)
    rml_converter.register_function("metropolitan_city_code_2", metropolitan_city_code_2)
    g = rml_converter.convert(StringInputSource(rml_mapping.encode('utf-8')))
    
    #toLoad_toDelete(g, "municipalities", "places")
    file_tripleM, file_loadM, file_deleteM = loader.toLoad_toDelete_2(g, "municipalities", "place")

    if bool_upload:
        #summary triples
        loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_tripleR), os.path.join(str(dest_path),str(file_tripleR.replace(file_tripleR.split('/')[-1],''))))
        loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_tripleP), os.path.join(str(dest_path),str(file_tripleP.replace(file_tripleP.split('/')[-1],''))))
        loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_tripleM), os.path.join(str(dest_path),str(file_tripleM.replace(file_tripleM.split('/')[-1],''))))

        #to load and to delete triples
        if os.path.exists(file_loadR):
            loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_loadR), os.path.join(str(dest_path),str(file_loadR.replace(file_loadR.split('/')[-1],''))))
        if os.path.exists(file_loadP):
            loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_loadP), os.path.join(str(dest_path),str(file_loadP.replace(file_loadP.split('/')[-1],''))))
        if os.path.exists(file_loadM):
            loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_loadM), os.path.join(str(dest_path),str(file_loadM.replace(file_loadM.split('/')[-1],''))))

        if os.path.exists(file_deleteR):
            loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_deleteR), os.path.join(str(dest_path),str(file_deleteR.replace(file_deleteR.split('/')[-1],''))))
        if os.path.exists(file_deleteP):
            loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_deleteP), os.path.join(str(dest_path),str(file_deleteP.replace(file_deleteP.split('/')[-1],''))))
        if os.path.exists(file_deleteM):
            loader.upload_triple_file(str(dest_ip), str(user_str), str(pass_str), str(file_deleteM), os.path.join(str(dest_path),str(file_deleteM.replace(file_deleteM.split('/')[-1],''))))


    if bool_update:
        if os.path.exists(file_loadR):
            loader.sparql_bulk_load(str(dest_ip),str(file_loadR),str(dest_path),"place")
        if os.path.exists(file_loadP):
            loader.sparql_bulk_load(str(dest_ip),str(file_loadP),str(dest_path),"place")
        if os.path.exists(file_loadM):
            loader.sparql_bulk_load(str(dest_ip),str(file_loadM),str(dest_path),"place")

        if os.path.exists(file_deleteR):
            print ('deleting regions ...')
            file_delR = print_delete(file_deleteR,str(file_tripleR),"regions")
            command = "isql-vt " + str(dest_ip)+":1111 " + "dba " + "dba " + "VERBOSE=OFF " + " 'EXEC=status()' " + file_delR
            run([command], shell=True)
        if os.path.exists(file_deleteP):
            print ('deleting provinces ...')
            file_delP = print_delete(file_deleteP,str(file_tripleP),"provinces")
            command = "isql-vt " + str(dest_ip)+":1111 " + "dba " + "dba " + "VERBOSE=OFF " + " 'EXEC=status()' " + file_delP
            run([command], shell=True)
        if os.path.exists(file_deleteM):
            print ('deleting municipalities ...')
            file_delM = print_delete(file_deleteM,str(file_tripleM),"municipalities")
            command = "isql-vt " + str(dest_ip)+":1111 " + "dba " + "dba " + "VERBOSE=OFF " + " 'EXEC=status()' " + file_delM
            run([command], shell=True)