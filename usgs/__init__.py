__author__ = 'nicksantos'

"""
	Handles all interfacing with USGS, with the goal of making (parts) of their JSON
	API available to Python as native objects
"""

import pandas
import urllib
import urllib2
import json

class gage():
	def __init__(self, site_code = None, time_period = "P7D", url_params = {}):

		self.site_code = site_code
		self.time_series = None
		self.time_period = time_period
		self.url_params = url_params # optional dict of params - url key value pairs passed to the api
		self.data_frame = None

		self.startDT = None
		self.endDT = None

		self._json_string = None
		self._base_url = "http://waterservices.usgs.gov/nwis/iv/"

	def check_params(self, params = ('site_code',)):
		"""
			Makes sure that we have the base level of information necessary to run a query
			to prevent lazy setup errors
		"""

		for param in params:
			if self.__dict__[param] is None and param not in self.url_params:
				raise AttributeError("Required attribute %s must be set or provided in url_params before running this method" % param)

	def retrieve(self, return_pandas=False, automerge = True):
		"""
			runs the relevant private methods in sequence

			:param:return_pandas: specifies whether or not to return the pandas object, or to return a standard
		"""

		# makes sure that the user didn't forget to set something after init
		self.check_params()

		self._retrieve_data()
		self._json_to_dataframe(create_pandas = return_pandas)

		if return_pandas:
			return self.data_frame
		else:
			return self.time_series

	def _retrieve_data(self):
		"""
			requests retrieves, and stores the json
		"""

		# add the relevant parameters into the dictionary passed by the user (if any
		self.url_params['format'] = "json"
		self.url_params['sites'] = self.site_code

		if self.time_period and not self.startDT and 'startDT' not in self.url_params:
			# if we have a time period, but not a time range, use the period
			self.url_params['period'] = self.time_period
		else:
			# otherwise, use the time range if it works (doesn't currently valdidate the dates
			# TODO: Validate the date formats
			self.check_params(('startDT','endDT')) # it's possible that they won't be defined

			self.url_params['startDT'] = self.startDT
			self.url_params['endDT'] = self.endDT

		# merge parameters into the url
		request_url = self._base_url + "?" + urllib.urlencode(self.url_params)

		# open the url and read in the json string to a private variable
		request = urllib2.Request(request_url)
		data_stream = urllib2.urlopen(request)
		self._json_string = data_stream.read()

		self._json_data = json.loads(self._json_string)

	def _json_to_dataframe(self, create_pandas = False):
		"""
			converts the json to a pandas data frame
		"""
		self.time_series = self._json_data['value']['timeSeries'][0]['values'][0]['value']

		if create_pandas:
			self.data_frame = pandas.DataFrame(self.time_series)


	def _merge_with_existing(self):
		"""
			if we execute a request when we already have data, this method attempts
			to merge the two datasets into a single time series so you can effectively
			execute a partial query and then go further if need be
		"""
		pass

# TODO: Create shortcut function for getting data from a station - single function

def retrieve_flow(user_gage_id=None, return_pandas = False):
	"""
		Helper function that initializes the gage for you, runs the necessary methods, and just returns the table. Takes
		no date limiters so default is used. If you need to specify dates, please use the gage class
	"""

	if not user_gage_id:
		raise ValueError("user_gage_id must be specified to use this helper function. If you want to initialize a gage"
						 "without specifying an ID, please use the gage class")

	t_gage = gage(user_gage_id)
	return t_gage.retrieve(return_pandas=return_pandas)