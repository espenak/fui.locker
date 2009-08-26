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
from AccessControl.SecurityManagement import newSecurityManager, \
	getSecurityManager, setSecurityManager
from fui.locker.content import lockerreservation
from fui.locker import LockerMessageFactory as _
from fui.locker.interfaces import ILockerReservation
from plone.memoize.instance import memoize 



INFO_TPL = \
u"""Locker %(lockerid)d was successfully reserved for %(fullname)s (%(username)s).
This locker is only available to master students. If you are not a master student,
please visit the. FUI office for manual registration."""



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
	

FULLNAME_PATT = re.compile("(?:In real life|Name): (.+?)$")
def get_fullname(username):
	p = subprocess.Popen(["finger", username], stdout=subprocess.PIPE,
			stderr=subprocess.PIPE)
	for line in p.stdout:
		m = FULLNAME_PATT.search(line)
		if m:
			return m.group(1)
	raise ValueError("Could not find full name for user: %s." % username)


	



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



class LockerReservationForm(form.AddForm):
	form_fields = form.FormFields(ILockerReservationForm)
	template = ViewPageTemplateFile("lockerreservation_form.pt")

	@form.action("Register")
	def action_send(self, action, data):
		context = aq_inner(self.context)
		urltool = getToolByName(context, 'portal_url')
		portal = urltool.getPortalObject()


		##
		## Validate
		##
		username = data["username"]
		lockerid = data["lockerid"]
		try:
			try:
				lockerreservation.validate_lockerid(context,
						context.getParsedMasterlockers(), lockerid)
			except lockerreservation.LockerNotFoundError, e:
				# Only authenticated users can reserve bachelor lockers..
				lockerreservation.validate_lockerid(context,
						context.getParsedBachelorlockers(), lockerid)
				if context.portal_membership.isAnonymousUser():
					errormsg = u"The locker you selected, %d, is " \
							"only available to bachelor students. Please " \
							"select another locker, or visit the FUI office " \
							"to register a bachelor locker." % lockerid
					IStatusMessage(self.request).addStatusMessage(errormsg,
							type='error')
					return self.template()

			lockerreservation.validate_unique_username(context, username)
		except lockerreservation.LockerValidationError, e:
			IStatusMessage(self.request).addStatusMessage(unicode(e),
					type='error')
			return self.template()


		##
		## Save
		##

		# Elevate rights to allow anonymous users to add to the db
		securityManagerBackup = getSecurityManager()
		user = context.getWrappedOwner()
		newSecurityManager(context.REQUEST, user)

		try:
			# Create a new LockerReservation
			context.invokeFactory(
					type_name = "LockerReservation",
					id = username)
			r = context[username]
			r.setLockerid(lockerid)
			r.setTitle(username)
			r.setExcludeFromNav(True)
		finally:
			# Reset secutitymanager to clear elevated rights
			setSecurityManager(securityManagerBackup)

		fullname = get_fullname(username)
		info = INFO_TPL % locals()


		##
		## Email notification
		##
		if context.getEmailnotification():
			email_charset = portal.getProperty('email_charset')
			to_address = "%s@ulrik.uio.no" % username
			from_address = portal.getProperty('email_from_address')
			subject = context.Title()
			message = context.getEmailcontent() % dict(
					username=username, lockerid=lockerid,
					fullname=fullname)

			context.MailHost.secureSend(
					message, to_address, from_address,
					subject = subject,
					charset = email_charset,
					debug = False,
					From = from_address)

			info += " A confirmation mail has been sent to your UiO email address."




		##	
		## This status message is displayed at the top of the
		## page where the user is redirected.
		##
		IStatusMessage(self.request).addStatusMessage(info, type='info')
		
		self.request.response.redirect(context.absolute_url()) 
		return ''
