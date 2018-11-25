# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from werkzeug.utils import secure_filename
import os


from esso_admin.public.forms import PgUploadForm
from esso_admin.public.models import PgFile
from esso_admin.public.tasks import load_setup, load_file

blueprint = Blueprint('public', __name__, static_folder='../static')




@blueprint.route('/', methods=['GET', 'POST'])
def home():
    """Home page."""
    return render_template('public/home.html')


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')


@blueprint.route('/drawbot/', methods=['GET', 'POST'])
def drawbot():
    """Shows drawbot status and functions."""
    form = PgUploadForm()
    if form.validate_on_submit():
        if 'file' in request.files():
            file = request.files['file']
            filename = secure_filename(form.data.file)
            file.save(os.path.join(current_app.config['APP_DIR'], 'static', filename))

    pg_files = PgFile.query.all()
    return render_template('public/drawbot.html', pg_files=pg_files, form=form)


@blueprint.route('/action/<action_id>', methods=('GET', 'POST',))
def action(action_id):
    if action_id == 'setup':
        load_setup.apply_async()
        return redirect(url_for('public.home'))
    return redirect(url_for('public.home'))
