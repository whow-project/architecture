import json
import os

from flask.helpers import send_file
from flask.views import MethodView
from pelix.ipopo.decorators import ComponentFactory, Property, Provides, Instantiate, Validate

from api.api import WebComponent


@ComponentFactory("webcomponent-factory")
@Property('_path', 'webcomponent.path', '/preprocessor/<file>')
@Provides('webcomponent')
@Instantiate("data-cleansing-web-inst")
class PreprocessorWeb(MethodView, WebComponent):
    
    def __init__(self):
        with open('./data_cleansing/conf/props.json') as f:
            js = json.load(f)
            self._dest_folder = js['cleaned_data']
            
    @Validate
    def validate(self, context):
        print('PreprocessorWeb is active!')
    
    def get(self, file):
        
        print(f'Dest folder {self._dest_folder}.')
        f = os.path.join(self._dest_folder, file)
        
        if os.path.exists(f):
            return send_file(f)
        else:
            abort(404)
        
    def delete(self, file):
        f = os.path.join(self._dest_folder, file)
        
        if os.path.exists(f):
            os.remove(f)
            return "Success", 200
        else:
            abort(404)