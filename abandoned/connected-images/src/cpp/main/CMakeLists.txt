project(main)
cmake_minimum_required(VERSION 2.8)
aux_source_directory(. SRC_LIST)
add_executable(${PROJECT_NAME} ${SRC_LIST})

# Find OpenCV.
find_package(OpenCV REQUIRED)
find_package(YARP REQUIRED)

# Set up our main executable.
target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS} ${YARP_LIBRARIES})
