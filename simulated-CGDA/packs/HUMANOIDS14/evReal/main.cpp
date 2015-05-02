// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "EvReal.hpp"

int main(int argc, char **argv) {

    //-- The main class
    EvReal module;

    //-- Use the following line to override the sensor data with a mesh.
    module.setMeshName("mesh_05");  //-- objs/mesh_01.obj for higher resolution

    //-- Initialize OpenRAVE and sensor (if used).
    module.init();

    //--
    module.run();

    return 0;
}

