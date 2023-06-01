from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Any, List
import os

from airflow import DAG
from airflow.models.baseoperator import BaseOperator, Context
from airflow.utils.dates import days_ago
from rdflib import Graph, RDF, Namespace
from rdflib.term import URIRef
import urllib.request
import json
import asyncio

import websockets


async def communicate_with(host: str, port: str, path: str, message = ''):
    async with websockets.connect(f"ws://{host}:{port}/{path}") as websocket:
        await websocket.send(message)
        
        print(f'Sent request to {path}.')
        
        print(f'Waiting response from {path}...')
        
        data = await websocket.recv()
        #await data = websocket.recv()
        
        print(f'Received message of {path} completed')
        
    return data

class TriplifyOperator(BaseOperator):
    
    def __init__(self, **kwargs):
        super().__init__(task_id='Triplifier')
        self.__rml_in = rml_in if 'rml' in kwargs else None
        self.task_id = 'Triplification'
    
    
    def execute(self, data, context: Context) -> Any:
        for arg, value in context:
            print(f'{arg}: {value}')
            
        print(f'Mapping {rml_in}')
        
class PreprocessingOperator(BaseOperator):
    
    def __init__(self, **kwargs):
        super().__init__(task_id='Preprocessor')
        config_uri = kwargs['config'] if 'config' in kwargs else None
        print(f'Config uri: {config_uri}')
        
        with urllib.request.urlopen(config_uri) as url:
            self.__config = json.load(url)
        
        self.task_id = 'Preprocessing'
    
    
    def execute(self, context: Context) -> Any:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(communicate_with('localhost', '8765', 'data-cleansing', str(self.__config)))
        
        print(f'Result: {result}')
        

class DAGFactory(object):
    
    
    PROVO = Namespace('http://www.w3.org/ns/prov#')
    TVO = Namespace('https://data.europa.eu/m8g/transform-validate-ontology#')
    WFM = Namespace('https://w3id.org/whow/onto/workflow-mgmt/')
    
    DEFAULT_ARGS = {
        'owner': 'whow',
        'depends_on_past': False,
        'email': ['airflow@example.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 0,
        'retry_delay': timedelta(minutes=5),
    }
    
    
    @classmethod
    def create(cls, graph: Graph) -> DAG:
        
        plans = graph.subjects(RDF.type, cls.PROVO.Plan or cls.TVO.Plan, True)
        
        dags = []
        
        for plan in plans:
            
            
            print(f'Plan {plan}')
            
            dag_id = plan.replace(':', '_').replace('/', '_')
            
            dag : DAG = DAG(
                dag_id=str(dag_id),
                default_args=cls.DEFAULT_ARGS,
                description=f'WHOW workflow {dag_id}',
                schedule_interval=timedelta(days=1),
                start_date=days_ago(1),
                tags=['eProcurement'],
            )
            
            first_task = graph.value(plan, cls.WFM.hasFirstTask)
            
            if first_task:
                operators = cls.__get_tasks(first_task, graph, [])
                
                previous_operator = None
                for operator in operators:
                    dag.add_task(operator)
                    
                    if previous_operator:
                        operator.set_upstream(previous_operator)
                        
                    previous_operator = operator
                    
            
                    
            dags.append(dag)
                
        return dags
                
    @classmethod
    def __get_tasks(cls, task: URIRef, graph: Graph, operators: List[BaseOperator] = None) -> List[BaseOperator]:
    
        if not operators:
            operators = []
                
        ins = graph.objects(task, cls.WFM.hasInput)

        inputs = dict()
        for _in in ins:
            arg = graph.value(_in, cls.WFM.argument)
            value = graph.value(_in, cls.WFM.value)
            inputs[arg.value] = value.value
            
            print(f'ARG {arg}: {value}')
            
        triplification_type = URIRef('https://w3id.org/whow/onto/workflow-mgmt/ActivityType/triplification')
        preprocessing_type = URIRef('https://w3id.org/whow/onto/workflow-mgmt/ActivityType/preprocessing')
        
        t_type = graph.value(task, cls.WFM.hasActivityType)
        
        print(f'T_type {t_type} {task}')
        
        if t_type == triplification_type:
            operators.append(TriplifyOperator(**inputs))
        elif t_type == preprocessing_type:
            operators.append(PreprocessingOperator(**inputs))
            
        next_task = graph.value(task, cls.WFM.hasNextTask)
        
        if next_task:
            return cls.__get_tasks(next_task, graph, operators)
        else:
            return operators
             
g = Graph()
g.parse('http://semantics.istc.cnr.it/whow/transformationPlan_v2.ttl', format='ttl')
    
dags = DAGFactory.create(g)

print(dags)

for dag in dags:
    dag : DAG = dag
    
    for task in dag.tasks:
        #print(f'Task: {task.downstream_task_ids}')
        print(f'Task: {task}')
            
        
