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
from src.apis.parameters.AbstractStringParameter import AbstractStringParameter 
from src.apis.ApiConstants import PARAMETER_TYPES

#=============================================================================
# Class
#=============================================================================
class UpperCaseStringParameter(AbstractStringParameter):
    ''' 
    This parameter parses a string value provided in the api call and converts
    it into an upper case string for searching the database. If a default value
    and/or enum are provided, they are also converted to upper case.
    '''

    #===========================================================================
    # Constructors
    #===========================================================================    
    ''' '''
    def __init__(self, name, description, alias=None, required=False, 
                 allow_multiple=True, default=None, enum=None, 
                 param_type=PARAMETER_TYPES.query):         # @UndefinedVariable
        
        super(UpperCaseStringParameter, self).__init__(name, alias, description, 
                                                       required, allow_multiple,
                                                       default, enum, 
                                                       param_type)
        
    #===========================================================================
    # Overriden Methods
    #===========================================================================    
    def update_case(self, s):
        return s.upper()
    
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    parameter = UpperCaseStringParameter("StringParameter", 
                                         "StringParameter description.",
                                         alias="StringParameterAlias",
                                         required=True, allow_multiple=False, 
                                         default="this", enum=['This', 'THaT'])
    print parameter
    print parameter._convert_args(['THiS', 'that'])