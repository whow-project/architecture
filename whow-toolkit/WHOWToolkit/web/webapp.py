from pelix.ipopo.decorators import ComponentFactory, Requires, Instantiate, Validate, Property, Provides

import asyncio
import websockets


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
            self._rml_mapper.map()
        elif path == '/triplestore_manager':
            self._triplestore_manager.load_graphs()
        elif path == '/data-cleansing':
            self._cleanser.clean()
        
        await websocket.send('mapping completed')
    
    async def start_server(self):
        async with websockets.serve(self._manage, self._host, self._port):
            await asyncio.Future()  # run forever
    
    @Validate
    def validate(self, context):
        print('Server')
        
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(self.start_server())
        asyncio.run(self.start_server())
    