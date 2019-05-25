import os
import unittest

from surface import MongeSurface, PointSet, SplineSet


class TestSurfaceMethods(unittest.TestCase):

    def test_addpoint(self):
        pointset = PointSet()
        self.assertEqual(pointset.addpoint([1.0, 2.0, 3.0]), 1)
        self.assertEqual(pointset.addpoint([2.0, 4.0, 6.0]), 2)
        self.assertEqual(pointset.addpoint(
            [0.999999999999, 1.9999999999999, 3.0]), 1)

    def test_addspline(self):
        splineset = SplineSet()
        self.assertEqual(splineset.addspline([1, 2, 3, 4]), 1)
        self.assertEqual(splineset.addspline([2, 2, 3, 5]), 2)
        self.assertEqual(splineset.addspline([1, 4, 6, 4]), 1)
        self.assertEqual(splineset.addspline([4, 4, 6, 1]), -1)

    def test_addpatch(self):
        def f(X):
            return 0.0
        surface = MongeSurface(f, 2)

        surface.addpatch([(0, 0), (0, 1), (1, 1), (1, 0)])
        self.assertEqual(surface.pointset.pointid, 4)
        self.assertEqual(surface.splineset.splineid, 4)
        self.assertEqual(surface.splineset.splines[0], [1, 2])
        self.assertEqual(surface.splineset.splines[1], [2, 3])
        self.assertEqual(surface.splineset.splines[2], [3, 4])
        self.assertEqual(surface.splineset.splines[3], [4, 1])
        self.assertEqual(surface.curveloops[0], [1, 2, 3, 4])

        surface.addpatch([(2, 0), (1, 0), (1, 1), (2, 1)])
        self.assertEqual(surface.pointset.pointid, 6)
        self.assertEqual(surface.splineset.splineid, 7)
        self.assertEqual(surface.splineset.splines[4], [5, 4])
        self.assertEqual(surface.splineset.splines[5], [3, 6])
        self.assertEqual(surface.splineset.splines[6], [6, 5])
        self.assertEqual(surface.curveloops[1], [5, -3, 6, 7])

        self.assertEqual(surface.subsurfaces, 2)

    def test_writecode(self):
        def f(X):
            return 0.0
        surface = MongeSurface(f, 2)
        surface.addpatch([(0, 0), (0, 1), (1, 1), (1, 0)])
        surface.addpatch([(2, 0), (1, 0), (1, 1), (2, 1)])
        matchcode = (
            '//The global element size variable.\n'
            'lc = 0.1;\n'
            '\n//All the points.\n'
            'Point (1) = {0.0, 0.0, 0.0, lc};\n'
            'Point (2) = {0.0, 1.0, 0.0, lc};\n'
            'Point (3) = {1.0, 1.0, 0.0, lc};\n'
            'Point (4) = {1.0, 0.0, 0.0, lc};\n'
            'Point (5) = {2.0, 0.0, 0.0, lc};\n'
            'Point (6) = {2.0, 1.0, 0.0, lc};\n'
            '\n//All the splines.\n'
            'Spline (1) = {1, 2};\n'
            'Spline (2) = {2, 3};\n'
            'Spline (3) = {3, 4};\n'
            'Spline (4) = {4, 1};\n'
            'Spline (5) = {5, 4};\n'
            'Spline (6) = {3, 6};\n'
            'Spline (7) = {6, 5};\n'
            '\n//All the curve loops.\n'
            'Curve Loop (1) = {1, 2, 3, 4};\n'
            'Curve Loop (2) = {5, -3, 6, 7};\n'
            '\n//All the surface fillings.\n'
            'Surface (1) = {1};\n'
            'Surface (2) = {2};\n'
            '\n//Finally, mesh it as a surface.\n'
            'Mesh 2;\n'
        )
        surface.writecode('checkcode.geo')
        with open('checkcode.geo', 'r') as codefile:
            writtencode = codefile.read()
            self.assertEqual(writtencode, matchcode)
        os.remove('checkcode.geo')


if __name__ == "__main__":
    unittest.main()
