__author__ = 'nicksantos'

from setuptools import setup

setup(name='usgs-api',
	version='0.1a',
	description='A Python wrapper for the USGS National Water Information System JSON API',
	url='https://bitbucket.org/UltraAyla/usgs-api',
	author='Nick Santos',
	author_email='python@nicksantos.com',
	license='Creative Commons Attribution Sharealike 3.0 Unported',
	packages=['usgs','docs'],
	install_requires=[
		'urllib2',
		'urllib',
		'json',
		'pandas',
		],
	zip_safe=False)

