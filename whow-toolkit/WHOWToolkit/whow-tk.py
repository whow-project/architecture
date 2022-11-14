from pelix.constants import BundleActivator
from pelix.framework import BundleContext, FrameworkFactory, Framework, create_framework
from builtins import classmethod
import os, csv, codecs, sys
from pathlib import Path
from machine_reading.api.api import GraphStore
        
        
class Toolkit(object): 
    
    __instance : 'Toolkit' = None
    __framework : Framework
        
    @classmethod
    def start(cls):
        if not cls.__instance:
            
            cls.__instance = Toolkit()
            
            bundles = [
                 "pelix.ipopo.core",
                 "pelix.shell.core",
                 "pelix.shell.ipopo",
                 "pelix.shell.completion.pelix",
                 "pelix.shell.completion.ipopo",
                 #"pelix.shell.console",
            ]
            
            modules = ['mappers', 'triplestores', 'web']
            
            cls.__framework = create_framework(bundles)
            cls.__framework.start()
            
            toolkit_bundles = []
            
            for module in modules : 
                for f in os.listdir(f'./{module}'):
                    if f.endswith('.py'):
                        f = f[:-3]
                        toolkit_bundles.append(cls.__framework.install_bundle(f, f'./{module}'))
            
            #mcr_bundles.append(cls.__framework.install_bundle('webapp', '.'))
            
            for bundle in toolkit_bundles:
                bundle.start()
                print(f'Started bundle {bundle}')
                
            print('Framework created.')    
            cls.__framework.wait_for_stop()
            
        else:
            return None
            
        
            
        
        
if __name__ == '__main__':
    sys.exit(Toolkit.start() or 0)
    