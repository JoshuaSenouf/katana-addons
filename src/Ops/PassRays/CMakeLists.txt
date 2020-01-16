add_library(PassRays MODULE
    src/PassRays.cpp)

set_target_properties(PassRays PROPERTIES
    PREFIX "")

target_include_directories(PassRays
    PRIVATE
    include)

target_link_libraries(PassRays
    PRIVATE
    Katana::FnAttribute
    Katana::FnConfig
    Katana::FnGeolibOpPlugin
    Katana::FnGeolibServices)

install(TARGETS PassRays DESTINATION Resources/Ops)
