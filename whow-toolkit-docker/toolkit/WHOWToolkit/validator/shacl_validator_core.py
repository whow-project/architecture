from pelix.ipopo.decorators import ComponentFactory, Property, Requires, Provides, Instantiate, Validate
from api.api import Validator, ValidatorInput, Configuration
import logging
from pyshacl import validate
from rdflib import Graph
import os
from rdflib.namespace import RDF, Namespace, DCAT, DCTERMS
import requests
import pandas as pd

@ComponentFactory("validator-factory")
@Property('_shacl_file', 'shacl.file', '')
@Property('_vocabularies_folder', 'vocabularies.folder', '')
@Property('_http_endpoint', 'http.endpoint', '')
@Provides("validator")
@Instantiate("validator_inst")
class SHACLValidator(Validator):
    
    @Validate
    def validate(self, context):
        
        self.__conf = Configuration('./validator/conf/props.json')
        self._shacl_file = self.__conf.get_property('shacl.file')
        self._vocabularies_folder = self.__conf.get_property('vocabularies.folder')
        self._http_endpoint = self.__conf.get_property('http.endpoint')
        
    
    def do_job(self, input: ValidatorInput, *args, **kwargs):
        
        confs = input.confs
        index = 0
        conforms = True
        
        report = ''
        
        results = []
        
        while index < len(confs):
            
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
            interoperability = self.check_interoperability(data)
            reusability = self.check_reusability(data)
            contextuality = self.check_contextuality(data)
            
            mqa = {'findability': findability,
                   'accessibility': accessibility,
                   'interoperability': interoperability,
                   'reusability': reusability,
                   'contextuality': contextuality}
            
            results.append({'id': conf.graph_id, 'conforms': conforms, 'report': report, 'mqa': mqa})
            
        return results
    
    
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
                
                url = g.value(distribution, DCAT.downloadURL, None)
                response = requests.get(url)
                code = response.status_code
                logging.info(f'X status CODE download URL {code} ({type(code)})')
                
                if code >= 200 and code <400:
                    download_url_accessibility = 30
                else:
                    download_url_accessibility = 0
            else:
                download_url = 0
                download_url_accessibility = 0
            
            
            
            score = access_url+download_url+download_url_accessibility
        
        score = score/distributions if score > 0 else 0
        access_url = access_url/distributions if access_url > 0 else 0
        download_url = download_url/distributions if download_url > 0 else 0 
        download_url_accessibility = download_url_accessibility/distributions if download_url_accessibility > 0 else 0 
        return {'score': score,
                'access_url': access_url,
                'download_url': download_url,
                'download_url_accessibility': download_url_accessibility
                } 
        
        
    def check_interoperability(self, g: Graph):
        
        DCATAPIT = Namespace('http://www.dati.gov.it/onto/dcatapit#')
        
        distributions = 0
        
        for distribution in g.subjects(RDF.type, DCATAPIT['Distribution']):
            
            
            distributions += 1
            
            score = 0
            
            format = 20 if (distribution, DCTERMS.format, None) in g else 0
            media_type = 10 if (distribution, DCAT.mediaType, None) in g else 0
            
            mr_formats = Graph()
            mr_formats.parse(os.path.join(self._vocabularies_folder, 'edp-machine-readable-format.rdf'), format='xml')
            
            np_formats = Graph()
            np_formats.parse(os.path.join(self._vocabularies_folder, 'edp-non-proprietary-format.rdf'), format='xml')
            
            iana = pd.read_csv(os.path.join(self._vocabularies_folder, 'iana.csv'))
            formats_a = g.objects(distribution, DCTERMS.format, True)
            formats_b = g.objects(distribution, DCTERMS.format, True)
            mediatypes = g.objects(distribution, DCAT.mediaType, True)
            
            a = any((format, None, None) in mr_formats for format in formats_a)
            b = any((format, None, None) in np_formats for format in formats_b)
            c = any((iana['Template'].eq(str(mediatype))).any() for mediatype in mediatypes)
            
            standard_format_mediatype = 10 if any((a,b,c)) else 0
            
            non_proprietary_format = 20 if b else 0
            machine_readable_format = 20 if a else 0
            
            dcat_ap_compliance = 30
            
            score = format+media_type+standard_format_mediatype+non_proprietary_format+machine_readable_format+dcat_ap_compliance
        
        score = score/distributions if score > 0 else 0
        format = format/distributions if format > 0 else 0
        media_type = media_type/distributions if media_type > 0 else 0 
        standard_format_mediatype = standard_format_mediatype/distributions if standard_format_mediatype > 0 else 0
        non_proprietary_format = non_proprietary_format/distributions if non_proprietary_format > 0 else 0 
        machine_readable_format = machine_readable_format/distributions if machine_readable_format > 0 else 0
        dcat_ap_compliance = dcat_ap_compliance/distributions if dcat_ap_compliance > 0 else 0
        
        return {'score': score,
                'format': format,
                'media_type': media_type,
                'standard_format_mediatype': standard_format_mediatype,
                'non_proprietary_format': non_proprietary_format,
                'machine_readable_format': machine_readable_format,
                'dcat_ap_compliance': dcat_ap_compliance
                } 
        
    def check_reusability(self, g: Graph):
        
        DCATAPIT = Namespace('http://www.dati.gov.it/onto/dcatapit#')
        
        distributions = 0
        datasets = 0
        
        dist_score = 0
        dataset_score = 0
        licence_information = 0
        licence_vocabulary = 0
        
        for distribution in g.subjects(RDF.type, DCATAPIT.Distribution):
            
            
            distributions += 1
            
            licence_information = 20 if (distribution, DCTERMS.license, None) in g else 0
            
            licence_graph = Graph()
            licence_graph.parse(os.path.join(self._vocabularies_folder, 'edp-licences-skos.rdf'), format='xml')
            licence_graph += Graph().parse(os.path.join(self._vocabularies_folder, 'ontopia-licences.rdf'), format='xml')
            
            licences = g.objects(distribution, DCTERMS.license, True)
            a = any((licence, None, None) in licence_graph for licence in licences)
            licence_vocabulary = 10 if a else 0
            
            
            dist_score = licence_information+licence_vocabulary
        
        dist_score = dist_score/distributions if dist_score > 0 else 0
        licence_information = licence_information/distributions if licence_information > 0 else 0
        licence_vocabulary = licence_vocabulary/distributions if licence_vocabulary > 0 else 0
        
        
        for distribution in g.subjects(RDF.type, DCATAPIT.Dataset):
            
            datasets += 1
            
            access_restriction = 10 if (distribution, DCTERMS.accessRights, None) in g else 0
            
            access_restriction_graph = Graph()
            access_restriction_graph.parse(os.path.join(self._vocabularies_folder, 'access-right-skos.rdf'), format='xml')
            
            access_rights = g.objects(distribution, DCTERMS.accessRights, True)
            a = any((access_right, None, None) in access_restriction_graph for access_right in access_rights)
            access_restriction_vocabulary = 5 if a else 0
            
            contact_point = 20 if (distribution, DCAT.contactPoint, None) in g else 0
            publisher = 10 if (distribution, DCTERMS.publisher, None) in g else 0
            
            dataset_score = access_restriction+access_restriction_vocabulary+contact_point+publisher
        
        dataset_score = dataset_score/datasets if dataset_score > 0 else 0
        access_restriction = access_restriction/datasets if access_restriction > 0 else 0
        access_restriction_vocabulary = access_restriction_vocabulary/datasets if access_restriction_vocabulary > 0 else 0
        contact_point = contact_point/datasets if contact_point > 0 else 0
        publisher = publisher/datasets if publisher > 0 else 0 
        
        score = dist_score+dataset_score
        
        return {'score': score,
                'licence_information': licence_information,
                'licence_vocabulary': licence_vocabulary,
                'access_restriction': access_restriction,
                'access_restriction_vocabulary': access_restriction_vocabulary,
                'contact_point': contact_point,
                'publisher': publisher
                } 
        
    def check_contextuality(self, g: Graph):
        
        DCATAPIT = Namespace('http://www.dati.gov.it/onto/dcatapit#')
        
        score = 0
        
        rights = 0
        file_size = 0
        date_of_issue = 0
        modification_date = 0
        
        distributions = 0
        
        for distribution in g.subjects(RDF.type, DCATAPIT.Distribution):
            
            
            distributions += 1
            
            rights = 5 if (distribution, DCTERMS.rights, None) in g else 0
            file_size = 5 if (distribution, DCAT.byteSize, None) in g else 0
            date_of_issue = 5 if (distribution, DCTERMS.issued, None) in g else 0
            modification_date = 5 if (distribution, DCTERMS.modified, None) in g else 0
            
            score = rights+file_size+date_of_issue+modification_date
        
        score = score/distributions if score > 0 else 0
        rights = rights/distributions if rights > 0 else 0
        file_size = file_size/distributions if file_size > 0 else 0
        date_of_issue = date_of_issue/distributions if date_of_issue > 0 else 0
        modification_date = modification_date/distributions if modification_date > 0 else 0
        
        return {'score': score,
                'rights': rights,
                'file_size': file_size,
                'date_of_issue': date_of_issue,
                'modification_date': modification_date
                } 
        
        