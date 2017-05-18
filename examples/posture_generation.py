#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2017 Stephane Caron <stephane.caron@normalesup.org>
#
# This file is part of pymanoid <https://github.com/stephane-caron/pymanoid>.
#
# pymanoid is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pymanoid is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# pymanoid. If not, see <http://www.gnu.org/licenses/>.

import IPython
import numpy
import os
import sys

try:
    import pymanoid
except ImportError:
    script_path = os.path.realpath(__file__)
    sys.path.append(os.path.dirname(script_path) + '/../')
    import pymanoid

from pymanoid import Stance
from pymanoid.robots import JVRC1


if __name__ == '__main__':
    sim = pymanoid.Simulation(dt=0.03)
    robot = JVRC1('JVRC-1.dae', download_if_needed=True)
    sim.set_viewer()
    sim.viewer.SetCamera([
        [-0.28985317,  0.40434422, -0.86746233,  2.73872042],
        [0.95680251,  0.10095043, -0.2726499,  0.86080128],
        [-0.02267371, -0.90901857, -0.41613837,  2.06654644],
        [0.,  0.,  0.,  1.]])

    robot.set_z(0.8)  # hack to start with the robot above contacts
    lf_target = robot.left_foot.get_contact(pos=[0, 0.3, 0], visible=True)
    rf_target = robot.right_foot.get_contact(pos=[0, -0.3, 0], visible=True)
    com = robot.get_com()

    stance = Stance(com=com, left_foot=lf_target, right_foot=rf_target)
    stance.dof_tasks[robot.R_SHOULDER_R] = -0.5
    stance.dof_tasks[robot.L_SHOULDER_R] = +0.5
    stance.bind(robot)

    # First, generate the initial posture corresponding to the stance
    robot.ik.solve(max_it=100, impr_stop=1e-4)

    # Now, we move the COM back and forth for 10 seconds
    sim.schedule(robot.ik)
    init_com = robot.com.copy()
    for t in numpy.arange(0., 10., sim.dt):
        com_var = numpy.sin(t) * numpy.array([.2, 0, 0])
        com.set_pos(init_com + numpy.array([-0.2, 0., 0.]) + com_var)
        sim.step()

    # Finally, we start the simulation
    sim.start()

    # Don't forget to give the user a prompt
    if IPython.get_ipython() is None:
        IPython.embed()