from api.api import Reasoner, HTTPResource, RESTApp
from pelix.ipopo.decorators import ComponentFactory, Instantiate, Validate, Provides, Requires, Property
from owlready2 import Ontology, get_ontology, sync_reasoner_pellet
from typing import List
from rdflib.term import URIRef
import uuid
import os

@ComponentFactory("reasoning-factory")
@Property('_inferences_folder', 'inferences.folder', './inferences')
@Provides("reasoner")
@Instantiate("pellet-reasoner")
class PelletReasoner(Reasoner):
    
    @Validate
    def validate(self, context):
        print('Activated Pellet reasoner with reasoning folder set to {self._inferences_folders}')
        
    def do_reasoning(self, ontolgy_network: List[URIRef], data: List[URIRef]):
        
        if not os.path.exists(self._inferences_folders):
            os.makedirs(self._inferences_folder)
        
        my_world = World()
        
        for ontology_iri in ontology_network:
            try:
                ontology: Ontology = my_world.get_ontology(ontology_iri).load()
            except Exception as e:
                print(f'[WARN] The ontology {ontology_iri} cannot be loaded.')
                pass
            
        for data_iri in data:
            try:
                ontology: Ontology = my_world.get_ontology(data_iri).load()
            except Exception as e:
                print(f'[WARN] The data in {data_iri} cannot be loaded.')
                pass
            
            
        onto_path.append('.')
        sync_reasoner_pellet(my_world)
        
        try:
            sync_reasoner_pellet(my_world)
            
            graph_file = os.path.join(self._inferences_folders, str(uuid.uuid4()))
            my_world.save(file=graph_file)
        except OwlReadyInconsistentOntologyError as e:
            raise e
    