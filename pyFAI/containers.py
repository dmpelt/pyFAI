# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Project: Azimuthal integration
#             https://github.com/silx-kit/pyFAI
#
#    Copyright 2013-2016 (C) European Synchrotron Radiation Facility, Grenoble, France
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  .
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#  .
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

"""Module containing holder classes, like returned objects."""

from __future__ import absolute_import, print_function, division, with_statement

__author__ = "Valentin Valls"
__contact__ = "valentin.valls@esrf.eu"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "02/09/2016"
__status__ = "development"


class IntegrateResult(tuple):
    """
    Class defining shared information between Integrate1dResult and Integrate2dResult.
    """

    def __init__(self):
        self._sum = None
        self._count = None
        self._unit = None
        self._has_dark_correction = None
        self._has_flat_correction = None
        self._normalization_factor = None
        self._polarization_factor = None

    @property
    def sum(self):
        """
        Sum information

        @rtype: numpy.ndarray
        """
        return self._sum

    def _set_sum(self, sum_):
        """
        Set the sum information

        @type count: numpy.ndarray
        """
        self._sum = sum_

    @property
    def count(self):
        """
        Count information

        @rtype: numpy.ndarray
        """
        return self._count

    def _set_count(self, count):
        """
        Set the count information

        @type count: numpy.ndarray
        """
        self._count = count

    @property
    def unit(self):
        """
        Radial unit

        @rtype: string
        """
        return self._unit

    def _set_unit(self, unit):
        """
        Define the radial unit

        @type unit: str
        """
        self._unit = unit

    @property
    def has_dark_correction(self):
        """
        True if a dark correction was applied

        @rtype: bool
        """
        return self._has_dark_correction

    def _set_has_dark_correction(self, has_dark_correction):
        """
        Define if dark correction was applied

        @type has_dark_correction: bool
        """
        self._has_dark_correction = has_dark_correction

    @property
    def has_flat_correction(self):
        """
        True if a flat correction was applied

        @rtype: bool
        """
        return self._has_flat_correction

    def _set_has_flat_correction(self, has_flat_correction):
        """
        Define if flat correction was applied

        @type has_flat_correction: bool
        """
        self._has_flat_correction = has_flat_correction

    @property
    def normalization_factor(self):
        """
        The normalisation factor used

        @rtype: float
        """
        return self._normalization_factor

    def _set_normalization_factor(self, normalization_factor):
        """
        Define the used normalisation factor

        @type normalization_factor: float
        """
        self._normalization_factor = normalization_factor

    @property
    def polarization_factor(self):
        """
        The polarization factor used

        @rtype: float
        """
        return self._polarization_factor

    def _set_polarization_factor(self, polarization_factor):
        """
        Define the used polarization factor

        @type polarization_factor: float
        """
        self._polarization_factor = polarization_factor


class Integrate1dResult(IntegrateResult):
    """
    Result of an 1D integration. Provide a tuple access as a simple way to reach main attrbutes.
    Default result, extra results, and some interagtion parameters are available from attributes.

    For compatibility with older API, the object can be read as a tuple in different ways:

    .. codeblock::

        result = ai.integrate1d(...)
        if result.sigma is None:
            radial, I = result
        else:
            radial, I, sigma = result
    """
    def __new__(self, radial, intensity, sigma=None):
        if sigma is None:
            t = radial, intensity
        else:
            t = radial, intensity, sigma
        return IntegrateResult.__new__(Integrate1dResult, t)

    def __init__(self, radial, intensity, sigma=None):
        super(Integrate1dResult, self).__init__()

    @property
    def radial(self):
        """
        Radial positions (q/2theta/r)

        @rtype: numpy.ndarray
        """
        return self[0]

    @property
    def intensity(self):
        """
        Regrouped intensity

        @rtype: numpy.ndarray
        """
        return self[1]

    @property
    def sigma(self):
        """
        Error array if it was requested

        @rtype: numpy.ndarray, None
        """
        if len(self) == 2:
            return None
        return self[2]


class Integrate2dResult(IntegrateResult):
    """
    Result of an 2D integration. Provide a tuple access as a simple way to reach main attrbutes.
    Default result, extra results, and some interagtion parameters are available from attributes.

    For compatibility with older API, the object can be read as a tuple in different ways:

    .. codeblock::

        result = ai.integrate2d(...)
        if result.sigma is None:
            I, radial, azimuthal = result
        else:
            I, radial, azimuthal, sigma = result
    """
    def __new__(self, intensity, radial, azimuthal, sigma=None):
        if sigma is None:
            t = intensity, radial, azimuthal
        else:
            t = intensity, radial, azimuthal, sigma
        return IntegrateResult.__new__(Integrate2dResult, t)

    def __init__(self, intensity, radial, azimuthal, sigma=None):
        super(Integrate2dResult, self).__init__()

    @property
    def intensity(self):
        """
        Azimuthaly regrouped intensity

        @rtype: numpy.ndarray
        """
        return self[0]

    @property
    def radial(self):
        """
        Radial positions (q/2theta/r)

        @rtype: numpy.ndarray
        """
        return self[1]

    @property
    def azimuthal(self):
        """
        Azimuthal positions (chi)

        @rtype: numpy.ndarray
        """
        return self[2]

    @property
    def sigma(self):
        """
        Error array if it was requested

        @rtype: numpy.ndarray, None
        """
        if len(self) == 3:
            return None
        return self[3]
