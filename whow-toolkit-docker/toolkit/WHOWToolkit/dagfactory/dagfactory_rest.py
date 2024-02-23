import os

from api.api import WebView, Configuration
from flask.views import MethodView
from pelix.ipopo.decorators import ComponentFactory, Property, Provides, Instantiate, Validate, Requires
from flask import request, abort, render_template, jsonify

from rdflib import Graph, RDF, RDFS, Namespace
from flask.wrappers import Response

import glob

import shortuuid
import json

import logging

@ComponentFactory("dagfactory-web-factory")
@Property('_name', 'webcomponent.name', 'dagfactory')
@Property('_path', 'webcomponent.path', '/api/dag/<dag_id>')
@Property('_context', 'webcomponent.context', __name__)
@Requires('_dagfactory','dagfactory')
@Provides('webcomponent')
@Instantiate("dagfactory-web-inst")
class DAGFactoryWeb(WebView):
    
    def __init__(self):
        super().__init__()
        self.__conf = Configuration('./dagfactory/conf/props.json')
        
        self._dags_folder = self.__conf.get_property('dags.folder')
        self._http_endpoint = self.__conf.get_property('http.endpoint')
        self._dagfactory = None
        
    @Validate
    def validate(self, context):
        print('DAGFactoryWeb is active!')
    
    
    def post(self, dag_id):
        
        supported_mime_types = ('application/rdf+xml', 'text/turtle', 'application/json-ld', 'application/json', 'application/n-triples')
        logging.info(f'DAG Factory content type {request.content_type.startswith("multipart/form-data")}')
        
        if not self._dagfactory:
            self._dagfactory = self._get_reference('dagfactory')
        
        if request.content_type.startswith('multipart/form-data'):
        
            #dag_id = request.form['dag_id']
            
            data = request.files['graph']
            
            
            if data:
                mimetype = data.content_type
                logging.info(f'DATA MIME TYPE {mimetype}.')
                if mimetype in supported_mime_types:
                    g = Graph()
                    g.parse(data, format=mimetype)
                    
                    flow = Namespace('https://w3id.org/whow/onto/flow/')

                    plans = g.subjects(RDF.type, flow.Plan, True)
                    
                    for plan in plans:
                    
                        sparql = f'''
                            PREFIX flow: <https://w3id.org/whow/onto/flow/>
                            CONSTRUCT {{ 
                                <{ plan }> ?p_plan ?o_plan . 
                                ?first_activity ?p_first_activity ?o_first_activity .
                                ?activity ?p_activity ?o_activity
                            }}
                            WHERE{{
                                <{ plan }> a flow:Plan;
                                    ?p_plan ?o_plan;
                                    flow:hasFirstActivity ?first_activity .
                                ?first_activity ?p_first_activity ?o_first_activity ;
                                    flow:hasNextActivity+ ?activity .
                                ?activity ?p_activity ?o_activity
                            }}
                        '''
                        
                        triples = g.query(sparql)
                        plan_graph = Graph()
                        
                        for triple in triples:
                            plan_graph.add(triple)
                            logging.info(triple)
                    
                        dag_uuid = shortuuid.uuid(str(plan))
                        
                        self._dagfactory.create_dag(dag_uuid, plan_graph)
                    
                    return "Success", 200
                else:
                    abort(406)
            else:
                abort(412)
        
        else:
            abort(406)
            
    def get(self, dag_id):
        
        supported_mime_types = ('application/rdf+xml', 'text/turtle', 'application/json-ld', 'application/json', 'application/n-triples', 'text/html')
        
        mime_types = [ctype for ctype in request.accept_mimetypes.values()]
            
        #if any(item in supported_mime_types for item in mime_types):
        if any(item.startswith(supported_mime_types) for item in mime_types):
            graph_file = os.path.join(self._dags_folder, f'{dag_id}.ttl')
            
            if os.path.exists(graph_file):
                
                g = Graph()
                g.parse(graph_file, format='text/turtle')
                
                return Response(g.serialize(format=mime_types[0]), mime_types[0])
            else:
                abort(404)
        else:
            abort(406)
        
    def delete(self, dag_id):
        graph_file = os.path.join(self._dags_folder, f'{dag_id}.ttl')
        
        if os.path.exists(graph_file):
            os.remove(graph_file)
            return "Success", 200
        else:
            abort(404)
            
    def set_web_services(self, services):
        self.__services = services
            
