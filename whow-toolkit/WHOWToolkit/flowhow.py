import pendulum

from airflow.decorators import dag, task
from pyrml import RMLConverter

import os, glob, uuid

from rdflib import Graph
from typing import List
import asyncio
import websockets

os.environ["no_proxy"]="*"

async def communicate_with(path: str):
    async with websockets.connect(f"ws://localhost:8765/{path}") as websocket:
        await websocket.send('data')
        
        print(f'Sent request to {path}')
        
        await websocket.recv()
        
        print(f'Received message of {path} completed')
        
    return 'Done'


@dag(
    schedule=None,
    start_date=pendulum.datetime(2022, 11, 8, tz="UTC"),
    catchup=False,
    tags=['whow-flow'],
)
def whow_flow():
    
    @task()
    def rdf_map():
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(communicate_with('rml_mapper'))
        
        return result 
        

    @task()
    def load(input: str):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(communicate_with('triplestore_manager'))
        
        return result
    #load(rdf_map())
    
    # STEP 1
    x = rdf_map()
    # STEP 2
    load(x)
    
whow_flow()
