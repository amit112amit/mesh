import numpy
from surface import MongeSurface
from itertools import tee


def f(X):
    """
    Equation of the surface z = f(x, y).
    """
    return 0.555*numpy.sin(numpy.pi*X[:, 0])*numpy.cos(numpy.pi*X[:, 1])


# -------------------------------------------------------------------------------
# Create B-Rep of the surface using surface patches
# -------------------------------------------------------------------------------
L = [-1, 1]
W = [-1, 1]
N = 21

patches = []
Y = numpy.linspace(L[0], L[1], N)

Yl, Yh = tee(Y)
next(Yh, None)

for yl, yh in zip(Yl, Yh):
    patches.append([(W[1], yl), (W[0], yl), (W[0], yh), (W[1], yh)])


surf = MongeSurface(f, N=10, lc=0.02)

for patch in patches:
    surf.addpatch(patch)

surf.writecode('mongesurface.geo')
