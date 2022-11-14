import subprocess
from pelix.ipopo.decorators import ComponentFactory, Property, Provides, Instantiate, Validate

@ComponentFactory('cleanser-factory')
@Property('_source_folder', 'cleanser.source_folder', '/Users/andrea/airflow/dirtydata/')
@Property('_dest_folder', 'cleanser.dest_folder', '/Users/andrea/airflow/data/')
@Provides('data-cleansing')
@Instantiate('data-cleansing-impl')
class Cleanser:
    
    @Validate
    def validate(self, context):
        print(f'The data cleanser {self} has been activated.    ls')
    
    def clean(self):
        
        source_folder = self._source_folder
        dest_folder = self._dest_folder 
        
        command = f'/Users/andrea/git/whow-architecture/whow-toolkit/WHOWToolkit/data_cleansing/utf8-converter.sh'
        
        print(f'Running: {command} {source_folder} {dest_folder}')
        subprocess.call(['pwd'])
        subprocess.call(['sh', command, source_folder, dest_folder])
        