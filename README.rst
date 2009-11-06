===============================================================================
README
===============================================================================

Plone product locker registration made spesifically to suite the needs of
*Fagutvalget ved Institutt for informatikk* (http://fui.ifi.uio.no).
The product is available at these addresses:

    - http://pypi.python.org/pypi/fui.locker/
    - http://github.com/espenak/fui.locker/


Install
-------

You can install this product in Plone using buildout.

    1. Add ``plonetheme.fui`` to ``buildout.cfg``::

        [buildout]
        ...
        eggs =
            ...
            fui.locker

        [instance]
        ...
        zcml = 
            ...
            fui.locker

    2. Run (maybe backup first..)::

        ~$ buildout -N

    3. Install the plugin using *Site Setup* in your Plone site.




For developers
--------------

Release a new version to pypi.python.org with::

    ~$ python setup.py register
    ~$ python setup.py egg_info -RDb "" sdist upload
