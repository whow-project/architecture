import json
import uuid
from slugify import slugify

from pelix.ipopo.decorators import ComponentFactory, Property, Requires, Provides, Instantiate, Validate
from rdflib import Graph, URIRef, Literal, RDF, RDFS, DCAT, DCTERMS
from rdflib.namespace import Namespace

from api.api import DataCollection, DCATCatalog, WebSocketComponent, WHOWFlow


@ComponentFactory("ingester-websocket-factory")
@Property('_path', 'websocketcomponent.path', '/ingestion')
@Requires('_ingester','ingester')
@Provides('websocketcomponent')
@Instantiate("ingester-websocket-inst")
class IngestionWebSocketComponent(WebSocketComponent):

    def __init__(self):
        super().__init__(self._path)
        
    @Validate
    def validate(self, context):
        print('IngestionWebSocketComponent is active!')
        
    '''
    
    message = {
    
        'title': 'Some title for the catalog',
        'description': 'Some description for the catalog',
        'distributions': ['uri'*],
        'store': true|false
    
    }
    
    '''
    def execute(self, message: str, *args, **kwargs) -> str:
            
        whow_data = Namespace("https://w3id.org/whow/data/")
        
        _input = json.loads(message)
        
        title = _input['title']
        description = _input['description']
        distros = _input['distributions']
        store = _input['store']
        
        catalog_id = str(uuid.uuid4())
        catalog_res = URIRef(f'{whow_data}catalog/{catalog_id}')
        
        g = Graph()
        g.add((catalog_res, RDF.type, DCAT.Catalog))
        g.add((catalog_res, DCTERMS.title, Literal(title)))
        g.add((catalog_res, DCTERMS.description, Literal(description)))
        
        counter = 0
        
        uri_refs = []
        
        access_urls = []
        
        print(distros)
        for distro in distros:
            
            distro_id = distro['id']
            mime_type = distro['mimetype']
            
            
            
            mime_type_res = URIRef(WHOWFlow._NS + slugify(mime_type))
            distro_res = URIRef(distro['accessURL'])
            
            dataset_id = str(uuid.uuid4())
            dataset_res = URIRef(f'{whow_data}dataset/{dataset_id}')
            
            g.add((dataset_res, RDF.type, DCAT.Dataset))
            g.add((dataset_res, DCTERMS.title, Literal(f'{dataset_id} - dataset {counter}')))
            g.add((dataset_res, DCTERMS.description, Literal(f'{title} - dataset {counter}')))
            g.add((catalog_res, DCAT.dataset, dataset_res))
            
            distribution_id = str(uuid.uuid4())
            distribution_res = URIRef(f'{whow_data}distribution/{distribution_id}')
            
            uri_refs.append(distribution_res)
            
            g.add((distribution_res, RDF.type, DCAT.Distribution))
            g.add((distribution_res, DCAT.accessURL, distro_res))
            g.add((distribution_res, DCAT.mediaType, mime_type_res))
            g.add((distribution_res, DCTERMS.identifier, Literal(distro_id)))
            g.add((mime_type_res, RDF.type, DCTERMS.MediaType))
            g.add((mime_type_res, RDFS.label, Literal(mime_type)))
            
            g.add((dataset_res, DCAT.distribution, distribution_res))
            
            counter += 1
            
        if len(g)==0:
            
            return '{"status": "error", "content": "No dataset found."}'
        
        else:
            self._ingester.ingest_catalog(DCATCatalog.from_rdf(catalog_res, g), store, True)
            data_collection: DataCollection = self._ingester.create_data_collection(uri_refs)
            
            out_message = {'status': 'success', 'content': json.loads(data_collection.serialize())}
        
            return json.dumps(out_message)