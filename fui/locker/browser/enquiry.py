import re 
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
from fui.locker import LockerMessageFactory as _ 


# Define a validation method for email addresses 
class NotAnEmailAddress(schema.ValidationError): 
	__doc__ = _(u"Invalid email address") 

check_email = re.compile( 
			r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}").match 


def validate_email(value): 
	if not check_email(value): 
		raise NotAnEmailAddress(value) 
	return True

MESSAGE_TEMPLATE = """\ 
Enquiry from: %(name)s <%(email_address)s> 
%(message)s 
""" 

class IEnquiryForm(Interface): 
	username = schema.TextLine(
			title = _(u"Your name"),
			required = True)
	lockerid = schema.TextLine(
			title = _(u"Locker id"),
			description = _(u"The id/number of the locker."),
			required = True)


class EnquiryForm(formbase.PageForm): 
	form_fields = form.FormFields(IEnquiryForm) 
	label = _(u"Make an enquiry") 
	description = _(u"Got a question or comment? Please submit it using the form below!")

	# This trick hides the editable border and tabs in Plone 
	def __call__(self): 
		return super(EnquiryForm, self).__call__() 

	@form.action(_(u"Send")) 
	def action_send(self, action, data): 
		context = aq_inner(self.context)
		print "###################################################"
		print dir(context)
		print "###################################################"
		context.invokeFactory(
				type_name = "LockerReservation",
				id = "test")
		urltool = getToolByName(context, 'portal_url')
		self.request.response.redirect(urltool.getPortalObject().absolute_url()) 
		return '' 
