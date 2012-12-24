__author__ = 'nicksantos'

import logging

log = logging.getLogger(__name__)

try:
	from lxml import objectify
except:
	log.info("Package lxml is required. Please install lxml. If you are on Windows, you may need to download the binary"
			 "distribution")

class _waterMLObject():
	"""
		The base class for constructing WaterML-based data into Python. It is built so it can handle empty objects,
		allowing the user to add data, then serialize the data out into XML (maybe not valid waterML?).
	"""

	def __init__(self, xml = None):
		self._xml = xml
		self._object_nodes = [] # these are nodes that have their own subobject
		self._allowed_nodes = [] # a list so users can push new nodes onto it. Will be iterated through and the object tree will be searched for items here.
								# each subobject cna have its own attribute for this, so we can know where we are in the tree. Ideally, each subobject's
								# "xml" attribute just contains the relevant part and can, itself, be parsed by objectify, if we are willing to use a
								# slower, more memory-intensive method that is a bit more convenient.
		self._allowed_attributes = [] # same

		self.children = {} # any parsed out child objects. Dict to allow lookups via
							# something like response.children['timeSeries'].children['variable']

	def add_child(self,child_name,child_object):
		self.__dict__[child_name] = child_object
		self.children[child_name] = child_object

	def parse_xml(self, xml=None):
		if not xml:
			self.xml_data = objectify.parse(self._xml)
		else:
			self.xml_data = objectify.parse(xml)

	def check_children(self):
		pass

	def __unicode__(self):
		if hasattr(self,'value'): # if it has the value attribute, then it's an item with a value in addition to the attributes on the node, and we want to return this when used in a scalar context
			return unicode(self.value)

	def __str__(self):
		if hasattr(self,'value'):
			return str(self.value)

	def __int__(self):
		if hasattr(self,'value'):
			return int(self.value)

	def slurp(self, xml, tree):

		if not xml:
			if not tree:
				if not self.xml_data:
					raise ValueError('parameter xml is required unless you have previously run the parse_xml method')
			else:
				self.xml_data = tree # we're on a subobject now, so putting tree in for xml_data works
		else:
			self.parse_xml(xml)

		for node_name in self._allowed_nodes:
			if node name in self._object_nodes:
				node_obj = globals()[node_name]
				# process into subobject, call subobject _slurp if it exists. use add_child to add it to this object
				child_node.slurp(tree = subtree_object)
			else:
				# retrieve the data and set it as an attribute
				pass

class waterMLRootObject(_waterMLObject):
	"""
		This should be the root object for use externally
	"""
	def __init__(self):
		_waterMLObject.__init__(self)
		self._object_nodes += ["queryInfo","timeSeriesResponse"]

class queryInfo(_waterMLObject):
	def __init__(self):
		_waterMLObject.__init__(self)


class timeSeries(_waterMLObject):
	def __init__(self):
		_waterMLObject.__init__(self)
		self._object_nodes += ["sourceInfo","variable"]
		self.values = []

	def _slurp(self):
		pass


class variable(_waterMLObject):
	def __init__(self):
		_waterMLObject.__init__(self)
		self.oid = None
		self.noDataValue = None

class value(_waterMLObject):
	def __init__(self):
		_waterMLObject.__init__(self)
		self.qualifiers = None
		self.dateTime = None
		self.value = None
		self.text = self.value

	def _slurp(self, data):
		pass

