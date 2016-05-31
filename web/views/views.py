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
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2016/03/30$"
__revision__ = "$Date: 2016/05/31 $"
__copyright__ = "Copyright (c) "
__license__ = ""

import string
import datetime
import subprocess
from flask import request, flash,render_template, session, url_for, redirect, \
    g, abort, jsonify
from flask_login import login_required, current_user

import conf
from bootstrap import app, db
from web.forms import LoginForm
from web.models import User

#
# Default errors
#
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('errors/405.html'), 405

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


def redirect_url(default='start'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


@app.errorhandler(403)
def authentication_failed(e):
    flash('You do not have enough rights.', 'danger')
    return redirect(url_for('login'))

@app.errorhandler(401)
def authentication_required(e):
    flash('Authenticated required.', 'info')
    return redirect(url_for('login'))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.datetime.now()
        db.session.commit()

#
# Views.
#
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    return render_template('dashboard.html', user=g.user,
                                users=User.query.all())


@app.route('/dashboard/user/<user_id>', methods=['GET'])
@login_required
def dashboard_user(user_id):
    employee = User.query.filter(User.id == user_id).first()
    return render_template('dashboard_user.html', user=g.user,
                                employee=employee)

@app.route('/contributors', methods=['GET'])
def contributors():
    return render_template('contributors.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/db_initialization', methods=['GET'])
def db_initialization():
    cmd = ['./init_db.sh']
    try:
        subprocess.Popen(cmd, stdout=subprocess.PIPE)
        flash('Re-initialization of the database in progress...', 'success')
    except:
        flash('An error occured.', 'danger')
    return redirect(redirect_url())
