cmake_minimum_required (VERSION 3.0)
project(katana_addons)

set(KATANA_HOME "$ENV{KATANA_HOME}" CACHE PATH "Path to Katana")

list(APPEND CMAKE_MODULE_PATH ${KATANA_HOME}/plugins/Src/cmake)

find_package(Katana PATHS "${KATANA_HOME}/plugin_apis/cmake" REQUIRED)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -Wall -Wextra -Wpedantic -std=c++14")

# Ensure we don't compile DSOs with undefined symbols.
if (CMAKE_SYSTEM_NAME MATCHES Linux)
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,--no-undefined")
    set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -Wl,--no-undefined")
endif ()

add_subdirectory(src)
add_subdirectory(python)
