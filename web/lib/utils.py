#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ***** BEGIN LICENSE BLOCK *****
# This file is part of LPS - Abstraction Layer.
# Copyright (c) 2015-2016 Luxembourg Institute of Science and Technology.
# All rights reserved.
#
#
#
# ***** END LICENSE BLOCK *****

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2016/03/01$"
__revision__ = "$Date: 2016/03/01 $"
__copyright__ = "Copyright (c) Luxembourg Institute of Science and Technology"
__license__ = ""

from flask import request
try:
    from urlparse import urlparse, parse_qs, urljoin
except:
    from urllib.parse import urlparse, parse_qs, urljoin

def is_safe_url(target):
    """
    Ensures that a redirect target will lead to the same server.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    """
    Looks at various hints to find the redirect target.
    """
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target
