from zope.interface import Interface
from zope import schema

from zope.app.container.constraints import contains

from fui.locker import LockerMessageFactory as _


class ILockerRegister(Interface):
	""" A locker register """
	contains()

	title = schema.TextLine(title = _(u"Title"), required = True)

	description = schema.TextLine(title = _(u"Description"),
			description = _(u"A short summary of this locker register."))

	text = schema.SourceText(title = _(u"Information"),
			description = _(u"Optional information about this locker register."),
			required = False)
