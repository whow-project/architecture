import json
import os

from flask.helpers import send_file, abort
from flask.views import MethodView
from pelix.framework import FrameworkFactory
from pelix.utilities import use_service
from pelix.ipopo.decorators import ComponentFactory, Instantiate, Validate, Provides, Property, Requires
from rdflib import Graph, URIRef, RDF, RDFS, DCAT, DCTERMS

from api.api import WebView, Configuration, Reference, DataSource, DataCollection, DCATCatalog, DCATDataset, DCATDistribution, HTTPResource, WebComponent, DCATObject, WebSocketComponent, WHOWFlow, MediaTypeRegistry


@ComponentFactory("data-collection-create-web-factory")
@Property('_path', 'webcomponent.path', '/ingestion/datacollection')
@Requires('_ingester','ingester')
@Provides('webcomponent')
@Instantiate("ingester-datacollection-create-web-inst")
class IngestionDataCollectionsWeb(MethodView, WebComponent):
    
    def __init__(self):
        super().__init__(self._path) 
    
    @Validate
    def validate(self, context):
        print('IngestionDataCollectionWeb is active!')
        
            
    def post(self):
        urls = [URIRef(url) for url in request.form.getlist('url')]
        
        print(f'URLS ! {urls}')
        
        ctx = FrameworkFactory.get_framework().get_bundle_context()
        reference = ctx.get_service_reference('ingester')
        
        with use_service(ctx, reference) as ingester:
            ingester.create_data_collection(urls)
            
            return 'Success', 200
    

@ComponentFactory("data-collection-web-factory")
@Property('_path', 'webcomponent.path', '/ingestion/datacollection/<file>')
@Requires('_ingester','ingester')
@Provides('webcomponent')
@Instantiate("ingester-datacollection-web-inst")
class IngestionDataCollectionWeb(MethodView, WebComponent):
    
    def __init__(self):
        super().__init__(self._path) 
    
    @Validate
    def validate(self, context):
        print('IngestionDataCollectionWeb is active!')
        
            
    def get(self, data_collection_id):
        
        print(f'Dest folder {self._dest_folder}.')
        f = os.path.join(self._dest_folder, file)
        
        if os.path.exists(f):
            return send_file(f)
        else:
            abort(404)
            
    def post(self, data_collection_id):
        pass
        
    def delete(self, data_collection_id):
        f = os.path.join(self._dest_folder, file)
        
        if os.path.exists(f):
            os.remove(f)
            return "Success", 200
        else:
            abort(404)
            
            
@ComponentFactory("ingester-web-factory")
@Property('_path', 'webcomponent.path', '/ingestion')
@Requires('_ingester','ingester')
@Provides('webcomponent')
@Instantiate("ingester-web-inst")
class IngestionWeb(MethodView, WebComponent):
    
    def __init__(self):
        super().__init__(self._path)
        
        
        
    @Validate
    def validate(self, context):
        print(f'Ingestion is active with dependency to {self._ingester}!')
        
            
    def get(self):
        
        supported_mime_types = ('application/rdf+xml', 'text/turtle', 'application/json-ld', 'application/json', 'application/n-triples')
        
        ctx = FrameworkFactory.get_framework().get_bundle_context()
        reference = ctx.get_service_reference('ingester')
        with use_service(ctx, reference) as ingester:
            
            content_types = [ctype for ctype in request.accept_mimetypes.values()]
            
            if any(item in supported_mime_types for item in content_types):
                
                g: Graph = ingester.data_catalogue_graph
                
                if 'application/json' in content_types:
                    
                    
                    catalogs = []
                    for catalog in g.subjects(RDF.type, DCAT.Catalog, True):
                        
                        title = g.value(catalog, DCTERMS.title, None)
                        description = g.value(catalog, DCTERMS.description, None)
                        
                        cat = {'id': str(catalog),
                               'title': title,
                               'description': description}
                        
                        
                        datasets = []
                        for dataset in g.objects(catalog, DCAT.dataset, True):
                            
                            title = g.value(dataset, DCTERMS.title, None)
                            description = g.value(dataset, DCTERMS.description, None)
                            dat = {'id': str(dataset),
                                   'title': title,
                                   'description': description}
                            
                            datasets.append(dat)
                            
                            distros = []
                            
                            for distribution in g.objects(dataset, DCAT.distribution, True):
                                url = g.value(distribution, DCAT.accessURL, None)
                                
                                distro = {'id': str(distribution),
                                           'access_url': str(url)}
                            
                                distros.append(distro)
                            
                            dat['distributions'] = distros
                            
                        cat['datasets'] = datasets
                        
                        catalogs.append(cat)
                        
                    return json.dumps({'catalogs': catalogs}), 200
                else:
                    return g.serialize(format=content_types[0]), 200
            else:
                return "Mime type not acceptable", 406
            
    def post(self):
        
        ctx = FrameworkFactory.get_framework().get_bundle_context()
        reference = ctx.get_service_reference('ingester')
        
        with use_service(ctx, reference) as ingester:
        
            print(f'Received request {ingester}')
            supported_mime_types = ('application/rdf+rml', 'text/turtle', 'application/json-ld', 'text', 'application/n-triples')
            
            content_type = request.content_type
            print(f'Content type: {content_type}')
            if content_type in supported_mime_types:
                data = request.data.decode('utf-8')
                
                g = Graph()
                g.parse(format=content_type, data=data)
                
                catalog = g.value(None, RDF.type, DCAT.Catalog)
                if catalog:
                    dcat_catalog: DCATCatalog = DCATCatalog.from_rdf(catalog, g)
                    ingester.ingest_catalog(dcat_catalog)
                    
                    return "Success", 200
                
                else:
                    return "Catalog Not Found", 404
            else:
                return "Mime type not acceptable", 406
        
        
    def delete(self, data_collection_id):
        f = os.path.join(self._dest_folder, file)
        
        if os.path.exists(f):
            os.remove(f)
            return "Success", 200
        else:
            abort(404)
        
@ComponentFactory("data-web-factory")
@Property('_name', 'webcomponent.name', 'data')
@Property('_path', 'webcomponent.path', '<dataset_id>')
@Property('_context', 'webcomponent.context', __name__)
@Requires('_ingester', 'ingester')
@Provides('webcomponent')
@Instantiate("data-web-inst")
class DataWeb(WebView):
    
    def __init__(self):
        super().__init__()
        self._ingester = None
        
        
        
    @Validate
    def validate(self, context):
        print(f'Ingestion Catalog is active!')
        
        
    def get(self, dataset_id: str):
        
        if not self._ingester:
            self._ingester = self._get_reference('ingester')
        
        path = os.path.join(self._ingester._data_folder, dataset_id)
        
        if os.path.exists(path):
            return send_file(path), 200
        else:
            abort(404)
        
    def set_web_services(self, services):
        self.__services = services