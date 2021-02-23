from flask import session, redirect, url_for, render_template, jsonify, request
from web.utils.auxiliary import login_required
from web import APP


@APP.route('/')
def html_system_login():
    """用户登录页面"""
    if 'status' in session:
        return redirect(url_for('html_system_index'), 302)
    return render_template('login.html')


@APP.route('/system/index')
@login_required
def html_system_index():
    """框架首页"""
    return render_template('index.html', username=session['username'])