from pelix.ipopo.decorators import ComponentFactory, Property, Requires, Provides, Instantiate, Validate
from api.api import Validator, ValidatorInput, Configuration
import logging
from pyshacl import validate
from rdflib import Graph
import os
from rdflib.namespace import RDF, Namespace, DCAT, DCTERMS


@ComponentFactory("validator-factory")
@Property('_shacl_file', 'shacl.file', '')
@Property('_http_endpoint', 'http.endpoint', '')
@Provides("validator")
@Instantiate("validator_inst")
class SHACLValidator(Validator):
    
    @Validate
    def validate(self, context):
        
        self.__conf = Configuration('./validator/conf/props.json')
        self._shacl_file = self.__conf.get_property('shacl.file')
        self._http_endpoint = self.__conf.get_property('http.endpoint')
        
    
    def do_job(self, input: ValidatorInput, *args, **kwargs):
        
        confs = input.confs
        index = 0
        conforms = True
        
        report = ''
        
        while index < len(confs) and conforms:
            
            conf = confs[index]
            
            data: Graph = Graph()
            data.parse(conf.graph_uri, format='ttl')
    
            shacl: Graph = Graph()
            shacl.parse(self._shacl_file)
    
            conforms, v_graph, v_text = validate(data, shacl_graph=shacl,
                                         #data_graph_format=data_file_format,
                                         #shacl_graph_format=shapes_file_format,
                                         inference='rdfs',
                                         serialize_report_graph=True)

            if conforms:
                report += f'The metadata for the graph {conf.graph_id} are DCAT-AP compliant.\n'
            else:
                report += f'The metadata for the graph {conf.graph_id} are NOT DCAT-AP compliant.\n'
                
            logging.info(f'Validation report: {report}')
                
            index += 1
            
        findability = self.check_findability(data)
        accessibility = self.check_accessibility(data)
        
        mqa = {'findability': findability,
               'accessibility': accessibility}
            
        return {'conforms': conforms, 'report': report, 'mqa': mqa}
    
    
    def check_findability(self, g: Graph):
        
        DCATAPIT = Namespace('http://www.dati.gov.it/onto/dcatapit#')
        
        score = 0
        datasets = 0
        
        for dataset in g.subjects(RDF.type, DCATAPIT['Dataset']):
            
            
            datasets += 1
            
            score = 0
            
            if (dataset, DCAT.keyword, None) in g:
                keyword_usage = 30
            else:
                keyword_usage = 0
            if (dataset, DCAT.theme, None) in g:
                categories = 30
            else:
                categories = 0
            if (dataset, DCTERMS.spatial, None) in g:
                geo_search = 20
            else:
                geo_search = 0
            if (dataset, DCTERMS.temporal, None) in g:
                time_based_search = 20
            else:
                time_based_search = 0
            
            score = keyword_usage+categories+geo_search+time_based_search
        
        score = score/datasets if score > 0 else 0
        keyword_usage = keyword_usage/datasets if keyword_usage > 0 else 0
        categories = categories/datasets if categories > 0 else 0
        geo_search = geo_search/datasets if geo_search > 0 else 0
        time_based_search = time_based_search/datasets if time_based_search > 0 else 0 
         
        return {'score': score,
                'keyword_usage': keyword_usage,
                'categories': categories,
                'geo_search': geo_search,
                'time_based_search': time_based_search
                } 
        
    def check_accessibility(self, g: Graph):
        
        DCATAPIT = Namespace('http://www.dati.gov.it/onto/dcatapit#')
        
        distributions = 0
        
        for distribution in g.subjects(RDF.type, DCATAPIT['Distribution']):
            
            
            distributions += 1
            
            score = 0
            
            if (distribution, DCAT.accessURL, None) in g:
                access_url = 50
            else:
                access_url = 0
            if (distribution, DCAT.downloadURL, None) in g:
                download_url = 20
            else:
                download_url = 0
            
            
            score = access_url+download_url
        
        score = score/distributions if score > 0 else 0
        access_url = access_url/distributions if access_url > 0 else 0
        download_url = download_url/distributions if download_url > 0 else 0 
         
        return {'score': score,
                'access_url': access_url,
                'download_url': download_url
                } 
        
        