# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Carlos Jenkins <carlos@jenkins.co.cr>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Improved l10n Python Module.
"""

# Python 2.7 - Python 3 base compatibility
from __future__ import unicode_literals
from __future__ import absolute_import

import os
import sys
import logging

log = logging.getLogger(__name__)

__version__ = '0.1.0'


def _(msg):
    """
    Temporal but valid translation function.
    """
    log.warning('_({}) called before configuring l10n'.format(msg))
    return msg


def find_localedir(localedir):
    """
    Custom function to find the locales message catalog in a multi-platform
    application.
    """
    import sys
    import os

    if localedir is None:
        if sys.platform.startswith('linux'):
            import gettext
            return gettext.bindtextdomain('messages')

        return find_localedir('locale')

    if os.path.isabs(localedir):
        return localedir

    def parent(path):
        return os.path.normpath(
            os.path.dirname(os.path.abspath(os.path.realpath(path)))
        )

    if sys.platform.startswith('win') and \
       getattr(sys, 'frozen', '') in ('dll', 'console_exe', 'windows_exe'):
        root = parent(sys.executable)
    else:
        import inspect
        root = parent(inspect.getfile(inspect.stack()[-1][0]))

    return os.path.join(root, localedir)


def l10n(domain=None, localedir=None):
    """
    Setup localization.

    :param str domain: The name of the translation domain (your application
     name). If None is provided (the default) the default domain is used as
     determined by gettext.textdomain() which usually is `messages`.

    :param str localedir: Path to the location of the binary `.mo` messages.

     Lookup path will then be `[prefix]/[locale]/LC_MESSAGES/[domain].mo`.

     The prefix will be determined as follow:

     1. If `localedir` is an absolute path as determined by
        :py:func:`os.path.isabs` then use the path as prefix for the lookup.

     2. If `localedir` is a relative path then determine the prefix as follow:

        1. If on Windows and in a freezed environment:

           `dirname([sys.executable])` + prefix

        2. Anything else:

           `dirname([calling_script])` + prefix

           Where `calling_script` is determined by inspecting the stack and
           retrieving the location of the calling script.

     3. If `localedir` is `None` (the default), then use the default system
        locale directory.

        1. On Linux:

           `[sys.prefix]/share/locale`

        2. Anything else, like Windows, which doesn't have a default folder,
           same as calling with `localedir` as a relative path `locale`.
    """
    import locale
    import traceback

    # Set LANG environment variable if unset
    # This is required by the gettext module to work on Windows
    os_windows = sys.platform.startswith('win')
    if os_windows:
        if os.getenv('LANG') is None:
            lang, enc = locale.getdefaultlocale()
            os.environ['LANG'] = lang

    # Set locale
    try:
        current = locale.setlocale(locale.LC_ALL, '')
        log.info('Locale set to {}'.format(current))
    except Exception:
        log.error('Unable to set user locale')
        log.error(traceback.format_exc())
        return _

    # Determine text domain and localedir
    import gettext

    if domain is None:
        domain = gettext.textdomain()

    localedir = find_localedir(localedir)

    # List modules to call
    modules = []
    if os_windows:
        try:
            import ctypes
            if not hasattr(l10n, 'libintl'):
                l10n.libintl = ctypes.cdll.LoadLibrary('intl.dll')
            modules.append(l10n.libintl)
        except Exception:
            log.error('Unable to load libintl')
            log.error(traceback.format_exc())
    modules.append(locale)
    modules.append(gettext)

    for module in modules:
        try:
            if hasattr(module, 'bindtextdomain'):
                module.bindtextdomain(domain, localedir)
            # Not sure about this call and encoding
            # Also, should we set the encoding here or just use lgettext
            # if hasattr(module, 'bind_textdomain_codeset'):
            #     module.bind_textdomain_codeset(domain, 'UTF-8')
            if hasattr(module, 'textdomain'):
                module.textdomain(domain)
        except Exception:
            log.error('Unable to bind text domain in module {}'.format(module))
            log.error(traceback.format_exc())

    global _
    _ = gettext.gettext

    return gettext.gettext


__all__ = ['_', 'l10n']
