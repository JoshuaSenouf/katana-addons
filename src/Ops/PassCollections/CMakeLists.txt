add_library(PassCollections MODULE
    src/PassCollections.cpp)

set_target_properties(PassCollections PROPERTIES
    PREFIX "")

target_include_directories(PassCollections
    PRIVATE
    include)

target_link_libraries(PassCollections
    PRIVATE
    Katana::FnAttribute
    Katana::FnConfig
    Katana::FnGeolibOpPlugin
    Katana::FnGeolibServices
    Katana::pystring)

install(TARGETS PassCollections DESTINATION Resources/Ops)
