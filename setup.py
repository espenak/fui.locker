from setuptools import setup, find_packages
import os

version = '1.3.0'

setup(name='fui.locker',
	version=version,
	description="",
	long_description=open("README.rst").read(),
	# Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
	classifiers=[
	  "Framework :: Plone",
	  "Programming Language :: Python",
	  "Topic :: Software Development :: Libraries :: Python Modules",
	  ],
	keywords='',
	author='Espen A. Kristiansen',
	author_email='post@espenak.net',
	url='http://github.com/espenak/fui.locker',
	license='GPL',
	packages=find_packages(exclude=['ez_setup']),
	namespace_packages=['fui'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
	    'setuptools',
		# -*- Extra requirements: -*-
	],
	entry_points="""
	# -*- Entry points: -*-

	[distutils.setup_keywords]
	paster_plugins = setuptools.dist:assert_string_list

	[egg_info.writers]
	paster_plugins.txt = setuptools.command.egg_info:write_arg
	""",
	paster_plugins = ["ZopeSkel"],
)
