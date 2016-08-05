#!/usr/bin/python
# coding: utf-8
#
#    Project: Azimuthal integration
#             https://github.com/pyFAI/pyFAI
#
#    Copyright (C) 2015 European Synchrotron Radiation Facility, Grenoble, France
#
#    Principal author:       Jérôme Kieffer (Jerome.Kieffer@ESRF.eu)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import division, print_function, absolute_import

__doc__ = "test suite for average library"
__author__ = "Jérôme Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "04/08/2016"

import unittest
import numpy
import os
import fabio
from .utilstest import UtilsTest, getLogger
from .. import average

logger = getLogger(__file__)


class TestAverage(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.unbinned = numpy.random.random((64, 32))
        self.dark = self.unbinned.astype("float32")
        self.flat = 1 + numpy.random.random((64, 32))
        self.raw = self.flat + self.dark
        self.tmp_file = os.path.join(UtilsTest.tempdir, "testUtils_average.edf")

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.dark = self.flat = self.raw = self.tmp_file = None

    def test_average_dark(self):
        """
        Some testing for dark averaging
        """
        one = average.average_dark([self.dark])
        self.assertEqual(abs(self.dark - one).max(), 0, "data are the same")

        two = average.average_dark([self.dark, self.dark])
        self.assertEqual(abs(self.dark - two).max(), 0, "data are the same: mean test")

        three = average.average_dark([numpy.ones_like(self.dark), self.dark, numpy.zeros_like(self.dark)], "median")
        self.assertEqual(abs(self.dark - three).max(), 0, "data are the same: median test")

        four = average.average_dark([numpy.ones_like(self.dark), self.dark, numpy.zeros_like(self.dark)], "min")
        self.assertEqual(abs(numpy.zeros_like(self.dark) - four).max(), 0, "data are the same: min test")

        five = average.average_dark([numpy.ones_like(self.dark), self.dark, numpy.zeros_like(self.dark)], "max")
        self.assertEqual(abs(numpy.ones_like(self.dark) - five).max(), 0, "data are the same: max test")

        six = average.average_dark([numpy.ones_like(self.dark), self.dark, numpy.zeros_like(self.dark), self.dark, self.dark], "median", .001)
        self.assert_(abs(self.dark - six).max() < 1e-4, "data are the same: test threshold")
        if fabio.hexversion < 262147:
            logger.error("Error: the version of the FabIO library is too old: %s, please upgrade to 0.4+. Skipping test for now", fabio.version)
            return
        seven = average.average_images([self.raw], darks=[self.dark], flats=[self.flat], threshold=0, output=self.tmp_file)
        self.assert_(abs(numpy.ones_like(self.dark) - fabio.open(seven).data).mean() < 1e-2, "average_images")

    def test_average_monitor(self):
        data1 = numpy.array([[1.0, 3.0], [3.0, 4.0]])
        data2 = numpy.array([[2.0, 2.0], [1.0, 4.0]])
        data3 = numpy.array([[3.0, 1.0], [2.0, 4.0]])
        mon1, mon2, mon3 = 0.1, 1.0, 3.1
        image1 = fabio.numpyimage.numpyimage(data1)
        image1.header["mon"] = str(mon1)
        image2 = fabio.numpyimage.numpyimage(data2)
        image2.header["mon"] = str(mon2)
        image3 = fabio.numpyimage.numpyimage(data3)
        image3.header["mon"] = str(mon3)
        image_ignored = fabio.numpyimage.numpyimage(data3)

        expected_result = data1 / mon1 + data2 / mon2 + data3 / mon3
        filename = average.average_images([image1, image2, image3, image_ignored], threshold=0, filter_="sum", monitor_key="mon", output=self.tmp_file)
        result = fabio.open(filename).data
        numpy.testing.assert_array_almost_equal(result, expected_result, decimal=3)

class TestQuantile(unittest.TestCase):
    """
    Check the quantile filter in average
    """
    def setUp(self):
        shape = (100, 100)
        dtype = numpy.float32
        self.image_files = []
        self.outfile = os.path.join(UtilsTest.tempdir, "out.edf")
        res = numpy.zeros(shape, dtype=dtype)
        for i in range(5):
            fn = os.path.join(UtilsTest.tempdir, "img_%i.edf" % i)
            if i == 3:
                data = numpy.zeros(shape, dtype=dtype)
            elif i == 4:
                data = numpy.ones(shape, dtype=dtype)
            else:
                data = numpy.random.random(shape).astype(dtype)
                res += data
            e = fabio.edfimage.edfimage(data=data)
            e.write(fn)
            self.image_files.append(fn)
        self.res = res / 3.0

    def tearDown(self):
        for fn in self.image_files:
            os.unlink(fn)
        if os.path.exists(self.outfile):
            os.unlink(self.outfile)
        self.image_files = None
        self.res = None

    def test_quantile(self):
        file_name = average.average_images(
            self.image_files,
            quantiles=(0.2, 0.8),
            threshold=0,
            filter_="quantiles",
            output=self.outfile)
        self.assert_(numpy.allclose(fabio.open(file_name).data, self.res),
                     "average with quantiles gives bad results")


class TestAverageMonitorName(unittest.TestCase):

    def setUp(self):
        header = {
            "mon1": "100",
            "bad": "foo",
            "counter_pos": "12 13 14 foo",
            "counter_mne": "mon2 mon3 mon4 mon5",
            "bad_size_pos": "foo foo foo",
            "bad_size_mne": "mon2 mon3 mon4 mon5",
            "mne_not_exists_pos": "12 13 14 foo",
            "pos_not_exists_mne": "mon2 mon3 mon4 mon5",
        }
        self.image = fabio.numpyimage.numpyimage(numpy.array([]), header)

    def test_monitor(self):
        result = average._get_monitor_value_from_edf(self.image, "mon1")
        self.assertEquals(100, result)

    def test_monitor_in_counter(self):
        result = average._get_monitor_value_from_edf(self.image, "counter/mon3")
        self.assertEquals(13, result)

    def test_bad_monitor(self):
        self.assertRaises(average.MonitorNotFound, average._get_monitor_value_from_edf, self.image, "bad")

    def test_bad_monitor_in_counter(self):
        self.assertRaises(average.MonitorNotFound, average._get_monitor_value_from_edf, self.image, "counter/mon5")

    def test_bad_counter_syntax(self):
        self.assertRaises(average.MonitorNotFound, average._get_monitor_value_from_edf, self.image, "counter/mon5/1")

    def test_missing_monitor(self):
        self.assertRaises(average.MonitorNotFound, average._get_monitor_value_from_edf, self.image, "not_exists")

    def test_missing_counter(self):
        self.assertRaises(average.MonitorNotFound, average._get_monitor_value_from_edf, self.image, "not_exists/mon")

    def test_missing_counter_monitor(self):
        self.assertRaises(average.MonitorNotFound, average._get_monitor_value_from_edf, self.image, "counter/not_exists")

    def test_missing_counter_mne(self):
        self.assertRaises(average.MonitorNotFound, average._get_monitor_value_from_edf, self.image, "mne_not_exists/mon")

    def test_missing_counter_pos(self):
        self.assertRaises(average.MonitorNotFound, average._get_monitor_value_from_edf, self.image, "pos_not_exists/mon")

    def test_missing_counter_pos_element(self):
        self.assertRaises(average.MonitorNotFound, average._get_monitor_value_from_edf, self.image, "bad_size/mon")

    def test_edf_file_motor(self):
        image = fabio.open(UtilsTest.getimage("Pilatus1M.edf"))
        result = average._get_monitor_value_from_edf(image, "motor/lx")
        self.assertEqual(result, -0.2)

    def test_edf_file_key(self):
        image = fabio.open(UtilsTest.getimage("Pilatus1M.edf"))
        result = average._get_monitor_value_from_edf(image, "scan_no")
        self.assertEqual(result, 19)

def suite():
    testsuite = unittest.TestSuite()

    test_names = unittest.getTestCaseNames(TestAverage, "test")
    for test in test_names:
        testsuite.addTest(TestAverage(test))

    test_names = unittest.getTestCaseNames(TestAverageMonitorName, "test")
    for test in test_names:
        testsuite.addTest(TestAverageMonitorName(test))
    return testsuite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
    UtilsTest.clean_up()