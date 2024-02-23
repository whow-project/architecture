from configparser import ConfigParser, RawConfigParser
import requests
from collections import OrderedDict
import re
from rdflib.namespace import DCTERMS, DCAT, XSD
from rdflib import URIRef, Literal

class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if key in self:
            if isinstance(value, list):
                self[key].extend(value)
                return
            elif isinstance(value,str):
                return # ignore conversion list to string (line 554)
        super(MultiOrderedDict, self).__setitem__(key, value)
            
NAMESPACES = {
        'dct': DCTERMS,
        'dcterms': DCTERMS,
        'terms': DCTERMS,
        'dcat': DCAT,
        'xsd': XSD
    }

class MalformedRDFTerm(Exception):
    
    def __init__(self, key, message="The RDF term {0} is malformed."):
        self.key = key
        self.message = message.format(key)
        super().__init__(self.message)

def get_uri(uri):
    
    if uri[0] == '<' and uri[-1] == '>':
        return URIRef(uri[1:-2])
    elif ':' in uri:
        prefix, id = uri.split(':')
        if prefix in NAMESPACES:
            return NAMESPACES[prefix][id]
    else:
        raise MalformedRDFTerm(uri)
        
def get_literal(literal):
    
    pattern_lexical_value = '(\'|")(.*)(\'|")'
    pattern_language = '@([a-z]{2})$'
    pattern_datatype = '\^\^(.*)$'
    
    #me = re.match(pattern, '\questo è un testo\'@it')
    
    me = re.search(pattern_lexical_value, literal)
    if me:
        lexical_value = me.group(2)
        
        me = re.search(pattern_language, literal)
        if me:
            return Literal(lexical_value, lang=me.group(1))
        else:
            me = re.search(pattern_datatype, literal)
            if me:
                datatype = me.group(1)
                datatype = get_uri(datatype)
                
                return Literal(lexical_value, datatype=datatype)
            else:
                return Literal(lexical_value)
        
    else:
        raise MalformedRDFTerm(literal)
    
    
    
    print(f'Literal {literal}')
    me = re.search(pattern, literal)
    if me:
        print(me.group(1))
    

if __name__ == '__main__':
    
    text = 'dct:titile'
    prefix, id = text.split(':')
    
    print(prefix, id)
    
    config = requests.get('http://localhost/whow/config_test.ini')
    config.encoding = 'utf-8'
    text = config.text
    
    #cp = ConfigParser(dict_type=MultiOrderedDict, strict=False)
    #cp.read_string(text)
    
    cp = RawConfigParser(dict_type=MultiOrderedDict, strict=False, delimiters=('='))
    cp.read_string(text)
    sections = cp.sections()
    dataset_props = cp['dataset']
    
    print(cp.items('dataset'))
    
    for prop in dataset_props:
        
        
        
        print(dataset_props[prop])
        #for value in dataset_props[prop]:
            #print(f'{prop}: {value}')
            
    literal = get_literal('\'questo è un testo\'@it')
    
    print(literal.language)
    
    literal = get_literal('\'questo è un altro testo\'^^xsd:string')
    
    print(literal.datatype)
    
    if 'dataset' in cp:
        print('STOCAZZO')
    
    if '':
        print('STOCAZZONE')
    
    