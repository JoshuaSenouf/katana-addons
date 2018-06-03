PrmanInstanceArray
======

This SuperTool makes use of a RfK specific data type, the instance array.

Inside of Katana, it is one of the three ways to express instancing for RenderMan, through a single SceneGraph location. Because of that, it fits very well into scenarios where you might need to instanciate dozens, hundreds of thousands of objects, if not millions at once, as it will not require to bloat your SceneGraph with a per-instance unique location like with hierarchical instancing for example.

This comes at the price, quite fair in my opinion, of being unable to do per-instance variation, may it be geometry or shading variation, as an instance array only operates at the instance source level, and no deeper. Not to say all is impossible with some cleverness, though.

The instance array is what is backing up Pixar USD's PointInstancer inside Katana, and one of the objective of this SuperTool is to allow users to have as most of the benefits of this USD schema as possible, without actually depending on USD, and will thus map quite closely [its specifications](https://github.com/PixarAnimationStudios/USD/wiki/PointInstancer-Object-Model).

Screenshots
------

* Options of the node

![](https://image.ibb.co/hV88sd/Prman_Instance_Array_Options.png)

Features
------

* General:
    * Loading as many (animated) Alembic geometry files as necessary to use as instance sources
    * Load an Alembic pointcloud to use to scatter the instance sources
    * Being able to compute the instance array either immediately or during op resolve, in order to bring the expansion time as close to zero as possible

* Scatter:
    * Density control
    * **TODO:** Per-instance animation offset

* Primvars (The default names comes from Maya/USD naming conventions):
    * Ability to override the default name of each supported primvars
    * Supported:
        * Position ("P")
        * Rotation ("rotationPP")
        * Scale ("scalePP")
        * Prototype Indices/Indexes ("objectId")
        * **NOT USED YET:** IDs ("particleId")
        * **NOT USED YET:** Velocity ("velocity")
        * **NOT USED YET:** Angular Velocity ("angularVelocity")

* Motion Blur:
    * Computed and applied depending on each point in the Alembic pointcloud
    * Methods:
        * **TODO:** Velocity-based
        * **TODO:** Transform-based
    * Velocity multiplier

How to use
------

In order to work with this tool, the geometry format must be Alembic (.abc).

The user will need at least one Alembic file to instanciate, as well as an Alembic pointcloud that will represent the scatter.

This pointcloud will need to contain at least a position attribute (which should be located in most cases under "geometry.point.P" in Katana anyway), as well as a indices/indexes primvar that will allow to map each instance with its corresponding instance source.
