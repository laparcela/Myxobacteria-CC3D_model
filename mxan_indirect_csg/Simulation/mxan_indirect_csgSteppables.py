
from PySteppables import *
import CompuCell
import sys
from Python_MXAN_GRN import InternalNetwork as GRN
import random
import os.path
import time
import CompuCellSetup
import math


######################################################################################################
###############################               PARAMETERS               ###############################
######################################################################################################

path_to_directory = "/srv/home/jarias/mxan_indirect_csg/"

nut_thr = 0.1
nut_consumption_rate = 0.5
nut_diff = 0.1

asg_initial_conc = 0.1
asg_prod_rate = 1.75 
asg_diff = 0.1 ### ParameterScan:diffA
asg_dt = 0.1
asg_thr = 0.5

csg_initial_conc = 0.001
csg_prod_rate = 1.75 ### ParameterScan:rate
csg_diff = 0.001 ### ParameterScan:diffC
csg_dt = 0.1
csg_thr = 0.25
######################################################################################################

######################################################################################################
###############################                PROCESSES               ###############################
######################################################################################################

class ConstraintInitializerSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
    def start(self):
        for cell in self.cellList:
            cell.targetVolume=25
            cell.lambdaVolume=2.0
        
        

class DeathSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
    def step(self,mcs):
        for cell in self.cellList:
            if not cell.dict['BoolNetwork'].state['NLA6'] and cell.dict['BoolNetwork'].state['MAZF'] and not cell.dict['BoolNetwork'].state['FRUA'] and not cell.dict['BoolNetwork'].state['DEVTRS']:
                cell.targetVolume=0
                cell.lambdaVolume=100

###################################### Nutrients consumption #########################################

class ManageNutrientsSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
    def start(self):
        NUT = self.getConcentrationField("nutrients")
        for xdim in range(self.dim.x):
            for ydim in range(self.dim.y):
                NUT[xdim, ydim, 0] = 0.0
        NUT[1,1,0] = 1.0
        for cell in self.cellList:
            cell.dict['nut_cont'] = 0.25
    def step(self,mcs):
        NUT = self.getConcentrationField("nutrients")
        for cell in self.cellList:
            nut_int = cell.dict['nut_cont']
            nut_ext = NUT[cell.xCOM, cell.yCOM, cell.zCOM] 
            cell.dict['nut_cont'] = nut_int*nut_consumption_rate + nut_diff*nut_ext
            NUT[cell.xCOM, cell.yCOM, cell.zCOM] = (1 - nut_diff)*nut_ext


########################################### A-signaling ##############################################

class ManageAsignalSteppable(SteppableBasePy):
        
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
    def start(self):
        ASG = self.getConcentrationField("asg")
        for xdim in range(self.dim.x):
            for ydim in range(self.dim.y):
                ASG[xdim, ydim, 0] = 0
                
        for cell in self.cellList:
            cell.dict['asg_cont'] = asg_initial_conc
    
    def step(self, mcs):
        ASG = self.getConcentrationField("asg")
        for cell in self.cellList:
            if cell.dict['BoolNetwork'].state['DEVTRS'] and not cell.dict['BoolNetwork'].state['MAZF'] and cell.dict['BoolNetwork'].state['FRUA']:
                pass
            else:
                ASG_int = cell.dict['asg_cont']
                ASG_ext = ASG[cell.xCOM, cell.yCOM, cell.zCOM]
                if cell.dict['BoolNetwork'].state['ASGAB'] == True and cell.dict['BoolNetwork'].state['ASGE'] == True:
                    cell.dict['asg_cont'] = ASG_int + asg_dt*asg_prod_rate*ASG_int*(1 - ASG_int) - asg_diff*(ASG_int - ASG_ext)
                    ASG[cell.xCOM, cell.yCOM, cell.zCOM]  = ASG_ext - asg_diff*(ASG_ext - ASG_int)
                
            
########################################### C-signaling ##############################################


