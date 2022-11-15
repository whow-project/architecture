import subprocess
from pelix.ipopo.decorators import ComponentFactory, Property, Provides, Instantiate, Validate
import json

@ComponentFactory('cleanser-factory')
@Property('_source_folder', 'cleanser.source_folder', '')
@Property('_dest_folder', 'cleanser.dest_folder', '')
@Provides('data-cleansing')
@Instantiate('data-cleansing-impl')
class Cleanser:
    
    @Validate
    def validate(self, context):
        with open('./data_cleansing/conf/props.json') as f:
            js = json.load(f)
            self._source_folder = js['dirty_data']
            self._dest_folder = js['cleaned_data']
            print(f'Dirty data folder: {self._source_folder}')
            print(f'Cleaned data folder: {self._dest_folder}')
            
        print(f'The data cleanser {self} has been activated.    ls')
    
    def clean(self):
        
        source_folder = self._source_folder
        dest_folder = self._dest_folder 
        
        command = f'/Users/andrea/git/whow-architecture/whow-toolkit/WHOWToolkit/data_cleansing/utf8-converter.sh'
        
        print(f'Running: {command} {source_folder} {dest_folder}')
        subprocess.call(['pwd'])
        subprocess.call(['sh', command, source_folder, dest_folder])
        