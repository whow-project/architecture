import pendulum

from airflow.decorators import dag, task
from pyrml import RMLConverter

import os, glob, uuid

from rdflib import Graph
from typing import List
import asyncio
import websockets
import uuid

os.environ["no_proxy"]="*"

async def communicate_with(host: str, port: str, path: str, message = ''):
    async with websockets.connect(f"ws://{host}:{port}/{path}") as websocket:
        await websocket.send(message)
        
        print(f'Sent request to {path}')
        
        data = await websocket.recv()
        #await data = websocket.recv()
        
        print(f'Received message of {path} completed')
        
    return data


@dag(
    schedule=None,
    start_date=pendulum.datetime(2022, 11, 8, tz="UTC"),
    catchup=False,
    tags=['whow-flow'],
)
def whow_flow():
    
    @task()
    def clean():
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(communicate_with('localhost', '8765', 'data-cleansing'))
        
        return result
    
    @task()
    def rdf_map(input: str):
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(communicate_with('localhost', '8765', 'rml_mapper'))
        
        id = f'{uuid.uuid4()}.nt.tag.gz'
        
        with open(id, 'wb') as binary_file:
            # Write bytes to file
            binary_file.write(result)
        
        return id 
        

    @task()
    def load(input):
        
        with open(input, "rb") as f:
            ba = bytearray(f.read())
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(communicate_with('localhost', '8765', 'triplestore_manager', ba))
        
        return result
    #load(rdf_map())
    
    # STEP 1
    clean_data = clean()
    # STEP 2
    rdf = rdf_map(clean_data)
    # STEP 2
    load(rdf)
    
whow_flow()
