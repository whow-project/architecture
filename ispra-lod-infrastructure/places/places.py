from jinja2 import Environment, FileSystemLoader, Template
from rdflib.parser import StringInputSource
#from load_delete import toLoad_toDelete
from kg_loader import KnowledgeGraphLoader
from pyrml import TermUtils, RMLConverter


def metropolitan_city(istat):
    metropolitan_cities = ["001", "010", "015", "027", "037", "048", "058", "063", "072", "080", "082", "083", "087", "092"]
    
    out = None
    if istat in metropolitan_cities:
        out = "metropolitancity/" + str(2) + istat[1:]
    else:
        out = "province/" + istat
        
    return out
        
def metropolitan_city_type(istat):
    metropolitan_cities = ["001", "010", "015", "027", "037", "048", "058", "063", "072", "080", "082", "083", "087", "092"]
        
    out = None
    if istat in metropolitan_cities:
        out = "MetropolitanCity"
    else:
        out = "Province"
    return out


def placesRDF():
    file_loader = FileSystemLoader('.')
    env = Environment(loader=file_loader)

    loader = KnowledgeGraphLoader()
    
    #regions
    template = env.get_template('places/regions_map.ttl')
    rml_mapping = template.render()
    
    rml_converter = RMLConverter()
    g = rml_converter.convert(StringInputSource(rml_mapping.encode('utf-8')))

    #toLoad_toDelete (g, "regions", "places")
    loader.toLoad_toDelete(g, "regions", "places")
    

    #provinces
    template = env.get_template('places/provinces_map.ttl')
    rml_mapping = template.render()

    rml_converter = RMLConverter()
    rml_converter.register_function("metropolitan_city", metropolitan_city)
    rml_converter.register_function("metropolitan_city_type", metropolitan_city_type)
    g = rml_converter.convert(StringInputSource(rml_mapping.encode('utf-8')))

    #toLoad_toDelete(g, "provinces", "places")
    loader.toLoad_toDelete(g, "provinces", "places")

    #municipalities
    template = env.get_template('places/municipalities_map.ttl')
    rml_mapping = template.render()

    rml_converter = RMLConverter()
    rml_converter.register_function("metropolitan_city", metropolitan_city)
    g = rml_converter.convert(StringInputSource(rml_mapping.encode('utf-8')))
    
    #toLoad_toDelete(g, "municipalities", "places")
    loader.toLoad_toDelete(g, "municipalities", "places")
