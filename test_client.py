__author__ = 'weigl'

from path import path

from restflow.client import *
from restflow.hf3lint import read_xml
from restflow.base import update_meshfile
from path import path

assets_dir = path("share/unitcube")
unitcube_vtu = (assets_dir/"unitcube.vtu").abspath()


##
# Create a new client instance.
# A client instance allows upload of files and opening new simulation session.
service = HiFlowRestClient("http://127.0.0.1:5000")

# currently not needed
# service.upload_mesh(url="https://github.com/CognitionGuidedSurgery/msml/blob/master/examples/BunnyExample/Bunny6000Surface.vtk?raw=true")
# service.upload_mesh(filename="local/folder/bunny.vtk")

##
# Request a simulation, this allocates some server data structures (bc, hf3)
session = service.open_simulation()
session._persistent = True # do not request delete at destructor call

##
# You can get and set these via .hf3 and .bc properties
print "HF3 data:"
print session.hf3

print "BC data:"
print session.bc


##
# We set our examples configs:
session.hf3 = read_xml(assets_dir/"hf3_000.xml")
session.update_hf3(update_meshfile(unitcube_vtu))
session.bc =  read_xml(assets_dir/"bc_000.xml")

result = session.run()

session.get_result(25, target="test.vtu")
session.get_result(25, "vtp", target="test.vtp")
session.get_result(25, "vtk", target="test.vtk")
session.get_result(25, "stl", target="test.stl")