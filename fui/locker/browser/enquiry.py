import re 
from random import randint

from zope.interface import Interface 
from zope import schema 
from zope.formlib import form 
from Products.Five.formlib import formbase 
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile 
from Products.CMFCore.interfaces import IURLTool 
from Products.MailHost.interfaces import IMailHost 
from Products.statusmessages.interfaces import IStatusMessage 
from Acquisition import aq_inner 
from Products.CMFCore.utils import getToolByName 
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager

from fui.locker import LockerMessageFactory as _ 





class IForm(Interface):
	""" A reserved locker in a locker registry.	"""
	username = schema.TextLine(
			title = _(u"UiO username"),
			description = _(u"Your UiO username. A confirmation email " +
				"is sent to your UiO mail."),
			required = True)
	lockerid = schema.TextLine(
			title = _(u"Locker id"),
			description = _(u"The id/number of the locker."),
			required = True)


class EnquiryForm(formbase.PageForm): 
	form_fields = form.FormFields(IForm)

	# This trick hides the editable border and tabs in Plone 
	def __call__(self): 
		return super(EnquiryForm, self).__call__() 

	@form.action(_(u"Send")) 
	def action_send(self, action, data): 
		context = aq_inner(self.context)

		# Elevate rights to allow anonymous users to add to the db
		user = context.getWrappedOwner()
		newSecurityManager(None, user)

		# Create a new LockerReservation
		id = data["username"]
		context.invokeFactory(
				type_name = "LockerReservation",
				id = id)
		r = context[id]
		r.setLockerid(data["lockerid"])
		r.setTitle(id)
		r.setConfirmkey(str(randint(50, 1000000000)))
		r.setConfirmed(False)

		# Clear elevated rights
		noSecurityManager()

		# Redirect to frontpage
		urltool = getToolByName(context, 'portal_url')
		self.request.response.redirect(urltool.getPortalObject().absolute_url()) 
		return ''
