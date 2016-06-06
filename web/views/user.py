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
__date__ = "$Date: 2016/06/06$"
__revision__ = "$Date: 2016/06/06 $"
__copyright__ = "Copyright (c) "
__license__ = ""

from flask import Blueprint, flash, render_template, url_for, current_app, \
                    request, redirect
from flask_login import login_required, current_user

from bootstrap import db
from web.models import User
from web.forms import ProfileForm
from web.lib.utils import redirect_url

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.filter(User.id==current_user.id).first()
    form = ProfileForm()

    if request.method == 'POST':
        if form.validate():
            # update user
            form.populate_obj(user)

            if form.password.data and \
                form.password.data == form.password_conf.data:
                user.set_password(form.password.data)

            db.session.commit()

            flash('User successfully updated', 'success')
            return redirect(url_for('user.profile'))
        else:
            return render_template('profile.html', user=user, form=form)

    if request.method == 'GET':
        form = ProfileForm(obj=user)
        return render_template('profile.html', user=user, form=form)