import re, subprocess

from zope.interface import implements
from Products.CMFCore import permissions
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata
from plone.memoize.instance import memoize 

from fui.locker import config
from fui.locker.interfaces import ILockerReservation
from fui.locker import LockerMessageFactory as _



USERNAME_TITLE = u"UiO username"
USERNAME_DESCRIPTION = u"Must be a valid UiO username."
LOCKERID_TITLE = u"Locker id"
LOCKERID_DESCRIPTION = u"The id/number of the locker."

ALREADY_RESERVER_MSG = \
u"""There is already a locker reserved by the '%s' user. If this is your
username, and you have not reserved a locker this semester, or you wish to
reserve more than one locker, contact FUI."""

# Schema definition
# http://api.plone.org/Archetypes/1.5.0/public/frames/products/Archetypes/index.html
# http://api.plone.org/Archetypes/1.5.0/public/frames/products/Archetypes/products.Archetypes.Widget-module.html
# http://plone.org/products/archetypes/documentation/old/arch_widget_quickref_1_3_1/
schema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
	atapi.IntegerField("lockerid",
		required = True,
		searchable = True,
		widget = atapi.IntegerWidget(
			label = LOCKERID_TITLE,
			description = LOCKERID_DESCRIPTION),
		),
))

# Just reuse the 'title' field for the username
schema['title'].storage = atapi.AnnotationStorage()
schema['title'].widget.label = USERNAME_TITLE
schema['title'].widget.description = USERNAME_DESCRIPTION

# Remove the "description" inherited from ATContentTypeSchema
del schema["description"]



class LockerValidationError(Exception):
	""" Base class for validation errors. """

class LockerNotFoundError(LockerValidationError):
	""" Base class for validation errors. """


def validate_lockerid(context, lockerlist, lockerid, edit_id=None):
	""" Validates a lockernumber against a Lockerlist and check that the
	lockerid is unique.

	>>> from fui.locker.content.lockerreservation import validate_lockerid
	>>> from fui.locker.content.lockerregistry import Lockerlist
	>>> lockerlist = Lockerlist(['Test:10-20'])

	>>> reg = self.folder.registry
	>>> validate_lockerid(reg, lockerlist, 11)
	>>> validate_lockerid(reg, lockerlist, "11")

	>>> validate_lockerid(reg, lockerlist, "a")
	Traceback (most recent call last):
	...
	LockerValidationError: ...

	>>> validate_lockerid(reg, lockerlist, 10, reg.reserv1.getId())
	>>> validate_lockerid(reg, lockerlist, 10)
	Traceback (most recent call last):
	...
	LockerValidationError: ...
	"""
	if not isinstance(lockerid, int):
		if not lockerid.isdigit():
			raise LockerValidationError("Locker id must be a number.")
		lockerid = int(lockerid)

	if not lockerid in lockerlist:
		raise LockerNotFoundError(
				u"There is no locker with the requested number (%d)." % lockerid )

	for id, item in context.objectItems():
		if edit_id != id and item.getLockerid() == lockerid:
			raise LockerValidationError(
				u"The requested locker, %s, is already reserved by " \
				"someone else." % item.getLockerid())


def validate_unique_username(context, username, edit_id=None):
	""" Check that username is unique.
	
	>>> r = self.folder.registry.reserv1
	>>> r.setTitle("test")

	>>> from fui.locker.content.lockerreservation import validate_unique_username
	>>> validate_unique_username(self.folder.registry, "a")

	>>> validate_unique_username(self.folder.registry, "test", r.getId())
	>>> validate_unique_username(self.folder.registry, "test")
	Traceback (most recent call last):
	...
	LockerValidationError: ...
	"""
	for id, item in context.objectItems():
		if edit_id != id and item.Title() == username:
			raise LockerValidationError(
					ALREADY_RESERVER_MSG % username)

INVALID_USERNAME = u"Invalid UiO username"
USERNAME_PATT = re.compile(u"^[a-z]+$")
def validate_username(username):
	""" Validates that the username is a lowercase english word,
	and that the 'id' command returns 0 when called with the username.
	
	>>> from fui.locker.content.lockerreservation import validate_username
	>>> import os
	>>> username = os.environ["USER"]
	>>> validate_username(username)

	>>> validate_username("hopefullynosuchuser")
	Traceback (most recent call last):
	...
	LockerValidationError: ...

	>>> validate_username("123")
	Traceback (most recent call last):
	...
	LockerValidationError: ...
	"""
	if not USERNAME_PATT.match(username):
		raise LockerValidationError(INVALID_USERNAME)
	retcode = subprocess.call(["id", username], stdout=subprocess.PIPE,
			stderr=subprocess.PIPE)
	if not retcode == 0:
		raise LockerValidationError(INVALID_USERNAME)


class LockerReservation(base.ATCTContent):
	"""An Archetype for a LockerReservation, """
	implements(ILockerReservation)
	schema = schema

	def validate_lockerid(self, lockerid):
		parent = self.aq_inner.aq_parent
		masterlockers = parent.getParsedMasterlockers()
		try:
			validate_lockerid(parent, masterlockers, lockerid, self.getId())
		except LockerValidationError, e:
			bachelorlockers = parent.getParsedBachelorlockers()
			try:
				validate_lockerid(parent, bachelorlockers, lockerid, self.getId())
			except LockerValidationError, e:
				return unicode(e)
		return None

	def validate_title(self, username):
		parent = self.aq_inner.aq_parent
		try:
			validate_username(username)
			validate_unique_username(parent, username, self.getId())
		except LockerValidationError, e:
			return unicode(e)
		return None


# Content type registration for the Archetypes machinery
atapi.registerType(LockerReservation, config.PROJECTNAME)
