
"""
Siemcli
----------

Siemcli is a foundational Security Information and Event Management (SIEM) system. It includes three primary command-line tools:

siemcli: Parses security events and stores them in a database.
siemquery: Enables querying and analyzing data from the database.
siemtrigger: Triggers alerts and SIEM events based on insights derived from database analysis.

"""

from setuptools import setup
from os.path import join
from sys import prefix
from siemcli import __version__

ourdata = [(join(prefix, 'share/man/man1'),
        ['doc/siemparse.1', 'doc/siemquery.1', 'doc/siemtrigger.1',
            'doc/siemmanage.1']),
        (join(prefix, 'share/man/man7'), ['doc/siemcli.7']),
        (join(prefix, '/etc/siemcli'),
            ['config/db.conf', 'config/sections.conf']),
        (join(prefix, 'share/doc/siemcli'), ['README.md', 'LICENSE',
            'CHANGELOG.md', 'config/example_rules.json',
            'config/example_helpers.json'])]

setup(name = 'siemcli', version = str(__version__),
        description = 'A very basic Security Information and Event Management system (SIEM)',
        long_description = __doc__,
        author = 'Dan Persons', author_email = 'dpersonsdev@gmail.com',
        url = 'https://github.com/dogoncouch/siemcli',
        download_url = 'https://github.com/dogoncouch/siemcli/archive/v' + str(__version__) + '.tar.gz',
        keywords = ['log', 'syslog', 'analysis', 'forensics', 'security',
            'cli', 'secops', 'sysadmin', 'forensic-analysis',
            'log-analysis', 'log-analyzer', 'log-viewer', 'log-analytics',
            'log-management', 'log-collector', 'log-monitoring'],
        packages = ['siemcli'],
        entry_points = \
                { 'console_scripts': [ 'siemparse = siemcli.parsecore:main',
                    'siemquery = siemcli.querycore:main',
                    'siemtrigger = siemcli.triggercore:main',
                    'siemmanage = siemcli.managecore:main' ]},
        data_files = ourdata,
        classifiers = ["Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: System Administrators",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 2",
            "Topic :: System :: Monitoring"])