@ComponentFactory("dags-web-factory")
@Property('_name', 'webcomponent.name', 'dagstore')
@Property('_path', 'webcomponent.path', '/api/dags')
@Property('_context', 'webcomponent.context', __name__)
@Requires('_dagfactory', 'dagfactory')
@Provides('webcomponent')
@Instantiate("dagstore-web-inst")
class DAGStoreWeb(WebView):
    
    def __init__(self):
        super().__init__()
        self.__conf = Configuration('./dagfactory/conf/props.json')
        
        self._dags_folder = self.__conf.get_property('dags.folder')
        self._http_endpoint = self.__conf.get_property('http.endpoint')
        self._dagfactory = None
        
    @Validate
    def validate(self, context):
        
            
        print(f'DAGStoreWeb is active!')
    
    
    def get(self):
        
        logging.info('Received request for dags')
        supported_mime_types = ('application/rdf+xml', 'text/turtle', 'application/json-ld', 'application/json', 'application/n-triples', 'text/html')
        
        if not self._dagfactory:
            self._dagfactory = self._get_reference('dagfactory')
        
        mime_types = [ctype for ctype in request.accept_mimetypes.values()]
        
        if len(mime_types) == 0:
            mime_types = ['text/turtle']
            
        #if any(item in supported_mime_types for item in mime_types):
        if any(item.startswith(supported_mime_types) for item in mime_types):
            
            dags: Graph = self._dagfactory.dags()
            if dags is not None:
                    
                if any(item.startswith('text/html') for item in mime_types):
                    
                    flow = Namespace('https://w3id.org/whow/onto/flow/')
                    plans = dags.subjects(RDF.type, flow.Plan, True)
                    
                    plans = [(plan, dags.value(plan, RDFS.label, None, '')) for plan in plans]
                    
                    logging.info(f'Existing plans: {plans}')
                    
                    return render_template('dagfactory-dags.html', services=self.webservices, plans=plans)
                
                else:
                    return Response(response=dags.serialize(format=mime_types[0]), status='200 Success', mimetype=mime_types[0])
            else:
                abort(404)
        else:
            abort(406)
            
    def set_web_services(self, services):
        self.__services = services
        
@ComponentFactory("dag-web-factory")
@Property('_name', 'webcomponent.name', 'dag')
@Property('_path', 'webcomponent.path', '/api/<dag_id>')
@Property('_context', 'webcomponent.context', __name__)
@Provides('webcomponent')
@Instantiate("dag-web-conf")
class DAGWeb(WebView):
    
    def __init__(self):
        self.__conf = Configuration('./dagfactory/conf/props.json')
        
        self._dags_folder = self.__conf.get_property('dags.folder')
        self._http_endpoint = self.__conf.get_property('http.endpoint')
        
    @Validate
    def validate(self, context):
        print('DAG Conf is active!')
    
    
    def get(self, dag_id):
        
        logging.info('Received request for dag: {dag_id}')
        supported_mime_types = ('application/json', 'text/html')
        
        mime_types = [ctype for ctype in request.accept_mimetypes.values()]
        
        if len(mime_types) == 0:
            mime_types = ['text/turtle']
            
        
        dag_uuid = shortuuid.uuid(dag_id)
        
        folder = os.path.join(self._dags_folder, 'configs', dag_uuid)
            
        #if any(item in supported_mime_types for item in mime_types):
        if any(item.startswith(supported_mime_types) for item in mime_types):
            if os.path.exists(folder):
                
                dags = Graph()
                dag_files = glob.glob(f'{self._dags_folder}/*.ttl')
                
                for dag_file in dag_files:
                    dag = Graph()
                    dag.parse(dag_file, format='text/turtle')
                    dags += dag
                    
                if any(item.startswith('text/html') for item in mime_types):
                    
                    flow = Namespace('https://w3id.org/whow/onto/flow/')
                    plans = dags.subjects(RDF.type, flow.Plan, True)
                    
                    plans = [(plan, dags.value(plan, RDFS.label, None, '')) for plan in plans]
                    
                    logging.info(f'Existing plans: {plans}')
                    
                    return render_template('dagfactory-dags.html', services=self.webservices, plans=plans)
                
                else:
                    return Response(response=dags.serialize(format=mime_types[0]), status='200 Success', mimetype=mime_types[0])
            else:
                abort(404)
        else:
            abort(406)
            
    def set_web_services(self, services):
        self.__services = services
            