class ManageCsignalSteppable(SteppableBasePy):
        
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
    def start(self):
        CSG = self.getConcentrationField("csg")
        for xdim in range(self.dim.x):
            for ydim in range(self.dim.y):
                CSG[xdim, ydim, 0] = 0
                
        for cell in self.cellList:
            cell.dict['csg_cont'] = csg_initial_conc
    
    def step(self, mcs):
        CSG = self.getConcentrationField("csg")
        for cell in self.cellList:
            if cell.dict['BoolNetwork'].state['DEVTRS'] and not cell.dict['BoolNetwork'].state['MAZF'] and cell.dict['BoolNetwork'].state['FRUA']:
                pass
            else:
                CSG_int = cell.dict['csg_cont']
                CSG_ext = CSG[cell.xCOM, cell.yCOM, cell.zCOM]
                if cell.dict['BoolNetwork'].state['NLA28'] or (cell.dict['BoolNetwork'].state['CSGA'] and cell.dict['BoolNetwork'].state['FRUA']):
                    cell.dict['csg_cont'] = CSG_int + csg_dt*csg_prod_rate*CSG_int*(1 - CSG_int) - csg_diff*(CSG_int - CSG_ext)
                    CSG[cell.xCOM, cell.yCOM, cell.zCOM]  = CSG_ext - csg_diff*(CSG_ext - CSG_int)
                    
################################# Gene regulatory network dynamic ####################################

class InternalNetworkSteppable(SteppableBasePy):    
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
    def start(self):
        state = {'NUT': True, 'RELA': False, 
            'ASGAB': False, 'ASGE': False, 'ASG': False,
            'NLA4': False, 'NLA18': False, 'NLA6': False, 'NLA28': False, 'CSGA': False,
            'PKTD9': True, 'PEP': True, 'PKTD1': False, 'MKAPB': False, 'PKTA4': False,
            'PKTA2': False, 'MKAPA': True, 'PKTC2': True, 'PSKA5': True,
            'MRPC2': False, 'FRUA': False, 'DEVTRS': False, 'MAZF': False}
        for cell in self.cellList:
            cell.dict['BoolNetwork'] = GRN(state.copy())
    def step(self,mcs):        
        for cell in self.cellList:
            if cell.dict['BoolNetwork'].state['DEVTRS'] and not cell.dict['BoolNetwork'].state['MAZF'] and cell.dict['BoolNetwork'].state['FRUA']:
                pass
            else:
                if cell.dict['nut_cont'] < nut_thr:
                    cell.dict['BoolNetwork'].state['NUT'] = False
                else:
                    cell.dict['BoolNetwork'].state['NUT'] = True
                if cell.dict['asg_cont'] > asg_thr:
                    cell.dict['BoolNetwork'].state['ASG'] = True
                else:
                    cell.dict['BoolNetwork'].state['ASG'] = False
                if cell.dict['csg_cont'] > csg_thr and (cell.dict['BoolNetwork'].state['MRPC2'] or (cell.dict['BoolNetwork'].state['FRUA'] and cell.dict['BoolNetwork'].state['DEVTRS'])):
                    cell.dict['BoolNetwork'].state['FRUA'] = True
                else:
                    cell.dict['BoolNetwork'].state['FRUA'] = False
                if cell.dict['BoolNetwork'].state['NLA28'] or (cell.dict['csg_cont'] > csg_thr and cell.dict['BoolNetwork'].state['FRUA']):
                       cell.dict['BoolNetwork'].state['CSGA'] = True
                else:
                    cell.dict['BoolNetwork'].state['CSGA'] = False
                cell.dict['BoolNetwork'].update()
    def finish(self):
        pass


######################################################################################################
###############################             VISUALIZATION              ###############################
######################################################################################################

############################################## GRN State #############################################

class StateFieldSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        self.scalarFieldState = CompuCellSetup.createScalarFieldCellLevelPy("State")
    def step(self,mcs):
        self.scalarFieldState.clear()
        for cell in self.cellList:
            self.scalarFieldState[cell]=math.log(cell.dict['BoolNetwork'].numeric_state())
            
########################################### A-signaling ##############################################

class AsgAFieldSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        self.scalarFieldAsgA = CompuCellSetup.createScalarFieldCellLevelPy("cell_asg")
        
    def step(self,mcs):
        self.scalarFieldAsgA.clear()
        
        for cell in self.cellList:
            if cell:
                self.scalarFieldAsgA[cell] = cell.dict['asg_cont']

########################################### C-signaling ##############################################

class CsgAFieldSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        self.scalarFieldCsgA = CompuCellSetup.createScalarFieldCellLevelPy("cell_csg")
        
    def step(self,mcs):
        self.scalarFieldCsgA.clear()
        
        for cell in self.cellList:
            if cell:
                self.scalarFieldCsgA[cell] = cell.dict['csg_cont']
                
########################################### Fate ##############################################

class FateFieldSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        self.scalarFieldFate = CompuCellSetup.createScalarFieldCellLevelPy("Fate")
        
    def step(self,mcs):
        self.scalarFieldFate.clear()
        
        for cell in self.cellList:
            if cell:
                if cell.dict['BoolNetwork'].state['DEVTRS'] and not cell.dict['BoolNetwork'].state['MAZF'] and cell.dict['BoolNetwork'].state['FRUA']:
                    self.scalarFieldFate[cell] = 1
                elif not cell.dict['BoolNetwork'].state['DEVTRS'] and cell.dict['BoolNetwork'].state['MAZF'] and not cell.dict['BoolNetwork'].state['FRUA']:
                    self.scalarFieldFate[cell] = 2
                else:
                    self.scalarFieldFate[cell] = 0

######################################################################################################
###############################              DATA OUTPUT               ###############################
######################################################################################################

class HandleOutputDataSteppable(SteppableBasePy):
	def __init__(self,_simulator,_frequency = 1):
		SteppableBasePy.__init__(self,_simulator,_frequency)
	def start(self):
		### Initialize file information...
		file_name = "output_data_"+ str(time.time()) + ".txt"
		path_to_file = path_to_directory + file_name
		self.output_data = open(path_to_file, "w")
                self.output_data.write("### Parameters:\n")
		
		### Cell attributes to extract
		self.attributes_to_extract = ['id', 'xCOM', 'yCOM']
		### Cell attributes to extract from dict
		self.attributes_to_extract_from_dict = ['nut_cont', 'asg_cont', 'csg_cont'] 
                
                ### Internal cellular network
                self.internal_network = True
                
                self.fate = True

                
		### Cell neighbordhood
		### This variable is True is you want to print the cell-to-cell neighbors. It is false otherwise.
		self.cell_neighborhood = True

		### Fields to extract
		### Note that this list may be an empty list.
		self.fields_to_extract = ['asg', 'csg']
	def step(self, mcs):
		### Cell atributes
		for attribute in self.attributes_to_extract:
			self.output_data.write("MCS" + str(mcs)+ "\tCELL_ATTRIBUTE\t" + attribute + ":\t")
			for cell in self.cellList:
				cellattr = getattr(cell, attribute)
				self.output_data.write(" " + str(cellattr))
			self.output_data.write("\n")

		for attribute in self.attributes_to_extract_from_dict:
			self.output_data.write("MCS" + str(mcs)+ "\tCELL_ATTRIBUTE\t" + attribute + ":\t")
			for cell in self.cellList:
				self.output_data.write(" " + str(cell.dict[attribute]))
			self.output_data.write("\n")
		
                ### Internal network
                if(self.internal_network):
                    self.output_data.write("MCS" + str(mcs)+ "\tCELL_ATTRIBUTE\tBOOLNETWORK:\t")
                    for cell in self.cellList:
                        self.output_data.write(" " + str(cell.dict['BoolNetwork'].numeric_state()))
                    self.output_data.write("\n")
                    
                if(self.fate):
                    self.output_data.write("MCS" + str(mcs)+ "\tCELL_ATTRIBUTE\tCELL_FATE:\t")
                    for cell in self.cellList:
                        self.output_data.write(" " + str(int(cell.dict['BoolNetwork'].state['DEVTRS']) + 2*int(cell.dict['BoolNetwork'].state['MAZF'])))
                    self.output_data.write("\n")
                    
		### Cell interactions
		if(self.cell_neighborhood):
                        self.output_data.write("MCS" + str(mcs)+ "\tCELL_INTERACTION\tCELL_NEIGHBORS:\t")
			for cell in self.cellList:
				for neighbor , commonSurfaceArea in self.getCellNeighborDataList(cell):
					if neighbor:
                                            if neighbor.id > cell.id:
						self.output_data.write(" " + str(cell.id) + "-" + str(neighbor.id))
			self.output_data.write("\n")

		### Fields
		### WARNING: Consider the large number of possible coordinates (dimX*dim)
		### 	     This might generate a large file size.
		### WARNING: Do not apply for cell-associated fields (Only chemical fields).
		for F in self.fields_to_extract:
			f = self.getConcentrationField(F)
			self.output_data.write("MCS" + str(mcs)+ "\tFIELD\t" + F + ":\t")
			for xdim in range(self.dim.x):
		    		for ydim in range(self.dim.y):
                                    if f[xdim, ydim, 0] != 0:
					self.output_data.write(" ")
					self.output_data.write(" " + str(xdim) + ',' + str(ydim) + ':' + str(f[xdim, ydim, 0]))
			self.output_data.write("\n")

		# End each step with this flag
		self.output_data.write("MCS" + str(mcs)+ "\tREPORT\n")
	def finish(self):
		self.output_data.close()