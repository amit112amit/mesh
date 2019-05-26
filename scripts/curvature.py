"""
Calculate mean and Gaussian curvatures of a surface given by z=f(x, y)
"""
import sympy


def getcurvatureexpr(expr, symmap=None):
    """
    Given an expression f(x, y), calculate symbolic expressions for Gaussian
    and mean curvatures i.e. K and H respectively.
    """
    locals().update(symmap)
    x, y = sympy.symbols('x, y')
    z = eval(expr)

    p = sympy.Matrix([x, y, z])
    px = p.diff(x)
    py = p.diff(y)
    n = px.cross(py)/px.cross(py).norm()

    E = px.dot(px)
    F = px.dot(py)
    G = py.dot(py)

    L = px.diff(x).dot(n)
    M = px.diff(y).dot(n)
    N = py.diff(y).dot(n)

    denominator = E*G - F**2
    K = (L*N - M**2)/denominator
    H = (L*G - 2*M*F + N*E)/2/denominator

    return K, H


def makefunction(exprs, assignto, funcname='func', returncodestr=False, usenumba=True):
    """
    Given sympy expressions list `expr` and a list of variable names
    `assignto`, it creates a function. It returns a function object if
    `returncodestr` = False. Otherwise, it returns a formatted function code
    as a string with the name of the function given by `funcname`. If
    `usenumba` is False it will not produce a Numba Jitted function.
    """
    codestr = [
        'import math',
        'from math import sqrt',       # Bug in Sympy, need to handle sqrt separately
    ]
    if usenumba:
        codestr += [
            'import numba',
            '\n@numba.njit'
        ]
    else:
        codestr.append('')             # Just to introduce a line break

    codestr += [
        'def {0}(x, y):'.format(funcname),
        '\n    ############## Sub-expressions ##############'
    ]

    # Now the codegeneration part, first eliminate common sub-expressions
    replacements, reduced_exprs = sympy.cse(exprs, optimizations='basic')
    for lhs, rhs in replacements:
        codestr.append('    {} = {}'.format(lhs, sympy.pycode(rhs)))

    codestr.append('\n    ############## Final Expressions ##############')
    for lhs, rhs in zip(assignto, reduced_exprs):
        codestr.append('    {} = {}'.format(lhs, sympy.pycode(rhs)))

    codestr.append('\n    return {}'.format(', '.join(assignto)))
    funccode = '\n'.join(codestr)

    if returncodestr:
        return funccode
    else:
        exec(funccode, globals())
        return globals()[funcname]
