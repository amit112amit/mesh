# Created by the script cgal_create_CMakeLists This is the CMake script for
# compiling a set of CGAL applications.

project(cgalmesh)

cmake_minimum_required(VERSION 3.5)

# CGAL and its components
find_package(CGAL REQUIRED)

include(${CGAL_USE_FILE})

# Boost and its components
find_package(Boost REQUIRED)

add_executable(cgalmesh cgalmesh.cxx)

message("Found CGAL_LIBRARIES ${CGAL_LIBRARIES}")
message("Found CGAL_3RD_PARTY_LIBRARIES ${CGAL_3RD_PARTY_LIBRARIES}")

# Link the executable to CGAL and third-party libraries
target_link_libraries(cgalmesh ${CGAL_LIBRARIES} ${CGAL_3RD_PARTY_LIBRARIES})
