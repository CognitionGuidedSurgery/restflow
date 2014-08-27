#
# Copyright (C) 2013-2014 Alexander Weigl, Nicolai Schoch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/>.

"""Local test case with unitcube

"""

__author__ = "Alexander Weigl uiduw@student.kit.edu>"
__date__ = "2014-08-27"
__version__ = "0.1"


from restflow import hf3lint, hf3binding, hf3configs
from path import path


assets_dir = path("share/unitcube")


##
# Create a session in working
session = hf3binding.Hiflow3Session(path("tmp/"))

##
# Read in HF3 and BCdata configs from share/unitcube
session.hf3 = hf3lint.read_xml(assets_dir/"hf3_000.xml")
session.bc =  hf3lint.read_xml(assets_dir/"bc_000.xml")

##
# Fix the path to the unitcube.vtu
# This is relative to asset_dir, but the working dir has changed
mesh = (assets_dir/"unitcube.vtu").abspath()
update = hf3binding.update_meshfile(mesh)

# An update is a dictionary with new values
print update

# Apply on the session
session.update_hf3(update)

# Everything should be alright
# We start elasticity

print session.run()
# New constraints for the next run
session.bc =  hf3lint.read_xml(assets_dir/"bc_001.xml")

# start again, the mesh from step 25 should be taken
print session.run()


# renaming files for paraview
import restflow.utils
files = sorted(session.get_result_files())
output = session.working_dir / "output"
output.makedirs_p()

for i, f in enumerate(files):
    restflow.utils.write_vtu(
        restflow.utils.read_ugrid(f),
        output/"mesh_%04d.vtu" % i)


