from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from fui.locker.interfaces import ILockerRegistry, ILockerReservation

from plone.memoize.instance import memoize 



class LockerRegistryList(BrowserView):
	""" Default view of a registry folder """
	
	__call__ = ViewPageTemplateFile('lockerregistry_overview.pt')


	def __init__(self, *args, **kwargs):
		BrowserView.__init__(self, *args, **kwargs)
		context = aq_inner(self.context)



	#@memoize
	def getReservations(self, lockerlist):
		""" Get a list of LockerReservation objects with lockerid
		in lockerlist. The list is sorted by lockerid. """
		context = aq_inner(self.context)

		r = [
			dict(
				viewurl = "/".join(item.getPhysicalPath()),
				editurl = "%s/edit" % "/".join(item.getPhysicalPath()),
				username = item.Title(),
				email = "%s@ulrik.uio.no" % item.Title(),
				lockerid = item.getLockerid())
			for id, item in context.objectItems()
			if item.getLockerid() in lockerlist]

		def compare(a, b):
			return cmp(a["lockerid"], b["lockerid"])
		r.sort(compare)
		return r


	def getMasterReservations(self):
		context = aq_inner(self.context)
		return self.getReservations(context.getParsedMasterlockers())

	def getBachelorReservations(self):
		context = aq_inner(self.context)
		return self.getReservations(context.getParsedBachelorlockers())	
