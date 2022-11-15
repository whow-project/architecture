from pelix.ipopo.decorators import ComponentFactory, Requires, Instantiate, Validate, Property, Provides

import asyncio
import websockets
import uuid
import os
import tarfile


@ComponentFactory("websocket-factory")
@Property("_host", "server.host", "localhost")
@Property("_port", "server.port", "8765")
@Requires("_cleanser", "data-cleansing")
@Requires("_rml_mapper", "rml-mapper")
@Requires("_triplestore_manager", "triplestore-manager")
@Instantiate("websocket-server")
class WebSocketServer(object):
    
    
    async def _manage(self, websocket, path):
        print(f'Websocket: {websocket}')
        print(f'Path: {path}')
        
        if path == '/rml_mapper':
            out = self._rml_mapper.map()
            print(f'RDF file tar.gz {out}')
            with open(out, "rb") as f:
                ba = bytearray(f.read())
                await websocket.send(ba)
        elif path == '/triplestore_manager':
            data = await websocket.recv()
            
            id = uuid.uuid4()
            tar_file = f'{uuid.uuid4()}.nt.tar.gz'
            
            graph_path = os.path.join(self._triplestore_manager._graphs_folder, tar_file)
            
            print(f'The graph path is {graph_path}')
            with open(graph_path, 'wb') as binary_file:
                binary_file.write(data)
                
            tar = tarfile.open(os.path.join(graph_path))
            tar.extractall(self._triplestore_manager._graphs_folder)
            
            os.remove(graph_path)
            
            self._triplestore_manager.load_graphs()
            await websocket.send('mapping completed')
        elif path == '/data-cleansing':
            self._cleanser.clean()
            await websocket.send('mapping completed')
        
        #await websocket.send('mapping completed')
    
    async def start_server(self):
        async with websockets.serve(self._manage, self._host, self._port):
            await asyncio.Future()  # run forever
    
    @Validate
    def validate(self, context):
        print('Server')
        
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(self.start_server())
        asyncio.run(self.start_server())
    