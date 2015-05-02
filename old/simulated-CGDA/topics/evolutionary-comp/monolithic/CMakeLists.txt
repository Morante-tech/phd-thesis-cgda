cmake_minimum_required (VERSION 2.6.0)

project (cppexamples)

#set(CMAKE_BUILD_TYPE Debug)#RelWithDebInfo)
FIND_PACKAGE(OpenRAVE REQUIRED)
FIND_PACKAGE(YARP REQUIRED)
find_package(OpenCV REQUIRED)
find_package(ASIBOT REQUIRED)
find_package(TRAVIS REQUIRED)

if( CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_GNUCXX )
  add_definitions("-fno-strict-aliasing -Wall")
endif( CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_GNUCXX )

find_package(Boost COMPONENTS iostreams python thread)

include_directories(${OpenRAVE_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR} ${TRAVIS_INCLUDE_DIRS} ${ASIBOT_INCLUDE_DIRS})
if( Boost_INCLUDE_DIRS )
  include_directories(${Boost_INCLUDE_DIRS})
endif()

link_directories(${OpenRAVE_LIBRARY_DIRS} ${Boost_LIBRARY_DIRS} ${TRAVIS_LINK_DIRS} ${ASIBOT_LINK_DIRS})

add_executable(monolithic monolithic.cpp)
set_target_properties(monolithic PROPERTIES COMPILE_FLAGS "${OpenRAVE_CXXFLAGS}")
set_target_properties(monolithic PROPERTIES LINK_FLAGS "${OpenRAVE_LINK_FLAGS}")
target_link_libraries(monolithic ${OpenRAVE_LIBRARIES} ${OpenRAVE_CORE_LIBRARIES} ${Boost_THREAD_LIBRARY} ${YARP_LIBRARIES} ${OpenCV_LIBS} ${TRAVIS_LIBRARIES} ${ASIBOT_LIBRARIES})
install(TARGETS monolithic DESTINATION . )

