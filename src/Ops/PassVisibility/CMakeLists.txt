add_library(PassVisibility MODULE
    src/PassVisibility.cpp)

set_target_properties(PassVisibility PROPERTIES
    PREFIX "")

target_include_directories(PassVisibility
    PRIVATE
    include)

target_link_libraries(PassVisibility
    PRIVATE
    Katana::FnAttribute
    Katana::FnConfig
    Katana::FnGeolibOpPlugin
    Katana::FnGeolibServices)

install(TARGETS PassVisibility DESTINATION Resources/Ops)
