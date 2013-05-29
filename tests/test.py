__author__ = 'Nick'

from unittest import TestCase
import usgs

class retrieval_tests(TestCase):
	def __init___(self):
		usgs_object = usgs.gage('')
		# TODO: we should probably slurp in a list of gages to test to make sure any test problems don't happen on only one gage
		# TODO: second change would be to  predownload some data nad make sure that it works on that data, but still test the whole stack of code on live data on the server, which would help us know if their API changes and we aren't compliant.
