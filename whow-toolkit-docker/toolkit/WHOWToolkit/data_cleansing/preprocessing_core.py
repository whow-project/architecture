from api.api import DataPreprocessor, HTTPResource, DataCollection, WebComponent
import subprocess
from pelix.ipopo.decorators import ComponentFactory, Property, Provides, Instantiate, Validate
import json
from typing import List, Dict
from rdflib.term import URIRef
import urllib.request
import os
from flask import send_file, abort
from flask.views import MethodView
import pathlib
import uuid
from chardet.universaldetector import UniversalDetector
import logging

@ComponentFactory('cleanser-factory')
@Property('_source_folder', 'cleanser.source_folder', '')
@Property('_dest_folder', 'cleanser.dest_folder', '')
@Property('_http_endpoint', 'cleanser.http_endpoint', '')
@Provides('cleanser')
@Instantiate('data-cleansing-impl')
class Cleanser(DataPreprocessor):
    
    @Validate
    def validate(self, context):
        with open('./data_cleansing/conf/props.json') as f:
            js = json.load(f)
            self._source_folder = js['dirty_data']
            self._dest_folder = js['cleaned_data']
            self._http_endpoint = js['http_endpoint']
            print(f'Dirty data folder: {self._source_folder}')
            print(f'Cleaned data folder: {self._dest_folder}')
            
        print(f'The data cleanser {self} has been activated.    ls')
    
    def do_job(self, input: DataCollection, *args, **kwargs):
        
        print(input)
        output = []
        
        #print(js)
        
        if not os.path.exists(self._dest_folder):
            os.makedirs(self._dest_folder)
        
        for source in input.data_sources:
            
            
            file_id= source.identifier
            filename = source.filename
            uri = source.reference.uri
        
            logging.info(f'File: {file_id} from URL {uri}')
            
            file_extension = pathlib.Path(filename).suffix
            
            id = str(uuid.uuid4())
            out_file = os.path.join(self._dest_folder, id + file_extension)
            
            urllib.request.urlretrieve(uri, out_file)
            
            UTF8Converter.convert(out_file, out_file)
            
            out_uri = f'{self._http_endpoint}/preprocessor/{id}{file_extension}'
            
            output.append({"id": file_id, "filename": id + file_extension, "uri": out_uri})
            
        
        return {"data": output}
        

class UTF8Converter():
    
    @classmethod
    def convert(cls, f_in, f_out):
        detector = UniversalDetector()
        
        
        with open(f_in, 'rb') as infile:
            for line in infile:
                detector.feed(line)
                if detector.done: 
                    break
            detector.close()
            #print (detector.result)
            encodingfrom = detector.result['encoding']
            print(encodingfrom)
        
        with open(f_in, mode="r", encoding=encodingfrom) as fr:
            data = fr.read()
            
        with open(f_out, mode="w",encoding='UTF-8') as fw:
            fw.write(data)
