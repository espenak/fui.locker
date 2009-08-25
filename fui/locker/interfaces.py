from zope.interface import Interface
from zope import schema

from zope.app.container.constraints import contains

from fui.locker import LockerMessageFactory as _


class ILockerRegistry(Interface):
	""" A locker registry """
	#contains()

	#title = schema.TextLine(title = _(u"Title"), required = True)

	#description = schema.TextLine(title = _(u"Description"),
	#		description = _(u"A short summary of this locker registry."))

	#text = schema.SourceText(title = _(u"Information"),
	#		description = _(u"Optional information about this locker registry."),
	#		required = False)


class ILockerReservation(Interface):
	""" A reserved locker in a locker registry.	"""
