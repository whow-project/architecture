import os, csv

import clevercsv
from jinja2 import Environment, FileSystemLoader, Template
from rdflib.parser import StringInputSource

from pyrml.pyrml import TermUtils, RMLConverter
from triplification import Triplifier, UtilsFunctions
from typing import Dict, Callable
import re



class RendisTriplifier(Triplifier):
    
    '''
        The following protected attributes are declared by the superclass Triplifier:
         - self._dataset -> the name of the dataset
         - self._rml_path -> the path to the RML mapping files
         - self._data_path -> the path to CSV data files.
    '''
    def __init__(self):
        
        functions_dictionary = {
            'lower_case': lower_case,
            'broader_entity': broader_entity,
            'boolean': boolean,
            'digest': UtilsFunctions.short_uuid,
            'po_assertion_uuid': UtilsFunctions.po_assertion_uuid,
            'responsible_agent_role': responsible_agent_role,
            'responsible_role': responsible_role
            }
        
        super().__init__('rendis', functions_dictionary)
        self._dirty_data_path = os.path.join('rendis', 'v2', 'dirtydata')
        
        
    def _dataset_initialisation(self) -> None:
        print("Rendis data cleansing...")
        self.__clean_data()
        print("\t data cleansing completed.")
        print("Rendis preprocessing...")
        self.__preprocess()
        print("\t preprocessing completed.")
        
    
    def get_graph_iri(self):
        return 'https://dati.isprambiente.it/ld/rendis'    
    
    def __clean_data(self) -> None:
        
        for file in [f for f in os.listdir(self._dirty_data_path) if f.endswith('.csv')]:
            with open(os.path.join(self._dirty_data_path, file), "r", encoding="latin-1") as csvfile:
                if "lotto_passi" in file:
                    cleaned = csv.reader(csvfile, delimiter=";", quotechar='"', escapechar="\\")
                else:
                    cleaned = clevercsv.reader(csvfile, delimiter=";", quotechar='"', escapechar="\\")
                rows = list(cleaned)
                data = []
                for x in rows[1:]:
                    rowdict = {}
                    for pos,y in enumerate(x):
                        if "\n" in y:
                            y = y.replace("\n", "")
                        if y.lower() == "na" or y.lower() == "none" or y.lower() == "non disponibile":
                            y = ""
                        if file == 'lotto_passi.csv' and pos == 'data':
                            y = y.replace(' ', 'T')
                        rowdict[rows[0][pos]] = y
                    data.append(rowdict)
    
            with open(os.path.join(self._data_path, file), "w", newline='', encoding="utf8") as finalfile:
                writer = csv.DictWriter(finalfile, fieldnames=data[0].keys(), delimiter=";")
                writer.writeheader()
                for x in data:
                    writer.writerow(x)
                    
    
    def __preprocess(self) -> None:
    
        #dissesti = dict()
        metropolitan_cities = ["001", "010", "015", "027", "037", "048", "058", "063", "072", "080", "082", "083", "087", "092"]
        
        '''
        with open(os.path.join(self._data_path, "classificazione_dissesto.csv"), "r+", encoding="utf-8") as classificazione_dissesto:
            reader = csv.DictReader(classificazione_dissesto, delimiter=";")
            data = [dict(r) for r in reader]
            
            for row in data:
                dissesto = {row["DISSESTO_IT"]:
                    {
                        "IT": row["DISSESTO_IT"],
                        "EN": row["DISSESTO_EN"],
                        "DBPEDIA": row["DBPEDIA"],
                        "WIKIDATA": row["WIKIDATA"],
                    }
                }
                
                dissesti.update(dissesto)
        '''
        
        iter_passi_data = []
        iter_first_last_steps = []
        with open(os.path.join(self._data_path, "iter_passi.csv"), "r+", encoding="utf-8") as iter_passi:
            reader = csv.DictReader(iter_passi, delimiter=";")
            data = [dict(r) for r in reader]
            id_iter_prev = None
            id_passo_prev = None
            firt_step = None
            for row in data:
                id_iter = row['id_iter']
                id_passo = row['id_passo']
                if id_iter == id_iter_prev:
                    row['id_passo_prec'] = id_passo_prev
                else:
                    row['id_passo_prec'] = ''
                    
                    if id_passo_prev:
                        iter_first_last_steps.append({'id_iter': id_iter_prev, 'first': firt_step, 'last': id_passo_prev})
                    
                    firt_step = id_passo
                
                id_iter_prev = id_iter
                id_passo_prev = id_passo
                iter_passi_data.append(row)
            
            iter_first_last_steps.append({'id_iter': id_iter_prev, 'first': firt_step, 'last': id_passo_prev})
                
        with open(os.path.join(self._data_path, "iter_passi.csv"), "w+", newline='', encoding="utf8") as newfile:
            writer = csv.DictWriter(newfile, fieldnames=iter_passi_data[0].keys(), delimiter=";")
            writer.writeheader()
            for x in iter_passi_data:
                writer.writerow(x)
                
        with open(os.path.join(self._data_path, "iter_passi_first_last.csv"), "w+", newline='', encoding="utf8") as newfile:
            writer = csv.DictWriter(newfile, fieldnames=iter_first_last_steps[0].keys(), delimiter=";")
            writer.writeheader()
            for x in iter_first_last_steps:
                writer.writerow(x)
            
                
        with open(os.path.join(self._data_path, "info_lod.csv"), "r+", encoding="utf-8") as lodfile:
            reader = csv.DictReader(lodfile, delimiter=";")
            data = [dict(r) for r in reader]
            with open(os.path.join(self._data_path, "tipo_affid.csv"), "r+", encoding="utf-8") as affidfile:
                reader = csv.DictReader(affidfile, delimiter=";")
                affid_data = [dict(r) for r in reader]
    
                for row in data:
                    row["_URL_scheda_lotto"] = url_extract(row["_URL_scheda_lotto"])
                    row["URL_scheda_lotto_QE"] = url_extract(row["URL_scheda_lotto_QE"])
                    row["_URL_scheda_int"] = url_extract(row["_URL_scheda_int"])
                    row["ID_URL_scheda_intervento_decreto"] = url_extract(row["ID_URL_scheda_intervento_decreto"]).replace(" ","_")
    
                    if row["_LG_G_pos_json"]:
                        coordinates = row["_LG_G_pos_json"].replace('"', "").replace('{type:MultiPoint,coordinates:', "").replace('}', "")
                        coordinates = coordinates.replace("[", "(").replace("]", ")")
                        coordinates = re.sub(r"(\d+\.\d+),(\d+\.\d+)", r"\1 \2", coordinates)
                        coordinates = coordinates.replace("[", "(").replace("]", ")")
                        if "," in coordinates:
                            row["POINT"] = "MULTIPOINT"+ coordinates
                        else:
                            coordinates = coordinates.replace("((", "(").replace("))", ")")
                            row["POINT"] = "POINT"+ coordinates
                            
                        
                    for a in affid_data:
                        if a["codice"] == row["L_modAggiudicazione"]:
                            row["L_modAggiudicazione"] = a["descrizione"]
                    
                    ente_proponente = row["_TE_E_FROM_I_ente_proponente"]
                    
                    ente_proponente_type = None
                    ente_proponente_type_uri = None
                    label_ente_proponente = ""
                    if ente_proponente.startswith("Comune - "):
                        ente_proponente_type = "municipality"
                        ente_proponente_type_uri = "https://dati.isprambiente.it/ontology/location/Municipality"
                        #ente_proponente = ente_proponente.replace("Comune - ", "")
                    elif ente_proponente.startswith("Provincia - "):
                    
                        ente_proponente_id = row["E_FROM_I_idEnteProp"]
                        
                        if ente_proponente_id in metropolitan_cities:
                            ente_proponente_type = "metropolitancity"
                            ente_proponente_type_uri = "https://dati.isprambiente.it/ontology/location/MetropolitanCity"
                        else:
                            ente_proponente_type = "province"
                            ente_proponente_type_uri = "https://dati.isprambiente.it/ontology/location/Province"
                    elif ente_proponente.startswith("Regione - "):
                    
                        ente_proponente_type = "region"
                        ente_proponente_type_uri = "https://dati.isprambiente.it/ontology/location/Region"
                    else:
                        ente_proponente_type = "organisation"
                        label_ente_proponente = ente_proponente
                        ente_proponente_type_uri = "https://dati.isprambiente.it/ontology/core/Organisation"
                        
                    row.update({"ENTE_PROPONENTE_LABEL": label_ente_proponente})
                    row.update({"ENTE_PROPONENTE_TYPE": ente_proponente_type})
                    row.update({"ENTE_PROPONENTE_TYPE_URI": ente_proponente_type_uri})
                    
                    
                    ente_attuatore = row["_TE_E_FROM_L_Ente attuatore"]
                    
                    ente_attuatore_type = None
                    ente_attuatore_type_uri = None
                    label_ente_attuatore = ""
                    if ente_attuatore.startswith("Comune - "):
                        ente_attuatore_type = "municipality"
                        ente_attuatore_type_uri = "https://dati.isprambiente.it/ontology/location/Municipality"
                        
                    elif ente_attuatore.startswith("Provincia - "):
                    
                        ente_attuatore_id = row["E_FROM_L_idEnteAttuat"]
                        
                        if ente_attuatore_id in metropolitan_cities:
                            ente_attuatore_type = "metropolitancity"
                            ente_attuatore_type_uri = "https://dati.isprambiente.it/ontology/location/MetropolitanCity"
                        else:
                            ente_attuatore_type = "province"
                            ente_attuatore_type_uri = "https://dati.isprambiente.it/ontology/location/Province"
                    elif ente_attuatore.startswith("Regione - "):
                    
                        ente_attuatore_type = "region"
                        ente_attuatore_type_uri = "https://dati.isprambiente.it/ontology/location/Region"
                    else:
                        ente_attuatore_type = "organisation"
                        label_ente_attuatore = ente_proponente
                        ente_attuatore_type_uri = "https://dati.isprambiente.it/ontology/core/Organisation"
                        
                    row.update({"ENTE_ATTUATORE_LABEL": label_ente_attuatore})
                    row.update({"ENTE_ATTUATORE_TYPE": ente_attuatore_type})
                    row.update({"ENTE_ATTUATORE_TYPE_URI": ente_attuatore_type_uri})
                    
                    gazzetta_ufficiale = row["D_gazzettaUfficiale"]
                    
                    if gazzetta_ufficiale and gazzetta_ufficiale != '' and gazzetta_ufficiale != 'non disponibilie':
                    
                        pattern = '((G\.U\.)|(Serie Generale)) n\.? ([0-9]+) del ([0-9]+)(/|-)([0-9]+)(/|-)([0-9]+)'
                        p = re.compile(pattern)
                        match = p.match(gazzetta_ufficiale)
                        gazzetta_numero = match.group(4)
                        gazzetta_giorno = match.group(5)
                        gazzetta_mese = match.group(7)
                        gazzetta_anno = match.group(9)
                        
                        gazzetta_url = 'https://www.gazzettaufficiale.it/gazzetta/serie_generale/caricaDettaglio?dataPubblicazioneGazzetta=%s-%s-%s&numeroGazzetta=%s'%(gazzetta_anno, gazzetta_mese, gazzetta_giorno, gazzetta_numero)
                        
                        row["D_gazzettaUfficiale"] = gazzetta_url
                        
                    else:
                        row["D_gazzettaUfficiale"] = ''
                        
                    if row["L_QE_incongruenzaFin"] == 't':
                        row["L_QE_incongruenzaFin"] = 'https://dati.isprambiente.it/ld/rendis/concept/financially_incongruent'
                    else:
                        row["L_QE_incongruenzaFin"] = 'https://dati.isprambiente.it/ld/rendis/concept/financially_congruent'
                        
                    if row["L_QE_incongruenzaProg"] == 't':
                        row["L_QE_incongruenzaProg"] = 'https://dati.isprambiente.it/ld/rendis/concept/projectually_incongruent'
                    else:
                        row["L_QE_incongruenzaProg"] = 'https://dati.isprambiente.it/ld/rendis/concept/projectually_congruent'
                        
                    '''
                    row.update({"TIPO_DISSESTO_IT": row["_FROM_I_Tipo_dissesto"]})
                    del row["_FROM_I_Tipo_dissesto"]
                    
                    if row["TIPO_DISSESTO_IT"] in dissesti:
                        tipo_dissesto = dissesti[row["TIPO_DISSESTO_IT"]]
                        print(tipo_dissesto)
                        row.update({"TIPO_DISSESTO_EN": tipo_dissesto["EN"]})
                        row.update({"TIPO_DISSESTO_DBPEDIA": tipo_dissesto["DBPEDIA"]})
                        row.update({"TIPO_DISSESTO_WIKIDATA": tipo_dissesto["WIKIDATA"]})
                    '''
    
                with open(os.path.join(self._data_path, "intervention_contract.csv"), "w+", newline='', encoding="utf8") as newfile:
                    writer = csv.DictWriter(newfile, fieldnames=data[0].keys(), delimiter=";")
                    writer.writeheader()
                    for x in data:
                        writer.writerow(x)
        


