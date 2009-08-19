"""Define a browser view for the LockerRegister content type. In the FTI 
configured in profiles/default/types/*.xml, this is being set as the default
view of that content type.
"""

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from fui.locker.interfaces import ILockerRegister

from plone.memoize.instance import memoize 

class LockerRegisterView(BrowserView):
	"""Default view of a register folder
	"""
	
	# This template will be used to render the view. An implicit variable
	# 'view' will be available in this template, referring to an instance
	# of this class. The variable 'context' will refer to the register folder
	# being rendered.
	
	__call__ = ViewPageTemplateFile('lockerregister.pt')
	
	# Methods called from the associated template
	
	def have_locker_registers(self):
		return len(self.locker_registers()) > 0
	
	# The memoize decorator means that the function will be executed only
	# once (for a given set of arguments, but in this case there are no
	# arguments). On subsequent calls, the return value is looked up from a
	# cache, meaning we can call this function several times without a 
	# performance hit.
	
	@memoize
	def locker_registers(self):
		context = aq_inner(self.context)
		catalog = getToolByName(context, 'portal_catalog')
		return [ dict(url=locker_register.getURL(),
					  title=locker_register.Title,
					  description=locker_register.Description,)
				 for locker_register in 
					catalog(object_provides=ILockerRegister.__identifier__,
							path=dict(query='/'.join(context.getPhysicalPath()),
									  depth=1),
							sort_on='sortable_title')
			]
	
	def have_registers(self):
		return len(self.registers()) > 0
	
	@memoize
	def registers(self):
		context = aq_inner(self.context)
		catalog = getToolByName(context, 'portal_catalog')
		
		# Note that we are cheating a bit here - to avoid having to "wake up"
		# the register object, we rely on our implementation that uses the 
		# Dublin Core Title and Description fields as title and address,
		# respectively. To rely only on the interface and not the 
		# implementation, we'd need to call getObject() and then use the
		# associated attributes of the interface, or we could add new catalog
		# metadata for these fields (with a catalog.xml GenericSetup file).

		return []