@ComponentFactory("dagconfs-web-factory")
@Property('_name', 'webcomponent.name', 'dag-configs')
@Property('_path', 'webcomponent.path', '/api/<path:dag_id>')
@Property('_context', 'webcomponent.context', __name__)
@Requires('_dagfactory','dagfactory')
@Provides('webcomponent')
@Instantiate("dagconfs-web-conf")
class DAGConfigsWeb(WebView):
    
    def __init__(self):
        super().__init__()
        self.__conf = Configuration('./dagfactory/conf/props.json')
        
        self._dags_folder = self.__conf.get_property('dags.folder')
        self._http_endpoint = self.__conf.get_property('http.endpoint')
        self._dagfactory = None
        
    @Validate
    def validate(self, context):
        print('DAG Configs is active!')
    
    
    def get(self, dag_id):
        
        logging.info(f'Received request for dag: {dag_id}')
        supported_mime_types = ('application/json', 'text/html')
        
        if not self._dagfactory:
            self._dagfactory = self._get_reference('dagfactory')
        
        mime_types = [ctype for ctype in request.accept_mimetypes.values()]
        
        if len(mime_types) == 0:
            mime_types = ['text/html', 'application/json']
            
        dag_uuid = shortuuid.uuid(dag_id)
        
        
        #if any(item in supported_mime_types for item in mime_types):
        if any(item.startswith(supported_mime_types) for item in mime_types):
            
            dag_configs = self._dagfactory.dag_configs(dag_uuid)
            
            logging.info(f'Dags configs is {dag_configs}.')
            if dag_configs is not None:
                if any(item.startswith('text/html') for item in mime_types):
                    
                    data = {
                        'services': self.webservices, 
                        'dag_id': dag_id, 
                        'configs': dag_configs, 
                        'airflow_endpoint': self._dagfactory.website_airflow_endpoint
                    }
                    return render_template('dagfactory-dag-configs.html', **data)
                else:
                    return Response(response=json.dumps(dag_configs), status='200 Success', mimetype='application/json')
            else:
                abort(404)
        else:
            abort(406)
            
    def set_web_services(self, services):
        self.__services = services
        
@ComponentFactory("dagconf-web-factory")
@Property('_name', 'webcomponent.name', 'dag-config')
@Property('_path', 'webcomponent.path', '/api/<path:dag_id>')
@Property('_context', 'webcomponent.context', __name__)
@Requires('_dagfactory','dagfactory')
@Provides('webcomponent')
@Instantiate("dagconf-web-conf")
class DAGConfigWeb(WebView):
    
    def __init__(self):
        super().__init__()
        self.__conf = Configuration('./dagfactory/conf/props.json')
        
        self._dags_folder = self.__conf.get_property('dags.folder')
        self._http_endpoint = self.__conf.get_property('http.endpoint')
        self._dagfactory = None
        
    @Validate
    def validate(self, context):
        print('DAG Conf is active!')
    
    
    def get(self, dag_id):
        
        supported_mime_types = ('application/json', 'text/html')
        
        if not self._dagfactory:
            self._dagfactory = self._get_reference('dagfactory')
        
        mime_types = [ctype for ctype in request.accept_mimetypes.values()]
        
        if len(mime_types) == 0:
            mime_types = ['text/html', 'application/json']
            
        dag_uuid = shortuuid.uuid(dag_id)
        
        
        #if any(item in supported_mime_types for item in mime_types):
        if any(item.startswith(supported_mime_types) for item in mime_types):
            
            flow = Namespace('https://w3id.org/whow/onto/flow/')
            dag: Graph = self._dagfactory.get_dag(dag_uuid)
            
            plan = dag.value(None, RDF.type, flow.Plan)
            
            activity = dag.value(plan, flow.hasFirstActivity, None)
            
            activities = []
            while activity:
                bound_service = dag.value(activity, flow.hasBoundService, None)
                activity = dag.value(activity, flow.hasNextActivity, None)
                
                activities.append(str(bound_service))
            
            logging.info(f'Available activities {activities}')
            
            dag_config_id = request.args.get('config_id')
            
            if dag_config_id:
                json_config = self._dagfactory.get_dag_config(dag_uuid, dag_config_id)
                
                mode: str = request.args.get('mode')
                if mode:
                    if mode.lower() == 'edit':
                        edit = True
                    else:
                        edit = False
                else:
                    edit = False
                    
                
                if any(item.startswith('text/html') for item in mime_types):
                    return render_template('dagfactory-dag-config-view.html', services=self.webservices, dag_id=dag_id, conf=json_config, edit=edit)
                else:
                    return Response(response=json.dumps(json_config), status='200 Success', mimetype='application/json')
            
            else:
                if any(item.startswith('text/html') for item in mime_types):
                    return render_template('dagfactory-dag-config-add.html', services=self.webservices, dag_id=dag_id, activities=activities)
                else:
                    abort(501)
        else:
            abort(406)
            
    def post(self, dag_id):
        
        if not self._dagfactory:
            self._dagfactory = self._get_reference('dagfactory')
        
        dag_uuid = shortuuid.uuid(dag_id)
        
        json_config = request.get_json()
        
        
        ret = self._dagfactory.add_dag_config(dag_uuid, json_config)
        
        if ret: 
            if ret['status'] == 'success':
                return 'Success', 200
            else:
                abort(Response(ret['explanation'], status=412))
        else:
            abort(Response('No workflow with ID {dag_id} exists in the system. Hence, no configuration can be added to such a workflow.', status=404))
        
            
            
    def set_web_services(self, services):
        self.__services = services
            