def lower_case(row, key) -> str:
    if row[key] and isinstance(row[key], str):
        return row[key].lower().strip()
    else:
        return None
    

def broader_entity(row):
    if row["from_tp_tipo"] and isinstance(row["from_tp_tipo"], str):
        return row["from_tp_tipo"].split(" -")[0]
    else:
        return None

def boolean(val):
    if val and isinstance(val, str):
        if "f" in val.lower():
            return "false"
        else:
            return "true"
    else:
        return "false"


def rendis_cleaning():
    folder_path = "rendis/input/"
    for file in os.listdir(folder_path):
        with open(os.path.join(folder_path, file), "r", encoding="latin-1") as csvfile:
            if "lotto_passi" in file:
                cleaned = csv.reader(csvfile, delimiter=";", quotechar='"', escapechar="\\")
            else:
                cleaned = clevercsv.reader(csvfile, delimiter=";", quotechar='"', escapechar="\\")
            rows = list(cleaned)
            data = []
            for x in rows[1:]:
                rowdict = {}
                for pos,y in enumerate(x):
                    if "\n" in y:
                        y = y.replace("\n", "")
                    if y.lower() == "na" or y.lower() == "none" or y.lower() == "non disponibile":
                        y = ""
                    rowdict[rows[0][pos]] = y
                data.append(rowdict)

        clean_folder_path = "rendis/pre_processed/"
        with open(os.path.join(clean_folder_path, file), "w", newline='', encoding="utf8") as finalfile:
            writer = csv.DictWriter(finalfile, fieldnames=data[0].keys(), delimiter=";")
            writer.writeheader()
            for x in data:
                writer.writerow(x)


