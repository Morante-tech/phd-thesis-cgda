cmake_minimum_required (VERSION 2.6.0)

project (babbling)

FIND_PACKAGE(OpenRAVE REQUIRED)


if( CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_GNUCXX )
  add_definitions("-fno-strict-aliasing -Wall")
endif( CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_GNUCXX )

find_package(Boost COMPONENTS iostreams python thread system)

include_directories(${OpenRAVE_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR}})
if( Boost_INCLUDE_DIRS )
  include_directories(${Boost_INCLUDE_DIRS})
endif()

link_directories(${OpenRAVE_LIBRARY_DIRS} ${Boost_LIBRARY_DIRS})

add_executable(babbling main.cpp Babbling.cpp)
set_target_properties(babbling PROPERTIES COMPILE_FLAGS "${OpenRAVE_CXXFLAGS}")
set_target_properties(babbling PROPERTIES LINK_FLAGS "${OpenRAVE_LINK_FLAGS}")
target_link_libraries(babbling ${OpenRAVE_LIBRARIES} ${OpenRAVE_CORE_LIBRARIES} ${Boost_SYSTEM_LIBRARY} ${Boost_THREAD_LIBRARY} )
install(TARGETS babbling DESTINATION . )

