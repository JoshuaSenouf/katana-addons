katana-addons
===

Collection of tools, nodes and Ops for Foundry's Katana.

What it contains
---

* Nodes:
    * PassDefine
    * PassResolve
* Ops:
    * PassVisibility
    * PassRays
    * PassCollections

How to use
---

These tools were written and compiled for Linux, with VSCode as the IDE, CMake as the building tool, a C++11 compiler in mind, and the latest version of Foundry's Katana available.

Download the source, build the project structure using CMake 3.x, open the project using your favorite IDE (tested on VSCode), build the project, execute a "make install" and everything will be installed under the default location of your system, so probably "/opt/...".
This can be changed by providing a custom path using the "CMAKE_INSTALL_PREFIX" variable.

Dependencies
---

* CMake 3+
* Katana 3+

Dependencies (As rez packages, for a rez build)
---

* CMake 3+
* GCC 6+
* Python 2.7+
* Katana 3+
