__version__ = '0.8-alpha'
__author__ = 'Dan Persons <dpersonsdev@gmail.com>'
__license__ = 'MIT License'
__github__ = 'https://github.com/dogoncouch/siemcli'
__all__ = ['parsecore', 'parse', 'querycore', 'query', 'triggercore',
        'trigger', 'managecore', 'manage', 'util']

import siemcli.parse
import siemcli.query
import siemcli.trigger
import siemcli.manage
import siemcli.util
