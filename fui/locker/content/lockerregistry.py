"""Definition of the LockerRegistry content type and associated schemata and
other logic.

This file contains a number of comments explaining the various lines of
code. Other files in this sub-package contain analogous code, but will 
not be commented as heavily.

Please see README.txt for more information on how the content types in
this package are used.
"""

import re
from zope.interface import implements
from zope.component import adapter, getMultiAdapter, getUtility

from zope.app.container.interfaces import INameChooser

from Acquisition import aq_inner, aq_parent

from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IObjectInitializedEvent

from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from fui.locker.interfaces import ILockerRegistry

from fui.locker.config import PROJECTNAME
from fui.locker.config import PROMOTIONS_PORTLET_COLUMN

from fui.locker import LockerMessageFactory as _



RANGE_DESCRIPTION = u"""One locker-range per line. Each line must contain a
label (a description of where the lockers are located), followed by 
number-ranges ('-' separated by numbers). The numbers define a valid
locker-number range. Example line: 'Bachelor lesesal:110-120,122-150'.
This line will make any number between 110 and 150, including the two numbers
and excluding 121, a valid locker number. You can define as many ranges as you
like, each on a separate line."""

LOCKERLIST_PATT = re.compile("^.+?:(\d+-\d+)(,\d+-\d+)*$")

LOCKER_EXAMPLE = \
u"""Bachelor lesesal:110-120,122-150
Bachelorlesesal 1.etg:4001-4010,4013-4020,4100-4130"""


EMAIL_TPL = \
u"""Someone has registered locker '%(lockerid)s' with your username
(%(username)s). If this someone is not you, please let us know by
replying to this email.

--
Fagutvalget ved Institutt for informatikk (FUI)
http://fui.ifi.uio.no"""




EMAIL_DESCRIPTION = \
u"""The email sent to notify a user about a registration. Use 
'%(username)s', '%(fullname)s' and '%(lockerid)s' to insert
names and locker number. The subject of the mail is the
title of this registry, and the from-address is the one
configured globally in site settings."""


# This is the Archetypes schema, defining fields and widgets. We extend
# the one from ATContentType's ATFolder with our additional fields.
LockerRegistrySchema = folder.ATFolderSchema.copy() + atapi.Schema((
	atapi.BooleanField("emailnotification",
		required = False,
		searchable = False,
		storage = atapi.AnnotationStorage(),
		widget = atapi.BooleanWidget(
				label = u"Use email notification?",
				description = u"Send an email to the user when he/she " \
						"registers a locker")
		),

	atapi.TextField("emailcontent",
		required = True,
		searchable = False,
		storage = atapi.AnnotationStorage(),
		default = EMAIL_TPL,
		allowable_content_types = ('text/plain',),
		widget = atapi.TextAreaWidget(
				rows = 10,
				label = u"Notification email",
				description = EMAIL_DESCRIPTION)
		),

	atapi.LinesField("bachelorlockers",
		required = True,
		searchable = False,
		default = LOCKER_EXAMPLE,
		storage = atapi.AnnotationStorage(),
		widget = atapi.LinesWidget(
				label = u"Lockers available to bachelor students",
				description = RANGE_DESCRIPTION)
		),

	atapi.LinesField("masterlockers",
		required = True,
		searchable = False,
		storage = atapi.AnnotationStorage(),
		widget = atapi.LinesWidget(
				label = u"Lockers available to master students",
				description = RANGE_DESCRIPTION)
		),

	atapi.TextField("text",
		required=False,
		searchable=True,
		storage=atapi.AnnotationStorage(),
		validators=('isTidyHtmlWithCleanup',),
		default_output_type='text/x-html-safe',
		widget=atapi.RichWidget(
				label = u"Descriptive text",
				description = u"This text is shown above the registration form.",
				rows = 25,
				allow_file_upload = False),
		),
	))