@ComponentFactory("dagfactory-webview-factory")
@Property('_name', 'webcomponent.name', 'workflow-mgr')
@Property('_path', 'webcomponent.path', '/')
@Property('_context', 'webcomponent.context', __name__)
@Provides('webviewcomponent')
@Instantiate("dagfactory-homepage")
class HomeWeb(WebView):
    
    def __init__(self):
        super().__init__()
        
    def get(self):
        logging.info("Dagfactory home page.")
        return render_template('dagfactory.html', services=self.webservices)
    
    
    def set_web_services(self, services):
        self.__services = services
        
@ComponentFactory("dagcreate-webview-factory")
@Property('_name', 'webcomponent.name', 'dagcreate')
@Property('_path', 'webcomponent.path', '/')
@Property('_context', 'webcomponent.context', __name__)
@Provides('webcomponent')
@Instantiate("dagcreate-instantiate")
class DAGCreateWeb(WebView):
    
    def __init__(self):
        super().__init__()
        
    def get(self):
        logging.info("Dagfactory Instantiate home page.")
        return render_template('dagfactory-instantiate.html', services=self.webservices)
    
    
    def set_web_services(self, services):
        self.__services = services
        
@ComponentFactory("dagstatus-web-factory")
@Property('_name', 'webcomponent.name', 'dag-status')
@Property('_path', 'webcomponent.path', '/api/<path:dag_id>')
@Property('_context', 'webcomponent.context', __name__)
@Requires('_dagfactory','dagfactory')
@Provides('webcomponent')
@Instantiate("dagstatus-web-conf")
class DAGStatus(WebView):
    def __init__(self):
        super().__init__()
        self._dagfactory = None
        
    def get(self, dag_id):
        if not self._dagfactory:
            self._dagfactory = self._get_reference('dagfactory')
            
        status = self._dagfactory.dag_status(dag_id)
        
        return Response(response=f'{{"status": "{status}"}}', status='200', mimetype='application/json')

@ComponentFactory("dagrun-web-factory")
@Property('_name', 'webcomponent.name', 'dag-run')
@Property('_path', 'webcomponent.path', '/api/<path:dag_id>')
@Property('_context', 'webcomponent.context', __name__)
@Requires('_dagfactory','dagfactory')
@Provides('webcomponent')
@Instantiate("dagrun-web-conf")
class DAGRun(WebView):
    def __init__(self):
        super().__init__()
        self._dagfactory = None
        
    def get(self, dag_id):
        
        if not self._dagfactory:
            self._dagfactory = self._get_reference('dagfactory')
        
        dag_config_id = request.args.get('config_id')
            
        ret = self._dagfactory.dag_run(dag_id, dag_config_id)
        
        if ret:
            return Response(response=f'{{"status": {ret}}}', status='200 Success', mimetype='application/json')
        else:
            abort(404)

        