'''
[LICENSE]
Copyright (c) 2015, Alliance for Sustainable Energy.
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided 
that the following conditions are met:

1. Redistributions of source code must retain the above 
copyright notice, this list of conditions and the 
following disclaimer.

2. Redistributions in binary form must reproduce the 
above copyright notice, this list of conditions and the 
following disclaimer in the documentation and/or other 
materials provided with the distribution.

3. Neither the name of the copyright holder nor the 
names of its contributors may be used to endorse or 
promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND 
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

If you use this work or its derivatives for research publications, please cite:
Timothy M. Hansen, Bryan Palmintier, Siddharth Suryanarayanan, 
Anthony A. Maciejewski, and Howard Jay Siegel, "Bus.py: A GridLAB-D 
Communication Interface for Smart Distribution Grid Simulations," 
in IEEE PES General Meeting 2015, Denver, CO, July 2015, 5 pages.
[/LICENSE]
Created on Aug 10, 2015

@author: thansen
'''

from buspy.controller.utils import set_gld_property
import buspy.comm.message as message
from buspy.controller.eventqueue import diff_seconds_from_dates
import pandas as pd

class Model(object):
    PHASE_A = 1
    PHASE_B = 2
    PHASE_C = 3
    
    #JSON IDs
    JSON_NAME       = 'Name'
    JSON_BUSNUM     = 'BusNum'
    JSON_GLMBUS     = 'GLMBusName'
    
    JSON_SCH_TIME   = 'Time'
    JSON_SCH_SET    = 'SetPoint'
    
    def __init__(self,name,bus_num,glm_bus_name,start_date):
        self.name = name
        self.bus_num = bus_num
        self.glm_bus_name = glm_bus_name
        
        self.start_date  = start_date
        self.last_update = start_date
        self.delta = 0.0 #number of seconds since last update
        
        #format: time:commonparam to be sent to gridlabd
        self.setpoints = {}
    
    def parse_schedule(self,sch,param_name):
        for setpoint in sch:
            self.setpoints[pd.to_datetime(setpoint[Model.JSON_SCH_TIME])] = message.CommonParam(name=self.name,param=param_name, value=setpoint[Model.JSON_SCH_SET])
        
        
    def update_state(self,time,setpoint):
        self.delta = diff_seconds_from_dates(self.last_update,time)
        updated_setpoint = self._local_update(setpoint)
        self.last_update = time
        return updated_setpoint
        
    def _local_update(self,setpoint):
        raise Exception('Subclasses of Model should implement _local_update')
#     
#     def setpoints(self,bus):
#         for param,val in self.setpoints.iteritems():
#             set_gld_property(bus,self.name,param,val)
    
    @staticmethod
    def json_common_model_params(json_obj):
        return json_obj[Model.JSON_NAME], json_obj[Model.JSON_BUSNUM], json_obj[Model.JSON_GLMBUS] 
    

import battery
#import generator
import load

from battery import Battery
from load import Load


def json_to_model(json_str,json_obj,cur_time):
    switch_statement = {
        Battery.JSON_STRING         : Battery.json_to_battery,
        Load.JSON_STRING            : Load.json_to_load,
    }
    
    return switch_statement[json_str](json_obj,cur_time)
    