import re, subprocess

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
from fui.locker.content import lockerreservation
from fui.locker import LockerMessageFactory as _
from fui.locker.interfaces import ILockerReservation
from plone.memoize.instance import memoize 


class InvalidUioUsernameError(schema.ValidationError): 
	__doc__ = u"Invalid UiO username"

USERNAME_PATT = re.compile(u"^[a-z]+$")
def validate_username(value):
	""" Validates that the username is a lowercase english word. """
	if not USERNAME_PATT.match(value):
		raise InvalidUioUsernameError(value)

	retcode = subprocess.call(["id", value], stdout=subprocess.PIPE,
			stderr=subprocess.PIPE)
	if not retcode == 0:
		raise InvalidUioUsernameError(value)
	return True
	


class ILockerReservationForm(Interface):
	""" A reserved locker in a locker registry.	"""
	username = schema.ASCIILine(
			title = lockerreservation.USERNAME_TITLE,
			description = lockerreservation.USERNAME_DESCRIPTION,
			required = True,
			constraint = validate_username)
	lockerid = schema.Int(
			title = lockerreservation.LOCKERID_TITLE,
			description = lockerreservation.LOCKERID_DESCRIPTION,
			required = True)



class LockerReservationForm(formbase.PageForm):
	form_fields = form.FormFields(ILockerReservationForm)
	result_template = ViewPageTemplateFile('lockerreservation_form_result.pt')
	error_template = ViewPageTemplateFile('lockerreservation_form_error.pt')

	# This trick hides the editable border and tabs in Plone
	def __call__(self):
		return super(LockerReservationForm, self).__call__()

	@form.action("save")
	def action_send(self, action, data):
		context = aq_inner(self.context)

		# Get input data
		username = data["username"]
		lockerid = data["lockerid"]

		# Validate
		masterlockers = context.getMasterlockers()
		try:
			lockerreservation.validate_lockerid(context, masterlockers, lockerid)
			lockerreservation.validate_unique_username(context, username)
		except lockerreservation.LockerValidationError, e:
			self.errormsg = unicode(e)
			return self.error_template()

		# Elevate rights to allow anonymous users to add to the db
		user = context.getWrappedOwner()
		newSecurityManager(context.REQUEST, user)

		# Create a new LockerReservation
		context.invokeFactory(
				type_name = "LockerReservation",
				id = username)
		r = context[username]
		r.setLockerid(lockerid)
		r.setTitle(username)

		# Clear elevated rights
		# This makes it appear like authenticated users are logged out,
		# but they are not!
		noSecurityManager()

		# Set some template variables and show the "success" template
		self.username = username
		self.lockerid = lockerid
		return self.result_template()
