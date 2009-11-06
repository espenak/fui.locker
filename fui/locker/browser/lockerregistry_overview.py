from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from fui.locker.interfaces import ILockerRegistry, ILockerReservation

from plone.memoize.instance import memoize 



class LockerRegistryOverview(BrowserView):
	__call__ = ViewPageTemplateFile('lockerregistry_overview.pt')


	def __init__(self, *args, **kwargs):
		BrowserView.__init__(self, *args, **kwargs)
		context = aq_inner(self.context)



	#@memoize
	def getReservations(self, lockerlist):
		""" Get a list of LockerReservation objects with lockerid
		in lockerlist. The list is sorted by lockerid. """
		context = aq_inner(self.context)

		r = []
		for id, item in context.objectItems():
			area = lockerlist.getArea(item.getLockerid())
			if area:
				url = "/".join(item.getPhysicalPath())
				r.append(dict(
					editurl = "%s/edit" % url,
					deleteurl = "%s/delete_confirmation" % url,
					username = item.Title(),
					email = "%s@ulrik.uio.no" % item.Title(),
					area = area,
					lockerid = item.getLockerid()))
		return r


		def compare(a, b):
			return cmp(a["lockerid"], b["lockerid"])
		r.sort(compare)
		return r

	def getUniqueMasterUsernames(self):
		return set([x["username"] for x in self.getMasterReservations()])

	def getUniqueBachelorUsernames(self):
		return set([x["username"] for x in self.getBachelorReservations()])

	def getMasterReservations(self):
		context = aq_inner(self.context)
		return self.getReservations(context.getParsedMasterlockers())

	def getBachelorReservations(self):
		context = aq_inner(self.context)
		return self.getReservations(context.getParsedBachelorlockers())	
