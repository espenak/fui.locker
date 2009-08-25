from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from fui.locker.interfaces import ILockerRegistry, ILockerReservation

from plone.memoize.instance import memoize 

class LockerRegistryList(BrowserView):
	""" Default view of a registry folder """
	
	__call__ = ViewPageTemplateFile('lockerregistry_list.pt')
	
	# The memoize decorator means that the function will be executed only
	# once (for a given set of arguments, but in this case there are no
	# arguments). On subsequent calls, the return value is looked up from a
	# cache, meaning we can call this function several times without a 
	# performance hit.
	
	@memoize
	def locker_reservations(self):
		context = aq_inner(self.context)
		return [
			dict(url = "/".join(item.getPhysicalPath()),
				title = item.Title(),
				lockerid = item.getLockerid())
			for id, item in context.objectItems()]
