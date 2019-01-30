
import sys
from os import environ
from os import getcwd
import string

sys.path.append(environ["PYTHON_MODULE_PATH"])


import CompuCellSetup


sim,simthread = CompuCellSetup.getCoreSimulationObjects()
            
# add extra attributes here
            
CompuCellSetup.initializeSimulationObjects(sim,simthread)
# Definitions of additional Python-managed fields go here
        
#Add Python steppables here
steppableRegistry=CompuCellSetup.getSteppableRegistry()
        

from mxan_indirect_csgSteppables import ConstraintInitializerSteppable
ConstraintInitializerSteppableInstance=ConstraintInitializerSteppable(sim,_frequency=1)
steppableRegistry.registerSteppable(ConstraintInitializerSteppableInstance)
        

from mxan_indirect_csgSteppables import ManageNutrientsSteppable
ManageNutrientsSteppableInstance=ManageNutrientsSteppable(sim,_frequency=50)
steppableRegistry.registerSteppable(ManageNutrientsSteppableInstance)

from mxan_indirect_csgSteppables import ManageAsignalSteppable
ManageAsignalSteppableInstance=ManageAsignalSteppable(sim,_frequency=50)
steppableRegistry.registerSteppable(ManageAsignalSteppableInstance)

from mxan_indirect_csgSteppables import ManageCsignalSteppable
ManageCsignalSteppableInstance=ManageCsignalSteppable(sim,_frequency=50)
steppableRegistry.registerSteppable(ManageCsignalSteppableInstance)

from mxan_indirect_csgSteppables import HandleOutputDataSteppable
HandleOutputDataSteppableInstance=HandleOutputDataSteppable(sim,_frequency=50)
steppableRegistry.registerSteppable(HandleOutputDataSteppableInstance)

from mxan_indirect_csgSteppables import InternalNetworkSteppable
InternalNetworkSteppableInstance=InternalNetworkSteppable(sim,_frequency=50)
steppableRegistry.registerSteppable(InternalNetworkSteppableInstance)

from mxan_indirect_csgSteppables import DeathSteppable
DeathSteppableInstance=DeathSteppable(sim,_frequency=50)
steppableRegistry.registerSteppable(DeathSteppableInstance)


from mxan_indirect_csgSteppables import StateFieldSteppable
StateFieldSteppableInstance=StateFieldSteppable(sim,_frequency=50)
steppableRegistry.registerSteppable(StateFieldSteppableInstance)

from mxan_indirect_csgSteppables import AsgAFieldSteppable
AsgAFieldSteppableInstance=AsgAFieldSteppable(sim,_frequency=50)
steppableRegistry.registerSteppable(AsgAFieldSteppableInstance)

from mxan_indirect_csgSteppables import CsgAFieldSteppable
CsgAFieldSteppableInstance=CsgAFieldSteppable(sim,_frequency=50)
steppableRegistry.registerSteppable(CsgAFieldSteppableInstance)

from mxan_indirect_csgSteppables import FateFieldSteppable
FateFieldSteppableInstance=FateFieldSteppable(sim,_frequency=50)
steppableRegistry.registerSteppable(FateFieldSteppableInstance)

CompuCellSetup.mainLoop(sim,simthread,steppableRegistry)
        
        