from abc import ABC
from api.api import Configuration, Reference, DataSource, DataCollection, DCATCatalog, DCATDataset, DCATDistribution, HTTPResource, WebComponent, DCATObject, WebSocketComponent, WHOWFlow, MediaTypeRegistry
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import DCAT, DC, RDF, RDFS
import requests
import uuid
from pelix.ipopo.decorators import ComponentFactory, Instantiate, Validate, Provides, Property, Requires
from pelix.framework import FrameworkFactory, Bundle
from pelix.utilities import use_service
from typing import List, Dict
from rdflib.namespace._RDF import RDF
from babel.messages import catalog
from flask import request
from flask.views import MethodView
import os
from docutils.nodes import title
import json
from rdflib.namespace._DCTERMS import DCTERMS
from rdflib.term import URIRef
from flask.helpers import send_file
from slugify.slugify import slugify

class Ingester(ABC):
    
    def ingest(self, metadata: Graph, store=True):
        pass
        

@ComponentFactory("ingestion-factory")
@Property('_data_folder', 'data.folder', '')
@Property('_meta_folder', 'meta.folder', '')
@Property('_http_endpoint', 'http.endpoint', '')
@Property('_data_catalogue_graph_path', 'data.catalogue.graph_path', '')
@Provides("ingester")
@Instantiate("ingester-inst")
class SimpleIngester(Ingester):
    
    @Validate
    def validate(self, context):
        print('SimpleIngester is active!')
        self.__conf = Configuration('./ingestion/conf/props.json')
        self._data_folder = self.__conf.get_property('data.folder')
        self._meta_folder = self.__conf.get_property('meta.folder')
        self._http_endpoint = self.__conf.get_property('http.endpoint')
        
        self._data_catalogue_graph = Graph()
        self._data_catalogue_graph.parse(self.__conf.get_property('data.catalogue.graph_path'))
        
    
    def ingest_catalog(self, catalog: DCATCatalog, store=True, produce_dcat=True):
        
        if store:
            for dataset in catalog.datasets:
                self.ingest_dataset(dataset, store, False)
                
        if produce_dcat:
            self._data_catalogue_graph += catalog.to_rdf()
            self._data_catalogue_graph.serialize(destination=self.__conf.get_property('data.catalogue.graph_path'), format='ttl')
            
                    
    def ingest_dataset(self, dataset: DCATDataset, store=True, produce_dcat=True, save_dcat=True):
        
        
        if store:
            for distribution in dataset.distributions:
                self.ingest_distribution(distribution, store)
                
        if produce_dcat:
            self._data_catalogue_graph += dataset.to_rdf()
            self._data_catalogue_graph.serialize(destination=self.__conf.get_property('data.catalogue.graph_path'), format='ttl')
                
        
                
    def ingest_distribution(self, distribution: DCATDistribution, store=True, produce_dcat=True):
        
        
        if store:
                
            if not os.path.exists(self._data_folder):
                os.makedirs(self._data_folder)
            
            access_url = distribution.access_urls[0]
            
            mediatypes = distribution.values(DCAT.mediaType)
            if mediatypes:
                mediatype = mediatypes[0]
            else:
                mediatype = None
            
            response = requests.get(access_url)
            
            _id = str(uuid.uuid4())
            file_extension = MediaTypeRegistry.extension(mediatype) if mediatype else None
            file_id = _id + file_extension if file_extension else _id
            
            file_path = os.path.join(self._data_folder, file_id)
            open(file_path, "wb").write(response.content)
            
            distribution.access_urls = [URIRef(f'{self._http_endpoint}{file_id}')]
            
        if produce_dcat:
            self._data_catalogue_graph += distribution.to_rdf()
            self._data_catalogue_graph.serialize(destination=self.__conf.get_property('data.catalogue.graph_path'), format='ttl')
    
    
    def ingest(self, metadata: Graph, store=True):
        if store:
            tuples = metadata.subject_objects(DCAT.accessURL, True)
            downloaded = False
            
            removal_list = []
            
            new_triple = None

            for tuple in tuples:
                if not downloaded:
                    url = subject_object[1]
                    
                    response = requests.get(url)
                    file_id = uuid.uuid4()
                    
                    file_path = os.path.join(self._data_folder, file_id)
                    
                    open(file_path, "wb").write(response.content)
                    
                    downloaded = True
                    
                    metadata.add((tuple[0], DCAT.accessURL, URIRef(f'{self._http_endpoint}/{file_id}')))
                
                removal_list.append((tuple[0], DCAT.accessURL, tuple[1]))
                
            for triple in removal_list:
                metadata.remove(triple) 
                
        
        for triple in metadata:
            self._data_catalogue_graph.add(triple)
                
                
    def create_data_collection(self, distributions: List[URIRef]) -> DataCollection:
        
        #whow_dc = Namespace("https://w3id.org/whow/onto/dc/")
        #whow_data = Namespace("https://w3id.org/whow/data/")
        
        #catalogue_id = str(uuid.uuid4())
        #self._data_catalogue_graph.add((URIRef(whow_data + catalogue_id), RDF.type, whow_dc.DataCollection))
        
        data_sources = []
        for distribution in distributions:
            
            print(f'Looking for distribution {distribution}')
            url = self._data_catalogue_graph.value(distribution, DCAT.accessURL, None)
            
            if url:
                dcterms_identifier = self._data_catalogue_graph.value(distribution, DCTERMS.identifier, None)
                _id = dcterms_identifier if dcterms_identifier else str(uuid.uuid4())
                file_name = str(uuid.uuid4())
                ds = DataSource(_id, file_name, Reference(str(url)))
                data_sources.append(ds)
            
        print(f'DataSources {data_sources}')
        dcid = str(uuid.uuid4())
        data_collection: DataCollection = DataCollection(dcid, data_sources)
        data_collection.serialize(os.path.join(self._meta_folder, dcid))
        
        return data_collection 
        
    def get_data_collection(self, dcid: str) -> DataCollection:
        with open(os.path.join(self._meta_folder, dcid)) as json_file:
            data = json.load(json_file)
            
            return DataCollection.from_dict(data)
        
    def delete_data_collection(self, dcid: str) -> None:
        os.remove(os.path.join(self._meta_folder, dcid))
        
    @property
    def data_catalogue_graph(self):
        return self._data_catalogue_graph

            