# We want to ensure that the properties we use as field properties (see
# below), use AnnotationStorage. Without this, our property will conflict
# with the attribute with the same name that is being managed by the default
# attributestorage
LockerRegistrySchema['title'].storage = atapi.AnnotationStorage()

# Calling this re-orders a few fields to comply with Plone conventions.
finalizeATCTSchema(LockerRegistrySchema, folderish=True, moveDiscussion=False)





class LockerRange(object):
	"""
	>>> r = LockerRange(10, 20)
	>>> 10 in r
	True
	>>> 15 in r
	True
	>>> 20 in r
	True
	>>> 9 in r
	False
	>>> str(r)
	'10-20'
	"""
	def __init__(self, start, end):
		self.start = start
		self.end = end

	def __contains__(self, number):
		return number >= self.start and number <= self.end

	def __str__(self):
		return "%s-%s" % (self.start, self.end)


class LockerArea(object):
	"""
	>>> a = LockerArea('Area test', ['10-20', '30-40', '100-200'])
	>>> 10 in a
	True
	>>> 40 in a
	True
	>>> 35 in a
	True
	>>> 21 in a
	False
	>>> len([r for r in a])
	3
	>>> a.rangesToString()
	'10-20, 30-40, 100-200'
	>>> str(a)
	'Area test: 10-20, 30-40, 100-200'
	"""
	def __init__(self, label, ranges):
		self.ranges = []
		self.label = label
		for r in ranges:
			start, end = r.split("-")
			self.ranges.append(LockerRange(int(start), int(end)))

	def __contains__(self, number):
		for r in self.ranges:
			if number in r:
				return True
		return False

	def __iter__(self):
		return self.ranges.__iter__()

	def __str__(self):
		return u"%s: %s" % (self.label, self.rangesToString())

	def rangesToString(self):
		return ", ".join([str(x) for x in self.ranges])



class Lockerlist(object):
	"""
	>>> raw = ['Test one:1-2,10-20,1000-2000', 'Test two:30-40']
	>>> l = Lockerlist(raw)
	>>> 10 in l
	True
	>>> 20 in l
	True
	>>> 40 in l
	True
	>>> 35 in l
	True
	>>> 10000 in l
	False
	>>> len([a for a in l])
	2
	"""
	def __init__(self, lockerlist):
		self.areas = []
		for i in lockerlist:
			label, ranges = i.split(":")
			self.areas.append(LockerArea(label, ranges.split(",")))
	
	def __contains__(self, number):
		for a in self.areas:
			if number in a:
				return True
		return False

	def getArea(self, number):
		for a in self.areas:
			if number in a:
				return a
		return None

	def __iter__(self):
		return self.areas.__iter__()



class LockerRegistry(folder.ATFolder):
	""" Contains multiple locker reservations. """
	implements(ILockerRegistry)
	
	# The portal type name must be set here, matching the one in types.xml
	# in the GenericSetup profile
	portal_type = "LockerRegistry"
	
	# This enables Archetypes' standard title-to-id renaming machinery
	# If you need different semantics, it's possible to override the method
	# _renameAfterCreation() from BaseObject
	_at_rename_after_creation = True
	
	# We then associate the schema with our content type
	schema = LockerRegistrySchema

	def validate_masterlockers(self, lockerlist):
		for line in lockerlist:
			if not LOCKERLIST_PATT.match(line):
				return "Invalid locker line: %s. " \
						"Example of valid line: " \
						"'Example room:2000-3500,200-300'." % line
		return None

	def validate_bachelorlockers(self, lockerlist):
		return self.validate_masterlockers(lockerlist)

	def parseLockerlist(self, lockerlist):
		return Lockerlist(lockerlist)

	def getParsedMasterlockers(self):
		return self.parseLockerlist(self.getMasterlockers())

	def getParsedBachelorlockers(self):
		return self.parseLockerlist(self.getBachelorlockers())


# This line tells Archetypes about the content type
atapi.registerType(LockerRegistry, PROJECTNAME)
