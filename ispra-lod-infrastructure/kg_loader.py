from rdflib import Graph
from rdflib.store import Store
#from SPARQLWrapper import SPARQLWrapper
from rdflib.plugin import get as plugin
import os, sys
import configuration as conf
import vstroke
#from virtuoso.vsparql import Result
#import virtuoso
import gzip, tarfile
from builtins import staticmethod
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
import multiprocessing as mp
import time, traceback

'''
def synchronized(func):
	
    func.__lock__ = threading.Lock()
		
    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func
'''

class KnowledgeGraph():
    
    @staticmethod
    def add_all(g1, g2):
        for (s,p,o) in g2:
            g1.add((s,p,o))
        return g1

class KnowledgeGraphLoader():

    def __init__(self, lock=None):
        self.__lock = lock
        self.__connect()
        
    def add_all_triples_to_graph(self, g1, g2):
        for (s,p,o) in g2:
            g1.add((s,p,o))
        return g1
 

    def upload_triple_file(self,ipaddr,user,passwd,file,folder):

        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(hostname=ipaddr, port='22', username=user, password=passwd)

        scp = SCPClient(ssh.get_transport())
        print ('Uploading', file, 'to', user + '@' + ipaddr, '...')
        scp.put(file,folder)


    def toLoad_toDelete_2 (self, new_graph, name, dataset):
        
        #as toLoad_toDelete, but returns folder of produced files
        kg_folder = os.path.join("rdf", dataset, "kg")
        kg_name = name.lower() + ".nt.gz"
        kg_path = os.path.join(kg_folder, kg_name)
        
        if not os.path.exists(os.path.dirname(kg_path)):
            os.makedirs(os.path.dirname(kg_path))
            
        
        
        if os.path.isfile(kg_path):
        
            with gzip.open(kg_path, 'rb') as f:
                graph_string = f.read()
        
            old_graph = Graph()
            
            old_graph.parse(data = graph_string, format="nt11")
            
            to_load = new_graph - old_graph
            to_delete = old_graph - new_graph
            
            #new_graph.serialize(kg_path, format="nt11")

            try:
                '''
                TODO: It is possible to modify self.__delete() in order to use iSQL instead of VStroke 
                (i.e. the RDFLib extension for Virtuoso)  
                '''
                deleted = self.__delete(to_delete, dataset)
            except:
                self.__save_graph(os.path.join(kg_folder, name.lower()), "delete.nt.gz", to_delete)
                deleted = False
            
            try:
                '''
                TODO: It is possible to modify self.__load() in order to use iSQL instead of VStroke 
                (i.e. the RDFLib extension for Virtuoso)  
                '''
                loaded = self.__load(to_load, dataset)
            except:
                self.__save_graph(os.path.join(kg_folder, name.lower()), "load.nt.gz", to_load)
                loaded = False
                
            
            if deleted and loaded: 
                ret = True
            else:
                ret = False

        else:
            try:
                loaded = self.__load(new_graph, dataset)
            except:
                loaded = False
                self.__save_graph(os.path.join(kg_folder, name.lower()), "load.nt.gz", new_graph)
                
                
            if loaded:                    
                ret = True
            else:
                ret = False
                
        graph_string = new_graph.serialize(format="nt11")
        
        with gzip.open(kg_path, 'wt') as f:
            f.write(graph_string)

        return kg_path, (os.path.join(kg_folder, name.lower(), "load.nt.gz")), (os.path.join(kg_folder, name.lower(), "delete.nt.gz"))


    def toLoad_toDelete (self, new_graph, name, dataset):
        
        kg_folder = os.path.join("rdf", dataset, "kg")
        kg_name = name.lower() + ".nt.gz"
        kg_path = os.path.join(kg_folder, kg_name)
        
        if not os.path.exists(os.path.dirname(kg_path)):
            os.makedirs(os.path.dirname(kg_path))
            
        
        
        if os.path.isfile(kg_path):
        
            with gzip.open(kg_path, 'rb') as f:
                graph_string = f.read()
        
            old_graph = Graph()
            
            old_graph.parse(data = graph_string, format="nt11")
            
            to_load = new_graph - old_graph
            to_delete = old_graph - new_graph
            
            #new_graph.serialize(kg_path, format="nt11")

            try:
                '''
                TODO: It is possible to modify self.__delete() in order to use iSQL instead of VStroke 
                (i.e. the RDFLib extension for Virtuoso)  
                '''
                deleted = self.__delete(to_delete, dataset)
            except:
                self.__save_graph(os.path.join(kg_folder, name.lower()), "delete.nt.gz", to_delete)
                deleted = False
            
            try:
                '''
                TODO: It is possible to modify self.__load() in order to use iSQL instead of VStroke 
                (i.e. the RDFLib extension for Virtuoso)  
                '''
                loaded = self.__load(to_load, dataset)
            except:
                self.__save_graph(os.path.join(kg_folder, name.lower()), "load.nt.gz", to_load)
                loaded = False
                
            
            if deleted and loaded: 
                ret = True
            else:
                ret = False

        else:
            try:
                loaded = self.__load(new_graph, dataset)
            except:
                loaded = False
                self.__save_graph(os.path.join(kg_folder, name.lower()), "load.nt.gz", new_graph)
                
                
            if loaded:                    
                ret = True
            else:
                ret = False
                
        graph_string = new_graph.serialize(format="nt11")
        
        with gzip.open(kg_path, 'wt') as f:
            f.write(graph_string)

        return ret
        
    def __save_graph(self, place, file_name, graph):
        if not os.path.exists(place):
            os.makedirs(place)
                    
        gzip_nt = os.path.join(place, file_name)
                    
        with gzip.open(gzip_nt, 'wt') as f:
            f.write(graph.serialize(format="nt11"))

    #@synchronized
    def __load(self, graph, dataset):
        #store = virtuoso.vstore.Virtuoso("DSN=VOS;UID=dba;PWD=dba")
        dataset_uri = conf.dataset_mappings[dataset]
        
        
        if dataset_uri is not None and len(graph) > 0:
            counter = 0
        
            g = Graph()
            for sub, pred, obj in graph:
                g.add((sub, pred, obj))
                counter += 1
            
                if counter == conf.triplestore_triples_upload_limit:
                    counter = 0
                    
                    #if self.__lock is not None:
                    #    self.__lock.acquire()
                    
                    query = "INSERT DATA { GRAPH <" + dataset_uri + "> {" + g.serialize(format="nt11").decode("utf-8") + "}}"
                    try:
                        ret = self.__query(query)
                    except:
                        raise
                    
                    g = Graph()
                    
                    #if self.__lock is not None:
                    #    self.__lock.release()
            
                #store.close()
                else: 
                    ret = True
                
            if len(g) > 0:
                query = "INSERT DATA { GRAPH <" + dataset_uri + "> {" + g.serialize(format="nt11").decode("utf-8") + "}}"
                ret = self.__query(query)
        
        
            
        return ret
            
    def delete(self, graph, dataset):
        query = "DELETE DATA { GRAPH <" + dataset + "> {" + graph.serialize(format="nt11").decode("utf-8") + "}}"
        post_query(query)
    
    
    #@synchronized
    def __delete(self, graph, dataset):
        
        dataset_uri = conf.dataset_mappings[dataset]
        
        if dataset_uri is not None and len(graph) > 0:
            counter = 0
        
            g = Graph()
            for sub, pred, obj in graph:
                g.add((sub, pred, obj))
                counter += 1
            
                if counter == conf.triplestore_triples_upload_limit:
                    counter = 0
                    #if self.__lock is not None:
                    #    self.__lock.acquire()
                    
                    query = "DELETE DATA { GRAPH <" + dataset_uri + "> {" + g.serialize(format="nt11").decode("utf-8") + "}}"
                    try:
                        ret = self.__query(query)
                    except:
                        raise
                    
                    g = Graph()
                    
                    #if self.__lock is not None:
                    #    self.__lock.release()
            
                #store.close()
                else: 
                    ret = True
                
            if len(g) > 0:
                query = "DELETE DATA { GRAPH <" + dataset_uri + "> {" + g.serialize(format="nt11").decode("utf-8") + "}}"
                ret = self.__query(query)
                
        return ret
    

    def loadByFile(self, file, dataset):
        path = str(os.path.abspath(file)).replace("\\", "/")
        query = "LOAD <file:" + path + "> INTO GRAPH <" + dataset + ">"
        post_query(query)

    #Ancillary functions
    def post_query (self, query):
        ts = SPARQLWrapper(conf.triplestore_url)
        ts.setMethod('POST')
        ts.setQuery(query)
        ts.query()
        
    def __query(self, query):
        #self.__reconnect()
        
        '''
        TODO: Here we implement the connectivity with the triplestore via RDFLib.
        It is possible to change this behaviour by modifying this method.
        For example, it might be the case of executing an iSQL command via bash (e.g. with a dedicated routine).
        '''
        if self._store is not None:
            try:
                self._store._query(query, commit=True)
                return True
            except Exception:
                print("The DB connection is down and this prevent querying DB...trying to reconnect")
                print(query)
                self.__close()
                time.sleep(conf.triplestore_connection_retry_sleep)
                #self.__query(query)
                raise
        else:
            return False
        
    def __reconnect(self):
        i = 0
        while i < conf.triplestore_connection_retry_attempts and self._store is None:
            print("Connection attempt no. %d"%((i+1)))

            if self.__connect() is None:
                time.sleep(conf.triplestore_connection_retry_sleep)

            i += 1
                
        if self._store is None:
            print("After %d attempts no DB connection can be established."%conf.triplestore_connection_retry_attempts)
            
        return self._store
        
        
        
    def __connect(self):
        store = None
        try:
            #self._store = vstroke.Virtuoso("DSN=VOS;UID=dba;PWD=dba;WideAsUTF16=Y")
            store = vstroke.Virtuoso("DSN=VOS;UID=dba;PWD=dba")
            
        except Exception:
            print("The DB connection cannot be established.")
            
        self._store = store
            
        return self._store
        
        
    def __close(self):
        try:
            self._store.close()  
        except:
            print("The DB connection has been already closed probably.")

    def __del__(self):
        print("Closing connection gracefully.")
        self.__close()
        
    @staticmethod
    def upload(data_collection, tar_path, remote_triplestore_folder):
        if os.path.exists(data_collection) and os.path.isdir(data_collection):
            with tarfile.open(tar_path, "w:gz") as tar:
                for rdf in os.listdir(data_collection):
                    tar.add(os.path.join(data_collection, rdf), arcname=rdf, recursive=True)
            
            ssh = SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(conf.triplestore_host, username=conf.triplestore_host_username, password=conf.triplestore_host_password)
            
            scp = SCPClient(ssh.get_transport())
            scp.put(tar_path, remote_path=remote_triplestore_folder)
            
            scp.close()
            
            stdin, stdout, stderr = ssh.exec_command("cd " + remote_triplestore_folder + "; tar -xvzf " + os.path.basename(tar_path))
            for line in stdout:
                print('... ' + line.strip('\n'))
            for line in stderr:
                print('... ' + line.strip('\n'))
            ssh.close()

        

