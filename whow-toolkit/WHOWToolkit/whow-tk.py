from pelix.constants import BundleActivator
from pelix.framework import BundleContext, FrameworkFactory, Framework, create_framework

from builtins import classmethod
import os, csv, codecs, sys
from pathlib import Path
import logging

logging.basicConfig(filename='./logs/mapping.log', level=logging.INFO)
        
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
            
            #modules = ['triplifier', 'triplestores', 'web']
            #modules = ['ingestion', 'data_cleansing', 'triplifier', 'metadata', 'validator', 'triplestores', 'web']
            modules = ['triplifier', 'dagfactory', 'web']
            
            cls.__framework = create_framework(bundles)
            cls.__framework.start()
            
            ctx: BundleContext = cls.__framework.get_bundle_context()
            
            toolkit_bundles = []
            
            for module in modules :
                print(module) 
                _core_modules = []
                _rest_modules = []
                _ws_modules = []
                _other_modules = []
                for f in os.listdir(f'./{module}'):
                    if f.endswith('.py'):
                        f = f[:-3]
                        if f.endswith('_core'):
                            _core_modules.append(f)
                        elif f.endswith('_rest'):
                            _rest_modules.append(f)
                        elif f.endswith('_ws'):
                            _ws_modules.append(f)
                        else:
                            _other_modules.append(f)
                
                _bundles = _core_modules + _rest_modules + _ws_modules + _other_modules
                for _bundle in _bundles:
                    toolkit_bundles.append(ctx.install_bundle(_bundle, f'./{module}'))
                    print(f'Installed bundle {module}/{_bundle}')
            
            #mcr_bundles.append(cls.__framework.install_bundle('webapp', '.'))
            
            print(f'toolkit_bundles: {toolkit_bundles}')
            
            for bundle in toolkit_bundles:
                bundle.start()
                print(f'Started bundle {bundle}')
                
            ref_config = ctx.get_service_reference("ingester")
            
            print(f'Framework created {cls.__framework} - {ref_config}')    
            cls.__framework.wait_for_stop()
            
        else:
            return None
            
        
            
        
        
if __name__ == '__main__':
    sys.exit(Toolkit.start() or 0)
    