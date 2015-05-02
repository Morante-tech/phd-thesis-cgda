cmake_minimum_required (VERSION 2.6.0)

project (evReal)

FIND_PACKAGE(OpenRAVE REQUIRED)
find_package(PCL 1.2 REQUIRED)

if( CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_GNUCXX )
  add_definitions("-fno-strict-aliasing -Wall")
endif( CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_GNUCXX )

find_package(Boost COMPONENTS iostreams python thread system)

include_directories(${OpenRAVE_INCLUDE_DIRS} ${PCL_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR}})
if( Boost_INCLUDE_DIRS )
  include_directories(${Boost_INCLUDE_DIRS})
endif()

link_directories(${OpenRAVE_LIBRARY_DIRS} ${Boost_LIBRARY_DIRS} ${PCL_LIBRARY_DIRS} )
add_definitions(${PCL_DEFINITIONS})

add_executable(evReal main.cpp EvReal.cpp FunctionMinEvalOp.cpp)
set_target_properties(evReal PROPERTIES COMPILE_FLAGS "${OpenRAVE_CXXFLAGS}")
set_target_properties(evReal PROPERTIES LINK_FLAGS "${OpenRAVE_LINK_FLAGS}")
target_link_libraries(evReal ${OpenRAVE_LIBRARIES} ${OpenRAVE_CORE_LIBRARIES} ${Boost_SYSTEM_LIBRARY} ${Boost_THREAD_LIBRARY} ${PCL_LIBRARIES} ecf )
#target_link_libraries(evReal ${OpenRAVE_LIBRARIES} ${OpenRAVE_CORE_LIBRARIES} ${Boost_SYSTEM_LIBRARY} ${Boost_THREAD_LIBRARY} ecf mpichcxx )  # dep on install
install(TARGETS evReal DESTINATION . )

