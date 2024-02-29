******************************************************************************
Mesh Supported by a Simple Arch
******************************************************************************

.. figure:: /_images/example_mesh_constrained_on-arch.png

Summary
=======

In this example,
we construct a mesh from a meshgrid,
fix the corner vertices,
and constrain the middle vertices to a simple nurbs arch.

The contrained vertices slide along the arch
under influence of the tangential component of their residual forces,
until an equilibrium configuration is contained.

In the equilibrium configuration,
the tangential compnents at the contrained vertices have vanished,
leaving only the components normal to the constraint curve.

Code
====

.. literalinclude:: example_mesh_constrained_on-arch.py
    :language: python
