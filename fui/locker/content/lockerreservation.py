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

# Schema definition
# http://api.plone.org/Archetypes/1.5.0/public/frames/products/Archetypes/index.html
# http://api.plone.org/Archetypes/1.5.0/public/frames/products/Archetypes/products.Archetypes.Widget-module.html
# http://plone.org/products/archetypes/documentation/old/arch_widget_quickref_1_3_1/
schema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
	atapi.StringField("lockerid",
		required = True,
		searchable = True,
		widget = atapi.StringWidget(
			label = _(u'Locker Id'),
			description = _(u"The unique number or combination of " +
					"letters identifying the locker.")),
		),

	atapi.StringField("confirmkey",
		required = True,
		searchable = True,
		widget = atapi.StringWidget(
			label = _(u'Confirmation key'),
			description = _(u"The key required to confirm this "+
				"locker reservation by email.")),
		),

	atapi.BooleanField("confirmed",
		required = True,
		searchable = True,
		widget = atapi.BooleanWidget(
			label = _(u'Confirmed by email?'),
			description = _(u"Have this reservation.been confirmed "+
				"by email?")),
		),
))

# Just reuse the 'title' field for the username
schema['title'].storage = atapi.AnnotationStorage()
schema['title'].widget.label = _(u'Username')
schema['title'].widget.description = _(u"Your UiO username.")

# Remove the "description" inherited from ATContentTypeSchema
del schema["description"]


class LockerReservation(base.ATCTContent):
	"""An Archetype for a LockerReservation, """
	implements(ILockerReservation)
	schema = schema


# Content type registration for the Archetypes machinery
atapi.registerType(LockerReservation, config.PROJECTNAME)
