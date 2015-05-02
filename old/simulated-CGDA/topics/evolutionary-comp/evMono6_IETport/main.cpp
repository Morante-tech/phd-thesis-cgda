// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#include "EvMono.hpp"

int main(int argc, char **argv) {

    printf("evMono checking for yarp network... ");
    fflush(stdout);
    Network yarp;
    if (!yarp.checkNetwork()) {
        printf("[fail]\ncolorSegmentor found no yarp network (try running \"yarpserver &\"), bye!\n");
        return -1;
    } else printf("[ok]\n");

    EvMono mod;
    return mod.init();
}

