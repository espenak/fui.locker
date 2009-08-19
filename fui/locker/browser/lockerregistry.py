"""Define a browser view for the LockerRegistry content type. In the FTI 
configured in profiles/default/types/*.xml, this is being set as the default
view of that content type.
"""

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from fui.locker.interfaces import ILockerRegistry

from plone.memoize.instance import memoize 

class LockerRegistryView(BrowserView):
	"""Default view of a registry folder
	"""
	
	# This template will be used to render the view. An implicit variable
	# 'view' will be available in this template, referring to an instance
	# of this class. The variable 'context' will refer to the registry folder
	# being rendered.
	
	__call__ = ViewPageTemplateFile('lockerregistry.pt')
	
	# Methods called from the associated template
	
	def have_locker_registries(self):
		return len(self.locker_registries()) > 0
	
	# The memoize decorator means that the function will be executed only
	# once (for a given set of arguments, but in this case there are no
	# arguments). On subsequent calls, the return value is looked up from a
	# cache, meaning we can call this function several times without a 
	# performance hit.
	
	@memoize
	def locker_registries(self):
		context = aq_inner(self.context)
		catalog = getToolByName(context, 'portal_catalog')
		return [ dict(url=locker_registry.getURL(),
					  title=locker_registry.Title,
					  description=locker_registry.Description,)
				 for locker_registry in 
					catalog(object_provides=ILockerRegistry.__identifier__,
							path=dict(query='/'.join(context.getPhysicalPath()),
									  depth=1),
							sort_on='sortable_title')
			]
	
	def have_registries(self):
		return len(self.registries()) > 0
	
	@memoize
	def registries(self):
		context = aq_inner(self.context)
		catalog = getToolByName(context, 'portal_catalog')
		
		# Note that we are cheating a bit here - to avoid having to "wake up"
		# the registry object, we rely on our implementation that uses the 
		# Dublin Core Title and Description fields as title and address,
		# respectively. To rely only on the interface and not the 
		# implementation, we'd need to call getObject() and then use the
		# associated attributes of the interface, or we could add new catalog
		# metadata for these fields (with a catalog.xml GenericSetup file).

		return []

