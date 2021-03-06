#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""These test-cases are based on the examples from ASAM MCD-2MC Version 1.6 specification.
"""

import pytest

from pya2l import functions
from pya2l import exceptions
from pya2l.a2l_listener import ParserWrapper, A2LListener
from pya2l import model

try:
    import numpy as np
except ImportError:
    has_numpy = False
else:
    has_numpy = True

try:
    from scipy.interpolate import RegularGridInterpolator
except ImportError:
    has_scipy = False
else:
    has_scipy = True


RUN_MATH_TEST = has_numpy == True and has_scipy == True


class Value:
    """Value dummy class.
    """

Xs = [0.0, 200.0, 400.0, 1000.0, 5700.0]
Ys = [2.0,  2.7, 3.0,  4.2, 4.9]
Xins = [-1.0, 0.0, 850.0, 5700.0, 8000.0]
Rs = [2.0, 2.0, 3.9000000000000004, 4.9, 4.9]

@pytest.mark.skipif("RUN_MATH_TEST == False")
@pytest.mark.parametrize("x, expected", zip(Xins, Rs))
def test_interpolate1D_saturate(x, expected):
    interp = functions.Interpolate1D(xs = Xs, ys = Ys, saturate = True)
    assert interp(x) == expected


XsOutOfBounds = [-1.0, 8000.0]
expected = [None, None]

@pytest.mark.skipif("RUN_MATH_TEST == False")
@pytest.mark.parametrize("x, expected", zip(XsOutOfBounds, expected))
def test_interpolate1D_out_of_bounds(x, expected):
    interp = functions.Interpolate1D(xs = Xs, ys = Ys, saturate = False)
    with pytest.raises(ValueError):
        interp(x) == expected


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_axis_rescale_ok():
    EXPECTED = [
        0, 16.666666666666668, 33.333333333333336, 50.0, 66.66666666666667, 83.33333333333333, 100.0, 158.9206349206349, 216
    ]
    assert functions.axis_rescale(no_rescale_x = 3, no_axis_pts = 9,
        axis = (0x00, 0x64, 0xD8), virtual = (0x00, 0xC0, 0xFF)
        ) == EXPECTED

X_NORM = (
    (0.0,       2.0),
    (200.0,     2.7),
    (400.0,     3.0),
    (1000.0,    4.2),
    (5700,      4.9),
)

X_IDENT = (
    (0.0,       0.0),
    (1.0,       1.0),
    (2.0,       2.0),
    (3.0,       3.0),
    (4.0,       4.0),
    (5.0,       5.0),
    (6.0,       6.0),
)

Y_NORM = (
    (0.0,       0.5),
    (50.0,      1.0),
    (70.0,      2.4),
    (100.0,     4.2),
)

Y_IDENT = (
    (0.0,       0.0),
    (1.0,       1.0),
    (2.0,       2.0),
    (3.0,       3.0),
    (4.0,       4.0),
    (5.0,       5.0),
)

Z_MAP = (
    (3.4, 4.5, 2.1, 5.4, 1.2, 3.4, 4.4),
    (2.3, 1.2, 1.2, 5.6, 3.2, 2.1, 7.8),
    (3.2, 1.5, 3.2, 2.2, 1.6, 1.7, 1.7),
    (2.1, 0.4, 1.0, 1.5, 1.8, 3.2, 1.5),
    (1.1, 4.3, 2.1, 4.6, 1.2, 1.4, 3.2),
    (1.2, 5.3, 3.2, 3.5, 2.1, 1.4, 4.2),
)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_normalization_axes():
    na = functions.NormalizationAxes(X_NORM, Y_NORM, Z_MAP)
    assert na(850, 60) == 2.194

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_normalization_ident():
    na = functions.NormalizationAxes(X_IDENT, Y_IDENT, Z_MAP)
    for row_idx, row in enumerate(Z_MAP):
        for col_idx, value in enumerate(row):
            assert value == na(col_idx, row_idx)    # Interpolator should just pick every element from Z_MAP.

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_identity():
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 1
    coeffs.c = 0
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 1
    rf = functions.RatFunc(coeffs)
    assert rf(21845) == 21845

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_linear():
    xs = np.arange(-10, 11)
    ys = np.array(
        [-6.4, -5.6, -4.8, -4., -3.2, -2.4, -1.6, -0.8, 0., 0.8, 1.6, 2.4, 3.2, 4., 4.8, 5.6, 6.4, 7.2, 8., 8.8, 9.6],
        dtype = "float"
    )
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 4
    coeffs.c = 8
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 5
    rf = functions.RatFunc(coeffs)
    assert np.array_equal(rf(xs), ys)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_linear_inv():
    xs = np.arange(-10, 11)
    ys = np.array(
        [-6.4, -5.6, -4.8, -4., -3.2, -2.4, -1.6, -0.8, 0., 0.8, 1.6, 2.4, 3.2, 4., 4.8, 5.6, 6.4, 7.2, 8., 8.8, 9.6],
        dtype = "float"
    )
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 4
    coeffs.c = 8
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 5
    rf = functions.RatFunc(coeffs)
    rf = functions.RatFunc(coeffs)
    assert np.array_equal(rf.inv(ys), xs)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_constant():
    xs = np.arange(-10, 11)
    ys = np.full((21,), 10.0)
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 0
    coeffs.c = 20
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 2
    rf = functions.RatFunc(coeffs)
    assert np.array_equal(rf(xs), ys)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_constant_inv():
    xs = np.arange(-10, 11)
    ys = np.full((21,), 10.0)
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 0
    coeffs.c = 20
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 20
    rf = functions.RatFunc(coeffs)
    with pytest.raises(exceptions.MathError):
        rf.inv(ys)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_quadratic():
    xs = np.arange(-10, 11)
    ys = np.array([1.231638418079096, 1.1917808219178083, 1.1440677966101696, 1.086021505376344, 1.0140845070422535,
                   0.9230769230769231, 0.8055555555555556, 0.6521739130434783, 0.46153846153846156,0.3333333333333333,
                   1.5, 9.0, 6.666666666666667, 4.5, 3.5625, 3.074074074074074, 2.7804878048780486, 2.586206896551724,
                   2.448717948717949, 2.3465346534653464, 2.267716535433071
    ])
    coeffs = Value()
    coeffs.a = 5
    coeffs.b = 7
    coeffs.c = 6
    coeffs.d = 3
    coeffs.e = -5
    coeffs.f = 4
    rf = functions.RatFunc(coeffs)
    assert np.array_equal(rf(xs), ys)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_quadratic_inv():
    xs = np.arange(-10, 11)
    coeffs = Value()
    coeffs.a = 5
    coeffs.b = 7
    coeffs.c = 6
    coeffs.d = 3
    coeffs.e = -5
    coeffs.f = 4
    rf = functions.RatFunc(coeffs)
    with pytest.raises(NotImplementedError):
        rf.inv(xs)

def test_identical():
    xs = np.arange(-10, 11)
    rf = functions.Identical()
    assert np.array_equal(rf(xs), xs)

def test_identical_inv():
    xs = np.arange(-10, 11)
    ys = np.full((21,), 10.0)
    rf = functions.Identical()
    assert np.array_equal(rf.inv(xs), xs)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_linear():
    xs = np.arange(-10, 11)
    ys = np.array([-43, -39, -35, -31, -27, -23, -19, -15, -11, -7, -3, 1, 5, 9, 13, 17, 21, 25, 29, 33, 37
    ])
    coeffs = Value()
    coeffs.a = 4
    coeffs.b = -3
    rf = functions.Linear(coeffs)
    assert np.array_equal(rf(xs), ys)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_linear_inv():
    xs = np.arange(-10, 11)
    ys = np.array([-43, -39, -35, -31, -27, -23, -19, -15, -11, -7, -3, 1, 5, 9, 13, 17, 21, 25, 29, 33, 37
    ])
    coeffs = Value()
    coeffs.a = 4
    coeffs.b = -3
    rf = functions.Linear(coeffs)
    assert np.array_equal(rf.inv(ys), xs)

def test_tab_verb_with_default():
    mapping = [
        (1, "SawTooth"),
        (2, "Square"),
        (3, "Sinus"),
    ]
    default = "unknown signal type"
    tv = functions.TabVerb(mapping, default = default)
    assert tv(2) == "Square"
    assert tv(5) == default

def test_tab_verb_with_default_inv():
    mapping = [
        (1, "SawTooth"),
        (2, "Square"),
        (3, "Sinus"),
    ]
    default = "unknown signal type"
    tv = functions.TabVerb(mapping, default = default)
    assert tv.inv("Square") == 2
    assert tv.inv(default) is None


##
## Basic Integration Tests.
##
def test_compu_method_tab_verb():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_VERB.DEFAULT_VALUE
          "Verbal conversion with default value"
          TAB_VERB "%12.0" ""
          COMPU_TAB_REF CM.TAB_VERB.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB CM.TAB_VERB.DEFAULT_VALUE.REF
          "List of text strings and relation to impl value"
          TAB_VERB 3
          1 "SawTooth"
          2 "Square"
          3 "Sinus"
          DEFAULT_VALUE "unknown signal type"
        /end COMPU_VTAB
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    assert compu(1) == "SawTooth"
    assert compu.inv("Sinus") == 3
    assert compu(10) == "unknown signal type"

def test_compu_method_tab_verb_no_default_value():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_VERB.DEFAULT_VALUE
          "Verbal conversion with default value"
          TAB_VERB "%12.0" ""
          COMPU_TAB_REF CM.TAB_VERB.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB CM.TAB_VERB.DEFAULT_VALUE.REF
          "List of text strings and relation to impl value"
          TAB_VERB 3
          1 "SawTooth"
          2 "Square"
          3 "Sinus"
        /end COMPU_VTAB
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    assert compu(1) == "SawTooth"
    assert compu.inv("Sinus") == 3
    assert compu(10) is None

def test_compu_method_tab_verb_no_vtab():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_VERB.DEFAULT_VALUE
          "Verbal conversion with default value"
          TAB_VERB "%12.0" ""
          COMPU_TAB_REF CM.TAB_VERB.DEFAULT_VALUE.REF
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    with pytest.raises(exceptions.StructuralError):
        compu = functions.CompuMethod(session, module.compu_method[0])

def test_compu_method_identical():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.IDENTICAL
          "conversion that delivers always phys = int"
          IDENTICAL "%3.0" "hours"
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    xs = np.arange(-10, 11)
    assert np.array_equal(compu(xs), xs)
    assert np.array_equal(compu.inv(xs), xs)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_rat_func_identical():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.RAT_FUNC.IDENT
          "rational function with parameter set for int = f(phys) = phys"
          RAT_FUNC "%3.1" "m/s"
          COEFFS 0 1 0 0 0 1
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    xs = np.arange(-10, 11)
    assert np.array_equal(compu(xs), xs)
    assert np.array_equal(compu.inv(xs), xs)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_rat_func_linear():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.RAT_FUNC.DIV_81_9175
          "rational function with parameter set for impl = f(phys) = phys * 81.9175"
          RAT_FUNC "%8.4" "grad C"
          COEFFS 0 81.9175 0 0 0 1
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    xs = np.arange(-10, 11)
    ys = np.array([-819.1750000000001, -737.2575, -655.34, -573.4225, -491.505, -409.58750000000003, -327.67,
        -245.7525, -163.835, -81.9175, 0., 81.9175, 163.835, 245.7525, 327.67, 409.58750000000003,
        491.505, 573.4225, 655.34, 737.2575, 819.1750000000001
    ])
    assert np.array_equal(compu(xs), ys)
    assert np.array_equal(compu.inv(ys), xs)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_rat_func_no_coeffs():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.RAT_FUNC.DIV_81_9175
          "rational function with parameter set for impl = f(phys) = phys * 81.9175"
          RAT_FUNC "%8.4" "grad C"
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    with pytest.raises(exceptions.StructuralError):
        compu = functions.CompuMethod(session, module.compu_method[0])


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_linear():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.LINEAR.MUL_2
        "Linear function with parameter set for phys = f(int) = 2*int + 0"
         LINEAR "%3.1" "m/s"
         COEFFS_LINEAR 2 0
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    xs = np.arange(-10, 11)
    assert np.array_equal(compu(xs), xs * 2.0)
    assert np.array_equal(compu.inv(xs * 2.0), xs)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_linear_no_coeffs():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.LINEAR.MUL_2
        "Linear function with parameter set for phys = f(int) = 2*int + 0"
         LINEAR "%3.1" "m/s"
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    with pytest.raises(exceptions.StructuralError):
        compu = functions.CompuMethod(session, module.compu_method[0])
"""


"""


"""
    /begin COMPU_METHOD CM.VTAB_RANGE.DEFAULT_VALUE
       "verbal range with default value"
       TAB_VERB
       "%4.2"
       ""
       COMPU_TAB_REF CM.VTAB_RANGE.DEFAULT_VALUE.REF
    /end COMPU_METHOD

    /begin COMPU_VTAB_RANGE CM.VTAB_RANGE.DEFAULT_VALUE.REF
       ""
       11
       0 1 "Zero_to_one"
       2 3 "two_to_three"
       4 7 "four_to_seven"
       14 17 "fourteen_to_seventeen"
       18 99 "eigteen_to_ninetynine"
       100 100 "hundred"
       101 101 "hundredone"
       102 102 "hundredtwo"
       103 103 "hundredthree"
       104 104 "hundredfour"
       105 105 "hundredfive"
       DEFAULT_VALUE "out of range value"
    /end COMPU_VTAB_RANGE
"""
