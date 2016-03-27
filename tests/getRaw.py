#!/usr/bin/env python

import os

import unittest
import lsst.utils.tests as utilsTests

from lsst.pex.policy import Policy
import lsst.daf.persistence as dafPersist
from lsst.obs.wiyn.whirc import WhircMapper

import lsst.afw.display.ds9 as ds9
import lsst.afw.display.utils as displayUtils

import lsst.afw.cameraGeom as cameraGeom
import lsst.afw.cameraGeom.utils as cameraGeomUtils
try:
    type(display)
except NameError:
    display = False


def getButler(datadir):
    bf = dafPersist.ButlerFactory(mapper=WhircMapper(root=os.path.join(datadir, "raw"),
                                                     calibRoot=os.path.join(datadir, "calib")))
    return bf.create()


class GetRawTestCase(unittest.TestCase):
    """Testing butler raw image retrieval"""

    def setUp(self):
        self.datadir = os.getenv("TESTDATA_WHIRC_DIR")
        assert self.datadir, "testdata_whirc is not setup"
        self.butler = getButler(self.datadir)
        self.size = (2144, 2050)
        self.dataId = {'date': 20111115,
                       'year': 2011,
                       'month': 11,
                       'day': 15,
                       'expnum': 237,
                       'mjd': 55881.333657
                       }

    def tearDown(self):
        del self.butler

    def assertExposure(self, exp, ccd):
        print "dataId: ", self.dataId
        print "ccd: ", ccd
        print "width: ", exp.getWidth()
        print "height: ", exp.getHeight()
        print "detector name: ", exp.getDetector().getId().getName()

        self.assertEqual(exp.getWidth(), self.size[0])
        self.assertEqual(exp.getHeight(), self.size[1])
        self.assertEqual(exp.getFilter().getFilterProperty().getName(), "OPEN")
        self.assertEqual(exp.getDetector().getId().getName(), "VIRGO1")

    def testRaw(self):
        """Test retrieval of raw image"""
        ccd = 'VIRGO1'
        raw = self.butler.get("raw", self.dataId, ccd=ccd)

        self.assertExposure(raw, ccd)

        if display:
            ccd = cameraGeom.cast_Ccd(raw.getDetector())
            for amp in ccd:
                amp = cameraGeom.cast_Amp(amp)
                print ccd.getId(), amp.getId(), amp.getDataSec().toString(), \
                    amp.getBiasSec().toString(), amp.getElectronicParams().getGain()
            cameraGeomUtils.showCcd(ccd, ccdImage=raw, frame=frame)
            frame += 1

#     def testFlat(self):
#         """Test retrieval of flat image"""
#         ccd='VIRGO1'
#         flat = self.butler.get("flat", self.dataId, ccd=ccd)
#
#         self.assertExposure(flat, ccd)

#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


def suite():
    """Returns a suite containing all the test cases in this module."""

    utilsTests.init()

    suites = []
    suites += unittest.makeSuite(GetRawTestCase)
    suites += unittest.makeSuite(utilsTests.MemoryTestCase)
    return unittest.TestSuite(suites)


def run(shouldExit = False):
    """Run the tests"""
    utilsTests.run(suite(), shouldExit)

if __name__ == "__main__":
    run(True)
