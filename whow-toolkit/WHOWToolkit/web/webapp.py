from pelix.ipopo.decorators import ComponentFactory, Requires, Instantiate, Validate, Property, Provides, BindField, UnbindField

from api.api import WebView, RESTApp, _HTTPResource, WebSocketComponent

import asyncio
import threading
import websockets
import uuid
import os
import tarfile
import shutil

from typing import Dict

from flask import Flask
from websockets.server import WebSocketServerProtocol
import logging
from flask.views import MethodView
from flask import render_template, Blueprint
from _codecs import register


class WebSocketApp(object):
    
    PATH_REGISTRY: Dict[str, Dict[str,WebSocketComponent]] = dict()
    
    @classmethod
    async def _manage(cls, websocket: WebSocketServerProtocol, path: str):
        logging.info(f'Websocket: {websocket}')
        logging.info(f'Path: {path}')
        
        endpoint = f'{websocket.host}:{websocket.port}'
        logging.info(f'Request endpoint: {endpoint}')
        
        if endpoint in cls.PATH_REGISTRY:
            endpoint_services = cls.PATH_REGISTRY[endpoint]
            
            if path in endpoint_services:
                service: WebSocketComponent = endpoint_services[path]
                
                if service:
                    try:
                        message = await websocket.recv()
                        
                        out_message = service.execute(message)
                
                        await websocket.send(out_message)
                    except Exception as e:
                        logging.info('ERROR in websocket server handling {e}')
                        raise e
                    
                else:
                    logging.info('A path is registered, but service is None.')
                    
            else:
                logging.info(f'No path registered {path} for a websocket service.')
        else:
            logging.info(f'No WebSocket server is active and serving at {endpoint}.')
            
    @classmethod
    def start(cls, host, port):
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ws_server = websockets.serve(WebSocketApp._manage, host, port, ping_timeout=None)

        loop.run_until_complete(ws_server)
        loop.run_forever() # this is missing
        loop.close()

    @classmethod
    def register_service(cls, endpoint: str, path: str, service: WebSocketComponent):
        if endpoint not in cls.PATH_REGISTRY:
            cls.PATH_REGISTRY[endpoint] = dict()
            
        cls.PATH_REGISTRY[endpoint][path] = service
        print(f"Registerd websocket service {service} at path {endpoint}{service._path}")
            
    @classmethod
    def unregister_service(cls, endpoint: str, path: str):
        if endpoint in cls.PATH_REGISTRY:
            del(cls.PATH_REGISTRY[endpoint][path])

@ComponentFactory("websocket-factory")
@Property("_host", "server.host", "0.0.0.0")
@Property("_port", "server.port", "8765")
@Requires("_websocketcomponents", "websocketcomponent", aggregate=True)
@Instantiate("websocket-server")
class _WebSocketServer(object):
    
    
    @Validate
    def validate(self, context):
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(self.start_server())
        #asyncio.run(self.start_server()):
        
        server = threading.Thread(target=WebSocketApp.start, args=(self._host, self._port), daemon=True)
        server.start()
        
        print('WebSocket Server is UP!')
        
        
    @BindField('_websocketcomponents')
    def bind_dict(self, field, service, svc_ref):
        webcomponent_path = svc_ref.get_property('websocketcomponent.path')

        #self.__path_registry[service._path] = service
        
        WebSocketApp.register_service(f'{self._host}:{self._port}', service._path, service)

        print(f"Websocket server contains {len(self._websocketcomponents)} services.")
        
        
        
        
    @UnbindField('_websocketcomponents')
    def unbind_dict(self, field, service, svc_ref):
        WebSocketApp.unregister_service(f'{self._host}:{self._port}', path, service)


@ComponentFactory("http-server-factory")
@Property("_host", "http.server.host", "localhost")
@Property("_port", "http.server.port", "5000")
@Requires("_webcomponents", "webcomponent", aggregate=True)
@Requires("_webviewcomponents", "webviewcomponent", aggregate=True)
#@Provides("httpserver")
@Instantiate("httpserver-impl")
class HTTPServer(RESTApp):
    
    def __init__(self):
        super().__init__(self._port)
        
    
    @Validate
    def validate(self, context):
        logging.info(f"HTTP webapp is starting.")
        
    
    @BindField('_webcomponents')
    def bind_webcomponents(self, field, service, svc_ref):
        webcomponent_path= svc_ref.get_property('webcomponent.path')
        
        logging.info(f'** 1. name:{service._name} - context:{service._context} - urlprefix:{service._name} - path:{service._path}')
        if service._name in RESTApp.get_flask_app().blueprints:
            register_blueprint = False
            blp = RESTApp.get_flask_app().blueprints[service._name]
        else:
            register_blueprint = True
            blp = Blueprint(service._name, service._context, url_prefix=f'/{service._name}', template_folder='templates', static_folder='static')
        
        blp.add_url_rule(service._path, view_func=service.as_view(service._path))
        
        RESTApp.get_flask_app().register_blueprint(blp)
        
        
        #RESTApp.get_flask_app().add_url_rule(service._path, view_func=service.as_view(service._path))
        logging.info(f'Web component path: {service._path} {svc_ref}')
        
        logging.info(f"Web app running with {len(self._webcomponents)} web components.")
        
        
        
        
    @UnbindField('_webcomponents')
    def unbind_webcomponents(self, field, service, svc_ref):
        pass
    
    @BindField('_webviewcomponents')
    def bind_webviewcomponents(self, field, service, svc_ref):
        webcomponent_path= svc_ref.get_property('webcomponent.path')
        
        logging.info(f'** 2. name:{service._name} - context:{service._context} - urlprefix:{service._name} - path:{service._path}')
        
        if service._name in RESTApp.get_flask_app().blueprints:
            register_blueprint = False
            blp = RESTApp.get_flask_app().blueprints[service._name]
        else:
            register_blueprint = True
            blp = Blueprint(service._name, service._context, url_prefix=f'/{service._name}', template_folder='templates', static_folder='static')
        
        logging.info(f'ROOT PATH: {blp.root_path}')
        
        blp.add_url_rule(service._path, view_func=service.as_view(service._path))
        
        RESTApp.get_flask_app().register_blueprint(blp)
        
        
        #RESTApp.get_flask_app().add_url_rule(service._path, view_func=service.as_view(service._path))
        logging.info(f'Web View component path: {service._path} {svc_ref}')
        
        
        
        
        
    @UnbindField('_webviewcomponents')
    def unbind_webviewcomponents(self, field, service, svc_ref):
        pass
        
    @property
    def host(self):
        return self._host
    
    @property
    def port(self):
        return self._port

    '''
    def register_resource(self, func, path, *args, **kwargs):
        RESTApp.get_flask_app().add_url_rule(path, view_func=func.as_view(path), *args, **kwargs)
        print(f'2 Args: {path}')
        print(f'2 Registered resource {func}')
    '''
    
@ComponentFactory("web-factory")
@Property('_name', 'webcomponent.name', 'home')
@Property('_path', 'webcomponent.path', '/')
@Property('_context', 'webcomponent.context', __name__)
@Provides('webviewcomponent')
@Instantiate("homepage")
class HomeWeb(WebView):
    
    def __init__(self):
        super().__init__()
        
    def get(self):
        logging.info(f'Services viewed by HOMEPAGE {self.webservices}.')
        
        
        logging.info("Home page.")
        print("Home page.")
        return render_template('home.html', services=self.webservices)
    
    
    def set_web_services(self, services):
        self.__services = services
