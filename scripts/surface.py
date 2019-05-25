"""
Class for generating a mesh for a Monge-patch surface i.e. a surface given by z=f(x, y) using pygmsh.
"""
import itertools

import numpy


class PointSet:
    """
    Provides a set of unique points with unique ids.
    pointid: Unique id of the point last added to the set.
    points: a Nx3 numpy.ndarray storing all point coordinates in the order they were added.
    """

    def __init__(self):
        self.pointid = 0
        self.points = None

    def addpoint(self, X):
        """
        Adds a point to the set if it is not a duplicate and returns id of the new point.
        If the point is a duplicate, it returns id of the existing point.

        X: 1x3 numpy.ndarray.
        """
        if self.points is None:
            self.points = numpy.asarray([X])
            self.pointid += 1
            return self.pointid
        else:
            distance = numpy.linalg.norm(self.points - X, axis=1)
            existingid = numpy.where(distance < 1e-8)[0]
            if len(existingid) is 0:
                self.points = numpy.vstack([self.points, X])
                self.pointid += 1
                return self.pointid
            else:
                return existingid[0] + 1


class SplineSet:
    """
    Stores point ids comprising a gmsh spline object. Also compares two
    splines to find if they have same orientation or opposite orientation.
    N: number of splines in the set.
    """

    def __init__(self):
        self.splineid = 0
        self.splines = []

    def addspline(self, pointids):
        """
        Checks if the spline is unique in points and orientation. If a
        duplicate spline is found it returns its id. If the duplicate spline
        has opposite orientation then it returns the negative of the existing
        spline id. Otherwise, adds the spline to the set and returns the
        unique id. We determine uniqueness by comparing end-points of the
        splines. So sequence is important and it is assumed that if the
        end-points are same or reversed, the inner points must be same or
        reversed as well.

        Parameters:
        -----------
        pointids: a sequence of pointids comprising the spline.
        """
        if len(self.splines) is 0:
            self.splines.append(pointids)
            self.splineid += 1
            return self.splineid
        else:
            for i, spline in enumerate(self.splines):
                if pointids[0] == spline[0] and pointids[-1] == spline[-1]:
                    """
                    Same orientation.
                    """
                    return i + 1
                elif pointids[0] == spline[-1] and pointids[-1] == spline[0]:
                    """
                    Opposite orientation.
                    """
                    return -(i + 1)

            self.splines.append(pointids)
            self.splineid += 1
            return self.splineid


class MongeSurface:
    """
    A surface will consist of sub-surfaces which have overlapping boundaries,
    each sub-surface will be made up of curve loops which are made up of 4
    splines each. Each spline will be made up of N points. All the points and
    the splines must be unique in the whole surface although shared between
    sub-surfaces.
    """

    def __init__(self, zfunc, N=5, lc=0.1):
        """
        zfunc: a callable that accepts a Nx2 array (the x and y coordinates)
        as input and returns a Nx1 array (the z coordinate).

        N: Number of points along each spline boundary of the sub-surfaces.
        """
        self.N = N
        self.lc = lc
        self.f = zfunc
        self.pointset = PointSet()
        self.splineset = SplineSet()
        self.curveloops = []
        self.subsurfaces = 0

    def _splinepoints(self, X1, X2):
        """
        Given end-points of a line-segment X1 and X2, creates N equally-spaced
        points including the end-points. X1 and X2 are in the x-y plane. But we
        will return points in 3D by calculating the z-coordinates as well.
        """
        points = numpy.empty((self.N, 3))
        points[:, 0] = numpy.linspace(X1[0], X2[0], self.N)
        points[:, 1] = numpy.linspace(X1[1], X2[1], self.N)
        points[:, 2] = self.f(points[:, :-1])
        return points

    def addpatch(self, vertices):
        """
        Given 4 corners of a topological rectangle in the x-y plane, creates
        points along edges, joins them by an interpolating spline and adds a
        curve-loop and a surface filling to the gmsh model.

        vertices: a list or tuple of 4 tuples like [(x0, y0), (x1, y1), (x2, y2), (x3, y3)].
        """
        startiter, dummy = itertools.tee(vertices)
        enditer = itertools.chain(dummy, [vertices[0]])
        next(enditer, None)

        splineids = [self.splineset.addspline(
            [self.pointset.addpoint(p) for p in self._splinepoints(start, end)])
            for start, end in zip(startiter, enditer)]

        self.curveloops.append(splineids)
        self.subsurfaces += 1

    def writecode(self, filename):
        """
        Write the gmsh code to a file based on the patches added to the surface.
        """
        with open(filename, 'w') as f:
            f.write(
                '//The global element size variable.\nlc = {};\n'.format(self.lc))
            f.write('\n//All the points.\n')
            for i, point in enumerate(self.pointset.points):
                f.write(
                    'Point ({0}) = {{{1}, {2}, {3}, lc}};\n'.format(i+1, *point))

            f.write('\n//All the splines.\n')
            for i, spline in enumerate(self.splineset.splines):
                pointstr = ', '.join([str(p) for p in spline])
                f.write('Spline ({0}) = {{{1}}};\n'.format(i+1, pointstr))

            f.write('\n//All the curve loops.\n')
            for i, curveloop in enumerate(self.curveloops):
                splinestr = ', '.join([str(s) for s in curveloop])
                f.write('Curve Loop ({0}) = {{{1}}};\n'.format(i+1, splinestr))
            
            f.write('\n//All the surface fillings.\n')
            for subsurface in range(self.subsurfaces):
                f.write('Surface ({0}) = {{{0}}};\n'.format(subsurface + 1))
            
            f.write('\n//Finally, mesh it as a surface.\n')
            f.write('Mesh 2;\n')
