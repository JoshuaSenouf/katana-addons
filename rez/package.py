name = "katana_addons"

version = "1.0.0"

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
    "katana-3.0+",
    "python-2.7+<3"
]

variants = [
    ["platform-linux"]
]

build_system = "cmake"

with scope("config") as config:
    config.build_thread_count = "logical_cores"

uuid = "katana_addons-{version}".format(version=str(version))

def commands():
    env.KATANA_RESOURCES.append("{root}/Resources")
