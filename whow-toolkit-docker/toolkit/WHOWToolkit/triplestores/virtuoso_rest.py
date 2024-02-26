import os

from api.api import WebView, Configuration
from flask.views import MethodView
from pelix.ipopo.decorators import ComponentFactory, Property, Provides, Instantiate, Validate, Requires
from flask import request, abort, render_template, jsonify

from rdflib import Graph, RDF, RDFS, Namespace
from flask.wrappers import Response

import glob

import shortuuid
import json

import logging

@ComponentFactory("sparql-webview-factory")
@Property('_name', 'webcomponent.name', 'sparql')
@Property('_path', 'webcomponent.path', '/')
@Property('_context', 'webcomponent.context', __name__)
@Requires('_triplestore_manager','triplestore-manager')
@Provides('webviewcomponent')
@Instantiate("sparqlfactory-homepage")
class SPARQLWeb(WebView):
    
    def __init__(self):
        super().__init__()
        self._triplestore_manager = None
        
    def get(self):
        logging.info("SPARQL home page.")
        if not self._triplestore_manager:
            self._triplestore_manager = self._get_reference('triplestore-manager')
        return render_template('sparql.html', services=self.webservices, virtuoso_sparql=self._triplestore_manager.virtuoso_sparql)
    
    
    def set_web_services(self, services):
        self.__services = services

        