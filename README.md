A wrapper around the USGS Water Information System JSON API that provides native Python access.

Documentation is available at Read the Docs (https://usgs-api.readthedocs.org/en/latest). The code and documentation are licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

Please note that the module name is usgs, not usgs-api for importing.

If you would like to use the functionality to return pandas objects, you must install pandas separately as it is not a hard dependency (the module will load and run without that functionality and will raise an error if you attempt to use it. Windows users may need to install pandas separately via the binary installer. Pandas, in turn, requires numpy, which may also need to be installed using the binary installer if you do not already have it installed.