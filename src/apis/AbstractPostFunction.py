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
from abc import ABCMeta

from src.apis.AbstractFunction import AbstractFunction 
from src.apis.ApiConstants import METHODS

#=============================================================================
# Class
#=============================================================================
class AbstractPostFunction(AbstractFunction):
    __metaclass__ = ABCMeta
    
    #===========================================================================
    # Overridden Methods
    #===========================================================================    
    @staticmethod
    def method():
        return METHODS.POST                                 # @UndefinedVariable
    
    @staticmethod
    def response_messages():
        return [
                { "code": 200, 
                  "message": "Record(s) posted successfully."},
                { "code": 403, 
                  "message": "File already exists. Delete the existing file and retry."},
                { "code": 415, 
                  "message": "File is not a valid FASTA file."},
                { "code": 500, 
                  "message": "Operation failed."},
               ]
    
    @classmethod
    def handle_request(cls, query_params, path_fields):
        '''
        Example API call: http://<hostname>:<port>/api/v1/MeltingTemperatures/<user>/IDT?name=foo&sequence=bar
        
        In the above example, query_params would be {"name": "foo", 
        "sequence": "bar"} and path_fields would be [<user>]. After collecting 
        input parameters, call process_request(). Then return the results in the 
        requested format.
        '''
        (params_dict, _) = cls._parse_query_params(query_params)
        cls._handle_path_fields(path_fields, params_dict)
        
        return (cls.process_request(params_dict), None, None)