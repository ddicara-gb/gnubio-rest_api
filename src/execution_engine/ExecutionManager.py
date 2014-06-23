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

#===============================================================================
# Imports
#===============================================================================

#===============================================================================
# Imports
#===============================================================================

#===============================================================================
# Class
#===============================================================================
class ExecutionManager(object):
    '''
    This class is intended to be a singleton. It handles communication (i.e.
    queries) with MongoDB. Every call to the DB should go through this 
    class.
    '''
    _INSTANCE  = None
    _JOB_QUEUE = []
    
    #===========================================================================
    # Constructor
    #===========================================================================
    def __init__(self):
        # Enforce that it's a singleton
        if self._INSTANCE:
            raise Exception("%s is a singleton and should be accessed through the Instance method." % self.__class__.__name__)
    
    @classmethod
    def Instance(cls):
        if not cls._INSTANCE:
            cls._INSTANCE = ExecutionManager()
        return cls._INSTANCE
    
    #===========================================================================
    # Simple get methods
    #===========================================================================
        
#===========================================================================
# Ensure the initial instance is created.
#===========================================================================    
ExecutionManager.Instance()