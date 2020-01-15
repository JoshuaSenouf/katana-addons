cmake_minimum_required (VERSION 3.2)
project(katana-ops)

set(KATANA_HOME "$ENV{KATANA_HOME}" CACHE PATH "Path to Katana")

set(CMAKE_INSTALL_PREFIX "$ENV{HOME}/workspace/katana/katana-ops" CACHE PATH "Installation directory of katana-ops" FORCE)
set(CMAKE_CXX_STANDARD 11)

find_package(Katana PATHS "${KATANA_HOME}/plugin_apis/cmake" REQUIRED)

# Ensure we don't compile DSOs with undefined symbols.
if (CMAKE_SYSTEM_NAME MATCHES Linux)
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,--no-undefined")
    set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -Wl,--no-undefined")
endif ()

#-------------------------------------------------------------------------------

add_subdirectory(src/Ops/ComputeInstanceArray)
add_subdirectory(src/SuperTools)
