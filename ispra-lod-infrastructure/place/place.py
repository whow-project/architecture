import os
import json
import gzip
import pandas as pd
from paramiko import SSHClient, AutoAddPolicy
from shapely.wkt import loads
from subprocess import Popen, run
from jinja2 import Environment, FileSystemLoader, Template
from rdflib import Graph, URIRef
from rdflib.namespace import RDF
from rdflib.parser import StringInputSource
from kg_loader import KnowledgeGraphLoader
from pyrml import TermUtils, RMLConverter
from typing import Dict
from utils import Utils


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

def get_long(shp_point):
    pt_wkt = loads(str(shp_point))
    try:
        value = str(round(float(pt_wkt.x),5))
    
    except ValueError:
        value = str(pt_wkt.x)

    return value

def get_lat(shp_point):
    pt_wkt = loads(str(shp_point))
    try:
        value = str(round(float(pt_wkt.y),5))
    
    except ValueError:
        value = str(pt_wkt.y)

    return value


def exec_remote_command(ipaddr,user,passwd,command):
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(AutoAddPolicy())

    try:
        ssh.connect(hostname=ipaddr, port='22', username=user, password=passwd)
    except BlockingIOError:
        print('Resource unaivailable, check your inputs in the config file!')
        return 0
    
    stdin, stdout, stderr = ssh.exec_command(command)
    for line in stdout.readlines():
        print (line)
    ssh.close()


def remote_isql(ipaddr,user,passwd,dbuser,dbpasswd,sqlfile,destfolder):

    loader = KnowledgeGraphLoader()

    remote_sql_path = os.path.join(destfolder,'sql')

    loader.upload_triple_file(ipaddr,user,passwd,sqlfile,remote_sql_path)

    remote_sql_file = os.path.join(remote_sql_path, sqlfile.split('/')[-1])

    remote_command = "isql 1111 " + str(dbuser) + " " + str(dbpasswd) +  " " + remote_sql_file

    exec_remote_command(ipaddr,user,passwd,remote_command)


