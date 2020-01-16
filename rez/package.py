name = "katana_ops"

version = "0.0.1"

authors = [
    "Joshua Senouf"
]

description = \
    """
    Collection of tools, nodes and Ops for Foundry's Katana.
    """

requires = [
    "cmake-3+",
    "gcc-6+",
    "ilmbase-2.2.1<2.4",
    "katana-3.0+",
    "python-2.7+<3"
]

variants = [
    ["platform-linux"]
]

build_system = "cmake"

with scope("config") as config:
    config.build_thread_count = "logical_cores"

uuid = "katana_ops-{version}".format(version=str(version))

def commands():
    # env.PATH.prepend("{root}/bin")
    # env.LD_LIBRARY_PATH.prepend("{root}/lib")
    # env.PYTHONPATH.prepend("{root}/lib/python" + str(env.REZ_PYTHON_MAJOR_VERSION) + "." + str(env.REZ_PYTHON_MINOR_VERSION) + "/site-packages")
    # env.CMAKE_MODULE_PATH.prepend("{root}/lib/cmake/Alembic")
    env.KATANA_RESOURCES.append("{root}/Resources")

    # Helper environment variables.
    # env.KATANA_OPS_BINARY_PATH.set("{root}/bin")
    # env.KATANA_OPS_INCLUDE_PATH.set("{root}/include")
    # env.KATANA_OPS_LIBRARY_PATH.set("{root}/lib")
