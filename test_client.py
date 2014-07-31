__author__ = 'weigl'

from path import path

from restflow.client import *


service = HiFlowRestClient("http://127.0.0.1:5000/")

# currently not needed
# service.upload_mesh(url="https://github.com/CognitionGuidedSurgery/msml/blob/master/examples/BunnyExample/Bunny6000Surface.vtk?raw=true")
# service.upload_mesh(filename="local/folder/bunny.vtk")

# request a token
simulation = service.open_simulation()

print "HF3 data:"
print simulation.hf3

print "BC data:"
print simulation.bc

bunny = path("share/bunny.vtk").abspath()
print "Mesh Update %s " % bunny

mesh_update = lambda filename: \
    {'Param': {
        'Mesh': {
            'Filename': filename, }}}


def bc_fix_constraints(points):
    if len(points) % 3 != 0:
        raise BaseException("points must be a multiple of 3")

    p = ""
    dis = ""

    for i, c in enumerate(points):
        p += str(c)
        dis += str(0.0)

        if (i+1) != len(points):
            if (i+1) % 3 == 0 and i != 0:
                p += ";  "
                dis += ";  "
            else:
                p += ", "
                dis += ", "



    return {
        'Param': {
            'FixedConstraintsBCs': {
                'NumberOfFixedDirichletPoints': len(points)/3,
                'fDPoints': p,
                'fDisplacements': dis,
            }}}


print "Update: ", mesh_update(bunny)
simulation.hf3 = mesh_update(bunny)

fixConstraint = bc_fix_constraints([1.0, 2.0, 3.0]*5)

print "Update: ", fixConstraint
simulation.bc = fixConstraint


from pprint import pprint

pprint(simulation.hf3)
pprint(simulation.bc)

result = simulation(5, 0.5)