def rendis_preprocess():
    with open("rendis/pre_processed/info_lod.csv", "r+", encoding="utf-8") as lodfile:
        reader = csv.DictReader(lodfile, delimiter=";")
        data = [dict(r) for r in reader]
        with open("rendis/pre_processed/tipo_affid.csv", "r+", encoding="utf-8") as affidfile:
            reader = csv.DictReader(affidfile, delimiter=";")
            affid_data = [dict(r) for r in reader]

            for row in data:
                row["_URL_scheda_lotto"] = url_extract(row["_URL_scheda_lotto"])
                row["URL_scheda_lotto_QE"] = url_extract(row["URL_scheda_lotto_QE"])
                row["_URL_scheda_int"] = url_extract(row["_URL_scheda_int"])
                row["ID_URL_scheda_intervento_decreto"] = url_extract(row["ID_URL_scheda_intervento_decreto"]).replace(" ","_")

                if row["_LG_G_pos_json"]:
                    coordinate = row["_LG_G_pos_json"].replace('"', "").replace('{type:MultiPoint,coordinates:', "").replace('}', "")
                    coordinate = coordinate.replace("[", "(").replace("]", ")")
                    coordinate = re.sub("(\d+\.\d+),(\d+\.\d+)", coordinate, "\1 \2")
                    row["POINT"] = "MULTIPOINT"+ coordinate


                for a in affid_data:
                    if a["codice"] == row["L_modAggiudicazione"]:
                        row["L_modAggiudicazione"] = a["descrizione"]

            with open(os.path.join("rendis/pre_processed", "intervention_contract.csv"), "w+", newline='', encoding="utf8") as newfile:
                writer = csv.DictWriter(newfile, fieldnames=data[0].keys(), delimiter=";")
                writer.writeheader()
                for x in data:
                    writer.writerow(x)


def url_extract(val):
    return val.replace('"',"").replace('<a href=', "").replace('> Link </a>',"")



def responsible_agent_role(resp, role):
    resp = resp.strip()
    if role:
        role = role.strip()
        return UtilsFunctions.short_uuid(resp+role)
    else:
        return UtilsFunctions.short_uuid(resp+'responsible')
    
def responsible_role(role):
    if role and role != '':
        return 'https://dati.isprambiente.it/ld/rendis/role/' + UtilsFunctions.digest(role);
    else:
        return 'https://dati.isprambiente.it/ld/rendis/role/responsible';
