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
schema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

	atapi.TextField('username',
			required = True,
			searchable = True,
			storage = atapi.AnnotationStorage(),
			widget = atapi.StringWidget(label = _(u'UiO username')),
		),

	atapi.TextField('locker_id',
			required = True,
			searchable = True,
			storage = atapi.AnnotationStorage(),
			description = _(u"The unique number or combination of letters " +
				 "identifying the locker."),
			widget = atapi.StringWidget(label = _(u'Locker Id')),
		),
))


class LockerReservation(base.ATCTContent):
    """An Archetype for a LockerReservation, """
    implements(ILockerReservation)
    schema = schema
    
# Content type registration for the Archetypes machinery
atapi.registerType(LockerReservation, config.PROJECTNAME)
