# Zope3 imports
from zope.interface import implements

# CMF imports
from Products.CMFCore import permissions

# Archetypes & ATCT imports
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# Product imports
from fui.locker import config
from fui.locker.interfaces import ILockerReservation
from fui.locker import LockerMessageFactory as _



USERNAME_TITLE = u"UiO username"
USERNAME_DESCRIPTION = u"Must be a valid UiO username."
LOCKERID_TITLE = u"Locker id"
LOCKERID_DESCRIPTION = u"The id/number of the locker."


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



class LockerReservation(base.ATCTContent):
	"""An Archetype for a LockerReservation, """
	implements(ILockerReservation)
	schema = schema


	#def validate_lockerid(self, value):
	#	if value < 1000 or value > 3999:
	#		return "Crap!"
	#	return None


# Content type registration for the Archetypes machinery
atapi.registerType(LockerReservation, config.PROJECTNAME)
