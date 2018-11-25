# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, logout_user, login_manager, login_user
from esso_admin.user.forms import LoginForm, RegisterForm
from esso_admin.user.models import User
from esso_admin.utils import flash_errors


blueprint = Blueprint('user', __name__, url_prefix='/users', static_folder='../static')

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/')
@login_required
def members():
    """List members."""
    return render_template('users/members.html')


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('public.home'))
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash('You are logged in.', 'success')
            redirect_url = request.args.get('next') or url_for('user.members')
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("users/login.html", form=form)


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(username=form.username.data, email=form.email.data, password=form.password.data, active=True)
        flash('Thank you for registering. You can now log in.', 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('users/register.html', form=form)
