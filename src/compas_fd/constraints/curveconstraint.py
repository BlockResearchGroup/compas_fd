from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


from compas.geometry import Point
from compas.geometry import Vector
from compas_nurbs import Curve
from .constraint import Constraint

from numpy import dot


class CurveConstraint(Constraint):

    def __init__(self, curve, index, **kwargs):
        self._param = 0.5
        super(CurveConstraint, self).__init__(geometry=curve, index=index, **kwargs)
        if getattr(self, '_location', None) is None:
            self._location = self.geometry.points_at([self._param])[0]
            self.project_to_geometry()

    @property
    def curvature(self):
        # TODO update for proper quadratic approximation
        # curvature = self._curvature.unitized()
        # return projectino of (self.residual ** 2) ** 0.5 to curvature vector
        pass

    def compute_tangent(self):
        tangent = self._curve_tangent.unitized()
        self._tangent = tangent * dot(self.residual, tangent)

    def compute_normal(self):
        self._normal = self.residual - self.tangent

    def project_to_geometry(self):
        self._param, self._location, self._curve_tangent = (
            self.geometry.closest_point(self._location, self._param))

    def update_location(self):
        # self._location += (self.tangent + self.curvature) * Constraint.damping_factor
        self._location += self.tangent * Constraint.damping_factor
        self.project_to_geometry()


# replace with bound method in Curve class
def closest_point(curve, point, param=0.5, tol=1E-3, is_bounded=False, kmax=10):
    """Find the closest point on a curve using the Newton-Rhapson method.

        Parameters
        ----------
        point: :class:`Point`
            The sample point.
        param: float
            The initial guess for the curve parameter.
            (default is 0.5)
        tol: float
            The tolerance for convergence of the first
            derivative of the distance function.
            (default is 1E-3)
        is_bounded: bool
            Whether the closest point should lie within
            the [0, 1] parameter domain of the curve.
        kmax: int
            Maximum number of Newton-Rhapson iterations.
            (default is 10)

        Returns
        -------
        float
            The parameter at the closest point on the curve.
        :class:`Point`
            The closest point on the curve.
        :class:`Vector`
            The first derivative at the closest point on the curve.
        :class:`Vector`
            The second derivative at the closest point on the curve.
    """
    p = point
    t = param

    for _ in range(kmax):
        f, df, ddf = curve.derivatives_at([t], 2)[0]
        sx, sy, sz = (p[0] - f[0]), (p[1] - f[1]), (p[2] - f[2])

        dt = (sx * df[0] + sy * df[1] + sz * df[2])
        if abs(dt) < tol:
            break

        ddt = (sx * ddf[0] - df[0] ** 2 +
               sy * ddf[1] - df[1] ** 2 +
               sz * ddf[2] - df[2] ** 2)

        t = t - dt / ddt
        if is_bounded:
            t = max(min(t, 1), 0)

    return t, Point(*f), Vector(*df)


Curve.closest_point = closest_point
