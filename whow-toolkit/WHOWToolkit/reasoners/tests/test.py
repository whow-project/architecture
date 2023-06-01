from owlready2 import Ontology, get_ontology, sync_reasoner_pellet, onto_path, AllDisjoint, OwlReadyInconsistentOntologyError, World
from owlready2.namespace import owl


my_world = World()

ontology_iris = [
    'https://raw.githubusercontent.com/whow-project/semantic-assets/main/ispra-ontology-network/top/latest/top.rdf',
    'http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl'
    ]


for ontology_iri in ontology_iris:
    ontology: Ontology = my_world.get_ontology(ontology_iri).load()
    #ontology.load()
    #ontos.append(ontology)
    

onto_path.append('.')



    
try:
    sync_reasoner_pellet(my_world)
    my_world.save(file='out2.owl')
except OwlReadyInconsistentOntologyError as e:
    raise e


    #parents = ontology.get_parents_of(test_pizza)
    #print(parents)

    #ontology.save(file='reasoned.owl', format='rdfxml')
    