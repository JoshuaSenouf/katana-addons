add_library(ComputeInstanceArray MODULE src/ComputeInstanceArrayOp.cpp)

target_link_libraries(ComputeInstanceArray
    PRIVATE
    Katana::FnAttribute
    Katana::FnGeolibOpPlugin
    Katana::FnGeolibServices
)

install(FILES RegisterComputeInstanceArrayNode.py DESTINATION Plugins)
install(TARGETS ComputeInstanceArray DESTINATION Ops)
