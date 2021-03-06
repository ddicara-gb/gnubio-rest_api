'''
Copyright 2014 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Dan DiCara
@date:   Jun 1, 2014
'''

#=============================================================================
# Imports
#=============================================================================
from src.apis.AbstractGetFunction import AbstractGetFunction
from src.apis.parameters.ParameterFactory import ParameterFactory
from src import PROBES_COLLECTION
from src.apis.ApiConstants import ID

#=============================================================================
# Class
#=============================================================================
class ProbesGetFunction(AbstractGetFunction):
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def name():
        return "Probes"
   
    @staticmethod
    def summary():
        return "Retrieve list of available probes files."
    
    @staticmethod
    def notes():
        return ""
    
    @classmethod
    def parameters(cls):
        parameters = [
                      ParameterFactory.format(),
                     ]
        return parameters
    
    @classmethod
    def process_request(cls, params_dict):
        return (cls._DB_CONNECTOR.find(PROBES_COLLECTION, {}, {ID: 0}), None, None)
         
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    function = ProbesGetFunction()
    print function