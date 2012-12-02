Structure and Usage of the USGS API
=============================================================

The Python wrapper to this API is young, so these docs are colored with a large dose of code to help you understand the
approach we used when developing the wrapper. This wrapper provides results by composing a URL to USGS' NWIS JSON API
and translating the results into native python objects as a list of dictionaries
(from `simplejson/json <http://pypi.python.org/pypi/simplejson/>`_) or into a
`pandas <http://pypi.python.org/pypi/pandas/>`_ object.
