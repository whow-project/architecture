from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Any, List
import os

from airflow import DAG
from airflow.models.baseoperator import BaseOperator, Context
from airflow.utils.dates import days_ago
from rdflib import Graph, RDF, Namespace
from rdflib.namespace import DefinedNamespace
from rdflib.term import URIRef
import urllib.request
import json
import asyncio

import websockets



class WHOWFlow(DefinedNamespace):
    
    hasFirstActivity: URIRef
    hasLastActivity: URIRef
    hasActivity: URIRef
    hasBoundService: URIRef
    isBoundServiceOf: URIRef
    
    hasNextActivity: URIRef
    hasPreviousActivity: URIRef
    
    Plan: URIRef
    Activity: URIRef
    Service: URIRef
    
    ingestion: URIRef
    preprocessing: URIRef
    triplification: URIRef
    linking: URIRef
    reasoning: URIRef
    storage: URIRef
    
    text_csv: URIRef
    text_tsv: URIRef
    application_vnd_ms_excel: URIRef
    application_json: URIRef
    application_xml: URIRef
    
    _NS = Namespace("https://w3id.org/whow/onto/flow/")

async def communicate_with(service_uri: str, message = ''):
    
    print(f'Communicating with {service_uri}')
    
    async with websockets.connect(service_uri) as websocket:
        await websocket.send(message)
        
        print(f'Sent request to {service_uri}.')
        
        print(f'Waiting response from {service_uri}...')
        
        data = await websocket.recv()
        #await data = websocket.recv()
        
        print(f'Received message of {service_uri} completed')
        
    return data


class WHOWOperator(BaseOperator):
    
    def __init__(self, _id: str, service: URIRef, root:bool=False, **kwargs):
        
        _id = _id.replace(':', '_').replace('/', '_')
        super().__init__(task_id=_id)
        self.task_id: str = _id
        self.__service: URIRef = service
        self.__root: bool = root
        
    @property
    def is_root(self) -> bool :
        return self.__root
    
    @property
    def bound_service(self) -> URIRef:
        return self.__service
    
    def execute(self, context: Context) -> Any:
        
        print(context)
        
        in_data = BaseOperator.xcom_pull(context) 
        
        bound_services = context['dag_run'].conf['bound_services']
        
        print(f'Bound services: {bound_services}')
        
        print(f'IN DATA: {in_data}')
        
        bound_service = str(self.bound_service)
        
        if bound_service in bound_services:
            service = bound_services[bound_service]
            service_uri = service['endpoint']
            conf_data = service['data']
            
            if not (conf_data or in_data): 
                print(f'No data provided, hence no communication with {service_uri} will be established.')
                return None
            elif in_data and conf_data:
                data = {**conf_data, **in_data}
            elif not in_data and conf_data:
                data = conf_data
            else:
                data = in_data
                
            out = asyncio.run(communicate_with(service_uri, json.dumps(data)))
            out = json.loads(out)
            
            status = out['status']
            
            if status == 'success':
                print(f'Content of ws communication: {out["content"]}')
                return out['content']
            else:
                print(f'An error was returned via ws.')
                return None
            
            
        else:
            print(f'No service bound as {self.bound_service}')
            return None
        

class DAGFactory(object):
    
    
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
        
        plans = graph.subjects(RDF.type, WHOWFlow.Plan, True)
        
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
                tags=['WHOWProcessing'],
            )
            
            first_task = graph.value(plan, WHOWFlow.hasFirstActivity)
            
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
            
        t_type = graph.value(task, )
        
        is_root = True if len(operators)==0 else False 
        
        #service = graph.value(task, WHOWFlow.hasNextAction)
        service = graph.value(task, WHOWFlow.hasBoundService)
        
        if service:
        
            operators.append(WHOWOperator(_id=task, service=service, root=is_root))
            
        next_task = graph.value(task, WHOWFlow.hasNextActivity)
        
        print(f'Next task {next_task}')
            
        if next_task:
            return cls.__get_tasks(next_task, graph, operators)
        else:
            return operators
             
g = Graph()
g.parse('http://semantics.istc.cnr.it/whow/transformationPlan_v3.ttl', format='ttl')
    
dags = DAGFactory.create(g)

print(dags)

for dag in dags:
    dag : DAG = dag
    
    for task in dag.tasks:
        #print(f'Task: {task.downstream_task_ids}')
        print(f'Task: {task}')
            
        
