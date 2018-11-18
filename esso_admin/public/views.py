# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import login_required, login_user, logout_user
from werkzeug.utils import secure_filename
import os


from esso_admin.extensions import login_manager
from esso_admin.public.forms import LoginForm, PgUploadForm
from esso_admin.public.models import PgFile
from esso_admin.user.forms import RegisterForm
from esso_admin.user.models import User
from esso_admin.utils import flash_errors
from esso_admin.public.tasks import load_setup, load_file

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    """Home page."""
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
    return render_template('public/home.html', form=form)


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


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
    return render_template('public/register.html', form=form)


@blueprint.route('/about/')
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template('public/about.html', form=form)


@blueprint.route('/drawbot/')
def drawbot():
    """Shows drawbot status and functions."""
    form = PgUploadForm()
    if form.validate_on_submit():
        if 'file' in request.files():
            file = request.files['file']
            filename = secure_filename(form.data.file)
            file.save(os.path.join(current_app.config['APP_DIR'], 'static', filename))

    pg_files = PgFile.query.all()
    return render_template('public/drawbot.html', pg_files=pg_files)


@blueprint.route('/action/<action_id>', methods=('GET', 'POST',))
def action(action_id):
    if action_id == 'setup':
        load_setup.apply_async()
        return redirect(url_for('public.home'))
    return redirect(url_for('public.home'))
