// -*- mode:C++; tab-width:4; c-basic-offset:4; indent-tabs-mode:nil -*-

#ifndef __EV_REAL_HPP__
#define __EV_REAL_HPP__

// PCL
#include <pcl/io/openni_grabber.h>
#include <pcl/point_types.h>
#include <pcl/kdtree/kdtree_flann.h>
//#include <pcl/surface/mls.h>  // too slow
#include <pcl/ModelCoefficients.h>
#include <pcl/filters/extract_indices.h>
#include <pcl/filters/filter.h>
#include <pcl/filters/voxel_grid.h>
#include <pcl/features/normal_3d.h>
#include <pcl/io/pcd_io.h>
//#include <pcl/io/ply_io.h>  // for file writer
#include <pcl/kdtree/kdtree.h>
#include <pcl/sample_consensus/method_types.h>
#include <pcl/sample_consensus/model_types.h>
#include <pcl/segmentation/sac_segmentation.h>
#include <pcl/segmentation/extract_clusters.h>
//#include <pcl/surface/gp3.h>  // better use poisson; this leaves holes
#include <pcl/surface/poisson.h>
//#include <pcl/surface/vtk_utils.h> // worked in pcl-1.6
#include <pcl/surface/vtk_smoothing/vtk_utils.h> // worked in pcl-1.7
#include <pcl/ros/conversions.h>
#include <pcl/features/normal_3d_omp.h>

#include "FunctionMinEvalOp.hpp"

#define DEFAULT_FILE_NAME "evReal_ecf_params.xml"

class EvReal {

    public:

        EvReal() : useMesh(false) {}

        bool setMeshName(const char* meshName);  //-- Overrides use of sensor if called before init.
        bool init();
        bool run();
        bool quit();

        void sensorCallback(const pcl::PointCloud<pcl::PointXYZ>::ConstPtr &cloud);
        //--Planner
        bool createConfPlan(const std::vector<dReal> activegoal);

    private:
        //-- Sensor
        bool initSensor();
        bool stopSensor();
        bool quitSensor();
        pcl::Grabber* interface;

        //-- OpenRAVE
        bool initOR();
        bool quitOR();
        RobotBasePtr probot;
        EnvironmentBasePtr penv;
        ControllerBasePtr pcontrol;
        KinBodyPtr storeMeshKinBodyPtr;


        //-- PCL
        bool useMesh;
        string meshName;

        //-- Timing
        struct timeval start, end;
        long mtime, seconds, useconds;

        //-- General
        string xgnitiveRoot;
};

#endif  // __EV_REAL_HPP__

