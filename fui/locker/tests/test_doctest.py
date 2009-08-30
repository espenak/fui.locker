import unittest

from zope.testing import doctestunit, doctest
from zope.component import testing, eventtesting

from Testing import ZopeTestCase as ztc

from fui.locker.content import lockerregistry, lockerreservation
from fui.locker.tests import base


optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | \
		doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

def test_suite():
    return unittest.TestSuite([
		doctest.DocTestSuite(lockerregistry, optionflags = optionflags),
		ztc.ZopeDocTestSuite(lockerreservation, optionflags = optionflags,
				test_class = base.LockerreservationTestCase),

		ztc.ZopeDocFileSuite(
			'tests/functional.doctest',
			package = 'fui.locker',
			test_class = base.FuiLockerFunctionalTestCase,
			optionflags = optionflags),
		])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