def print_delete(file_toDel, file_update, cat):

    delG = Graph()

    str_graph = 'https://w3id.org/italia/env/ld/place/'

    graph_toDel = Graph()
    graph_update = Graph()

    print ('Reading toDel triples ...')
    with gzip.open(file_toDel, 'rb') as f:
        str_triple_todel = f.read()
    graph_toDel.parse(data=str_triple_todel, format='nt11')

    sql_dir = 'sql'
    if not os.path.exists(sql_dir):
        os.makedirs(sql_dir)
    sql_file = os.path.join(sql_dir,'del_list_' + cat + '.sql')
    len_batch = 500

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
        #Divide deletes in batches
        for sublist in list(Utils.chunks(delG.serialize(format='nt11').splitlines(),len_batch)):
            print ('SPARQL DELETE DATA { GRAPH <' + str_graph + '> {', file=sql_del)
            for dd in sublist:
                if dd: print (dd, file=sql_del)
            print ('} } ;', file=sql_del)
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
    dbuser_str = mapping_conf["dbuser"]
    dbpass_str = mapping_conf["dbpasswd"]
    graph_str = mapping_conf["graph_iri"]

    print("Starting preprocessing ...")
    KnowledgeGraphLoader.convert_utf8('data/place/v2/dirtydata','data/place/v2/data')
    print("\t preprocessing complete.")
    
    #regions
    template = env.get_template('data/place/v2/rml/regions_map.ttl')
    rml_mapping = template.render()

    rml_converter = RMLConverter()
    g = rml_converter.convert(StringInputSource(rml_mapping.encode('utf-8')))

    #toLoad_toDelete (g, "regions", "places")
    file_tripleR, file_loadR, file_deleteR = loader.toLoad_toDelete_2(g, "regions", "place")
    

    #provinces
    template = env.get_template('data/place/v2/rml/provinces_map.ttl')
    rml_mapping = template.render()

    rml_converter = RMLConverter()
    rml_converter.register_function("metropolitan_city", metropolitan_city)
    rml_converter.register_function("metropolitan_city_type", metropolitan_city_type)
    rml_converter.register_function("metropolitan_city_code", metropolitan_city_code)
    rml_converter.register_function("metropolitan_city_code_2", metropolitan_city_code_2)
    g = rml_converter.convert(StringInputSource(rml_mapping.encode('utf-8')))

    #Fix rdf:type
    print ('Fixing rdf:type ...')
    for s, p, o in g.triples((None, RDF.type, URIRef('https://w3id.org/italia/env/onto/place/province'))):
        g.remove((s, p, o))
        g.add((s, RDF.type, URIRef('https://w3id.org/italia/env/onto/place/Province')))
    for s, p, o in g.triples((None, RDF.type, URIRef('https://w3id.org/italia/env/onto/place/metropolitancity'))):
        g.remove((s, p, o))
        g.add((s, RDF.type, URIRef('https://w3id.org/italia/env/onto/place/MetropolitanCity')))

    #toLoad_toDelete(g, "provinces", "places")
    file_tripleP, file_loadP, file_deleteP = loader.toLoad_toDelete_2(g, "provinces", "place")

    #municipalities    
    with open("data/place/v2/data/comuni_soppressi.csv","rt") as f:
        lines = f.readlines()
    lines[0] = lines[0].replace(' ','_') #remove empty spaces from header
    with open("data/place/v2/data/comuni_soppressi.csv","wt") as ff:
        ff.writelines(lines)

    template = env.get_template('data/place/v2/rml/municipalities_map.ttl')
    rml_mapping = template.render()

    rml_converter = RMLConverter()
    rml_converter.register_function("metropolitan_city", metropolitan_city)
    rml_converter.register_function("metropolitan_city_type", metropolitan_city_type)
    rml_converter.register_function("metropolitan_city_code", metropolitan_city_code)
    rml_converter.register_function("metropolitan_city_code_2", metropolitan_city_code_2)
    rml_converter.register_function("get_long", get_long)
    rml_converter.register_function("get_lat", get_lat)
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

            sql_loadR = loader.sparql_bulk_load(str(dest_ip),str(dbuser_str),str(dbpass_str),str(file_loadR),str(dest_path),graph_str,run_load=False)

            remote_isql(str(dest_ip),str(user_str),str(pass_str),str(dbuser_str),str(dbpass_str),sql_loadR,str(dest_path))


        if os.path.exists(file_loadP):
            
            sql_loadP = loader.sparql_bulk_load(str(dest_ip),str(dbuser_str),str(dbpass_str),str(file_loadP),str(dest_path),graph_str,run_load=False)

            remote_isql(str(dest_ip),str(user_str),str(pass_str),str(dbuser_str),str(dbpass_str),sql_loadP,str(dest_path))


        if os.path.exists(file_loadM):
            
            sql_loadM = loader.sparql_bulk_load(str(dest_ip),str(dbuser_str),str(dbpass_str),str(file_loadM),str(dest_path),graph_str,run_load=False)

            remote_isql(str(dest_ip),str(user_str),str(pass_str),str(dbuser_str),str(dbpass_str),sql_loadM,str(dest_path))

        #Different function, to preserve dead entities
        if os.path.exists(file_deleteR):
            print ('deleting regions ...')
            file_delR = print_delete(file_deleteR,str(file_tripleR),"regions")
            #command = "isql.8.3 " + dest_ip + ":1111 " + str(dbuser_str) + " " + str(dbpass_str) + " " + file_delR
            #if os.path.exists(file_delR):
            #    run([command], shell=True)
            remote_isql(str(dest_ip),str(user_str),str(pass_str),str(dbuser_str),str(dbpass_str),file_delR,str(dest_path))
        if os.path.exists(file_deleteP):
            print ('deleting provinces ...')
            file_delP = print_delete(file_deleteP,str(file_tripleP),"provinces")
            #command = "isql.8.3 " + dest_ip + ":1111 " + str(dbuser_str) + " " + str(dbpass_str) + " " + file_delP
            #if os.path.exists(file_delP):
            #    run([command], shell=True)
            remote_isql(str(dest_ip),str(user_str),str(pass_str),str(dbuser_str),str(dbpass_str),file_delP,str(dest_path))
        if os.path.exists(file_deleteM):
            print ('deleting municipalities ...')
            file_delM = print_delete(file_deleteM,str(file_tripleM),"municipalities")
            #command = "isql.8.3 " + dest_ip + ":1111 " + str(dbuser_str) + " " + str(dbpass_str) + " " + file_delM
            #if os.path.exists(file_delM):
            #    run([command], shell=True)
            remote_isql(str(dest_ip),str(user_str),str(pass_str),str(dbuser_str),str(dbpass_str),file_delM,str(dest_path))