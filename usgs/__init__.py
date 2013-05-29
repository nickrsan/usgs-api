__author__ = 'nicksantos'

"""
	Handles all interfacing with USGS, with the goal of making (parts) of their JSON
	API available to Python as native objects
"""

import urllib
import urllib2
import json
from StringIO import StringIO
import gzip
from datetime import datetime
from logging import getLogger

log = getLogger("usgs_api")
log.info("usgs api loaded")

try:
	import pandas
except ImportError:
	log.info("failed to import pandas. Pandas object functionality will be unavailable (naturally). Install the 'pandas'"
			 "module if you need pandas/scientific functionality")
	pass  # pass - user should not be concerned.

config_max_windows = 52  # 52 * 2 weeks = 2 years - if window size changes, then this is just a multiplier for how many
						# times to batch the request
config_window_size = 14  # days
config_min_timestamp = 1191196800


class gage():
	def __init__(self, site_code=None, time_period="P7D", url_params={}, start_timestamp=None, end_timestamp=None):
		"""
		:param site_code: A USGS Site code for the gage this object represents. See `the USGS documentation
			<http://help.waterdata.usgs.gov/codes-and-parameters/codes#search_station_nm>`_
		:param time_period: A compatible period string as specified in
			`the USGS time period documentation <http://waterservices.usgs.gov/rest/IV-Service.html#Specifying>`_ - this parameter
			only accepts "period" values as explained in that documentation. If you would like to specify a time range
			using startDT and endDT please use the url_params argument. If you specify both, current behavior
			uses the time period as being more specific. An exception will not be raised.
		:param url_params: A dictionary of other parameters to pass to the USGS server in key/value format. They
			will be automatically added to the query. Case sensitive. For a full list of parameters, see
			`the USGS web service documentation <http://waterservices.usgs.gov/rest/IV-Service.html>`_
		"""

		self.site_code = site_code
		self.time_series = None
		self.time_period = time_period
		self.url_params = url_params  # optional dict of params - url key value pairs passed to the api
		self.data_frame = None

		self.startDT = None
		self.endDT = None

		self.start_timestamp = start_timestamp
		self.end_timestamp = end_timestamp

		self.batch = False

		self._json_string = None
		self._base_url = "http://waterservices.usgs.gov/nwis/iv/"

	def check_params(self, params=('site_code',)):
		"""
			Makes sure that we have the base level of information necessary to run a query
			to prevent lazy setup errors
		"""

		for param in params:
			if self.__dict__[param] is None and param not in self.url_params:
				raise AttributeError("Required attribute %s must be set or provided in url_params before running this method" % param)

		if self.startDT and self.start_timestamp:

	def retrieve(self, return_pandas=False, automerge=True):
		"""
			Retrieves data from the server based upon class configuration. Returns the a list of dicts by default,
			with keys set by the returned data from the server. If return_pandas is True, returns a pandas data frame.

			:param return_pandas: specifies whether or not to return the pandas object. When True, returns a pandas
				object. When False, returns the default list of dicts. If True and you have not installed pandas, will raise
				ValueError
			:param automerge: Not yet implemented! Warning! Intent is that when returning a pandas table, automerge
			    will allow you to run multiple separate requests for the same gage (different time series with gaps, etc)
			    and merge them into a single result for the gage
		"""

		# makes sure that the user didn't forget to set something after init

		if return_pandas and not pandas:  # do this first so we don't find out AFTER doing everything else
			_pandas_no_exist()

		self.batch = self.check_params()  # TODO: Make check_params determine if it's a multiwindow query

		if self.batch:  # if we need to retrieve multiple windows, then call the batching function
			self._batch()
		else:  # otherwise, if the time period is short enough, just retrieve the data
			self._retrieve_data()

		self._json_to_dataframe(create_pandas=return_pandas)

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
			# otherwise, use the time range if it works (doesn't currently validate the dates)
			# TODO: Validate the date formats
			self.check_params(('startDT', 'endDT'))  # it's possible that they won't be defined

			self.url_params['startDT'] = self.startDT
			self.url_params['endDT'] = self.endDT

		# merge parameters into the url
		request_url = self._base_url + "?" + urllib.urlencode(self.url_params)

		# open the url and read in the json string to a private variable
		request = urllib2.Request(request_url)
		request.add_header('Accept-encoding', 'gzip')  # be kind to the USGS servers - see http://waterservices.usgs.gov/rest/IV-Service.html#gzip

		data_stream = urllib2.urlopen(request)
		if data_stream.info().get('Content-Encoding') == 'gzip':  # with thanks to StackOverflow for the efficient code
			buf = StringIO(data_stream.read())
			f = gzip.GzipFile(fileobj=buf)
			self._json_string = f.read()
		else:
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

	def _batch(self):
		"""
			Automatically batches time windows of more than seven days
		"""

		orig_startDT = self.startDT
		orig_endDT = self.endDT
		orig_time_period = self.time_period

		if type(self.startDT) is not int or type(self.endDT) is not int:
			raise ValueError("Cannot batch and merge queries without integer unix timestamps in startDT and endDT")

		# TODO: make it check the start timestamp for if it's before the minimum configured time, then create windows
		# and loop through them as individual requests, and merge their data together.

	def retrieve_to_csv(self, file_path=None):
		"""
			Retrieves the data automatically to a CSV file
		"""

		if not file_path:
			raise ValueError("No path specified")

# TODO: Create shortcut function for getting data from a station - single function

def retrieve_flow(gage_id=None, return_pandas = False):
	"""
		Helper function that initializes the gage for you, runs the necessary methods, and returns the table (list of dicts).
		Takes no date limiters so default is used. If you need to specify dates, please use the gage class.

		:param gage_id: The USGS id for the gage
		:param return_pandas: specifies whether or not to return the pandas object. When True, returns a pandas
				object. When False, returns the default list of dicts. If True and you have not installed pandas, will raise
				ValueError

	"""

	if return_pandas and not pandas:
		_pandas_no_exist()

	if not gage_id:
		raise ValueError("gage_id must be specified to use this helper function. If you want to initialize a gage"
						 " without specifying an ID, please use the gage class")

	t_gage = gage(gage_id)
	return t_gage.retrieve(return_pandas=return_pandas)


def _pandas_no_exist():
	raise ValueError("Pandas could not be imported, cannot return pandas object. Try again after checking"
	                 " that the pandas module is correctly installed or using return_pandas = False")