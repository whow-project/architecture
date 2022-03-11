#usage: python3 delete_location.py <SAMPLE>
#<SAMPLE> = municipalities, provinces, regions

import sys
import gzip
import rdflib
from rdflib import Graph

def print_delete(str_graph, graph_toDel, graph_update, cat):

    delG = Graph()

    print ('Parsing toDel graph ...')
    for s, p, o in graph_toDel:
        if (s, None, None) in graph_update:
            delG.add((s, p, o))

    sql_file = 'del_list_' + cat + '.sql'        

    with open(sql_file, 'w') as sql_del:
        print("DELETE FROM LOAD_LIST;", file=sql_del)
        for dd in (delG.serialize(format='nt11').splitlines()):
            if dd: print ('SPARQL DELETE DATA { GRAPH <' + str_graph + '> { ' + dd + '} } ;', file=sql_del)
        print("RDF_LOADER_RUN();", file=sql_del)
        print("CHECKPOINT;", file=sql_del)
        print("COMMIT WORK;", file=sql_del)
        print("CHECKPOINT;", file=sql_del)
        

if __name__ == '__main__':

    print ('Category:', str(sys.argv[1]))

    str_ispra_graph = 'https://dati.isprambiente.it/ld/location/'

    file_triples_todel = 'rdf/location/kg/' + sys.argv[1] + '/delete.nt.gz'
    file_triples_update = 'rdf/location/kg/' + sys.argv[1] + '.nt.gz'

    triple_todel = Graph()
    triple_update = Graph()

    print ('Reading toDel triples ...')
    with gzip.open(file_triples_todel, 'rb') as f:
        str_triple_todel = f.read()
    triple_todel.parse(data=str_triple_todel, format='nt11')

    if not len(triple_todel):
        print ('No triples to delete!')
        exit()
        
    print ('Reading updated triples ...')
    with gzip.open(file_triples_update, 'rb') as f:
        str_triple_update = f.read()
    triple_update.parse(data=str_triple_update, format='nt11')

    print_delete(str_ispra_graph, triple_todel, triple_update, str(sys.argv[1]))
    

        

