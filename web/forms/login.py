#! /usr/bin/env python
#-*- coding: utf-8 -*-

# ***** BEGIN LICENSE BLOCK *****
# This file is part of Shelter Database.
# Copyright (c) 2016
# All rights reserved.
#
#
#
# ***** END LICENSE BLOCK *****

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.1 $"
__date__ = "$Date: 2016/03/30$"
__revision__ = "$Date: 2016/03/30 $"
__copyright__ = "Copyright (c) "
__license__ = ""

from flask_wtf import Form
from flask import url_for, redirect
from wtforms import validators, TextField, PasswordField, BooleanField, \
                    SubmitField, HiddenField

from web.models import User
from web.lib import utils

class RedirectForm(Form):
    """
    Secure back redirects with WTForms.
    """
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = utils.get_redirect_target() or ''

    def redirect(self, endpoint='start', **values):
        if utils.is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = utils.get_redirect_target()
        return redirect(target or url_for(endpoint, **values))

class LoginForm(RedirectForm):
    """
    Login form.
    """
    email = TextField("Email",
        [validators.Required("Please enter your email address.")])
    password = PasswordField('Password',
        [validators.Required("Please enter a password.")])
    remember_me = BooleanField("Remember me", default=False)
    submit = SubmitField("Log In")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        if not super(LoginForm, self).validate():
            return False

        user = User.query.filter(User.email==self.email.data).first()
        if user and user.check_password(self.password.data):
            self.user = user
            return True
        else:
            self.email.errors.append("Invalid name or password")
            return False
