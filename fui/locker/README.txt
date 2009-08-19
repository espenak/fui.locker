========================
 Optilux Cinema content
========================

This package contains content types that pertain to the Optilux Cinema
application. In this testbrowser doctest, we will demonstrate how the content 
types interact. See tests/test_doctest.py for how it is set up.

Setting up and logging in
-------------------------

We use zope.testbrowser to simulate browser interaction in order to show
the main flow of pages. This is not a true functional test, because we also
inspect and modify the internal state of the ZODB, but it is a useful way of
making sure we test the full end-to-end process of creating and modifying
content.

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> portal_url = self.portal.absolute_url()

The following is useful when writing and debugging testbrowser tests. It lets
us see error messages properly.

    >>> browser.handleErrors = False
    >>> self.portal.error_log._ignored_exceptions = ()

We then turn off the various portlets, because they sometimes duplicate links
and text (e.g. the navtree, the recent recent items listing) that we wish to
test for in our own views. Having no portlets makes things easier.

    >>> from zope.component import getUtility, getMultiAdapter
    >>> from plone.portlets.interfaces import IPortletManager
    >>> from plone.portlets.interfaces import IPortletAssignmentMapping

    >>> left_column = getUtility(IPortletManager, name=u"plone.leftcolumn")
    >>> left_assignable = getMultiAdapter((self.portal, left_column), IPortletAssignmentMapping)
    >>> for name in left_assignable.keys():
    ...     del left_assignable[name]

    >>> right_column = getUtility(IPortletManager, name=u"plone.rightcolumn")
    >>> right_assignable = getMultiAdapter((self.portal, right_column), IPortletAssignmentMapping)
    >>> for name in right_assignable.keys():
    ...     del right_assignable[name]

Finally, we need to log in as the portal owner, i.e. an administrator user. We
do this from the login page.

    >>> from Products.PloneTestCase.setup import portal_owner, default_password

    >>> browser.open(portal_url + '/login_form?came_from=' + portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

Addable content
---------------

Cinema content is managed inside two root content types: A "Cinema Folder"
contains cinemas and information about them. A "Film Folder" contains films.

    >>> browser.open(portal_url)

Verify that we have the links to create cinema and film folders, from the add
item menu:

    >>> browser.getLink(id='cinema-folder').url.endswith("createObject?type_name=Cinema+Folder")
    True
    

Adding cinema folders and cinemas
---------------------------------
    
Let us now add a cinema folder and some cinemas. The cinema folder
can contain a rich-text description of the cinema folder (e.g. of a group
of cinemas), which will be displayed on the front page of that folder. 

    >>> browser.open(portal_url)
    >>> browser.getLink(id='cinema-folder').click()
    >>> browser.getControl(name='title').value = "Cinemas"
    >>> browser.getControl(name='text').value = "<b>About this cinema</b>"
    >>> browser.getControl(name='form_submit').click()

This should have added an object called 'cinemas' in the portal root, invoking
the title-to-id renaming.

    >>> 'cinemas' in self.portal.objectIds()
    True
    >>> cinemas = self.portal['cinemas']
    >>> cinemas.title
    'Cinemas'
    >>> cinemas.text
    '<b>About this cinema</b>'

    >>> cinemas_url = cinemas.absolute_url()
