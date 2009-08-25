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



RANGE_DESCRIPTION = u"""One locker per line. Each line must contain two
numbers separated by '-'. The numbers define a valid locker-number range.
Example line: 1000-2999. This line will make any number between 1000 and 2999,
including the two numbers, a valid locker number. You can define as many ranges
as you like, each on a separate line."""

LOCKERLIST_PATT = re.compile("^\d+-\d+$")


# This is the Archetypes schema, defining fields and widgets. We extend
# the one from ATContentType's ATFolder with our additional fields.
LockerRegistrySchema = folder.ATFolderSchema.copy() + atapi.Schema((
	atapi.LinesField("masterlockers",
		required = True,
		searchable = False,
		storage = atapi.AnnotationStorage(),
		widget = atapi.LinesWidget(
				label = u"Lockers available to master students",
				description = RANGE_DESCRIPTION)
		),

	atapi.LinesField("bachelorlockers",
		required = True,
		searchable = False,
		storage = atapi.AnnotationStorage(),
		widget = atapi.LinesWidget(
				label = u"Lockers available to bachelor students",
				description = RANGE_DESCRIPTION)
		),

	atapi.TextField("text",
		required=False,
		searchable=True,
		storage=atapi.AnnotationStorage(),
		validators=('isTidyHtmlWithCleanup',),
		default_output_type='text/x-html-safe',
		widget=atapi.RichWidget(
				label = _(u"Descriptive text"),
				description = _(u""),
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
				return "Invalid number-range: %s. " \
						"Example of valid range: 2000-3500." % line
		return None

	def validate_bachelorlockers(self, lockerlist):
		return self.validate_masterlockers(lockerlist)
	


# This line tells Archetypes about the content type
atapi.registerType(LockerRegistry, PROJECTNAME)
