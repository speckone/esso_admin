# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask.json import jsonify
from werkzeug.utils import secure_filename
import os


from esso_admin.public.forms import PgUploadForm
from esso_admin.public.models import PgFile
from esso_admin.public.tasks import load_setup, load_file
from esso_admin.extensions import celery

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
        file = request.files.get('file')
        if file:
            filename = secure_filename(form.file.data.filename)
            file.save(os.path.join(current_app.config['APP_DIR'], 'static', filename))
            pg_file = PgFile.create(name=form.name.data, file=filename)
    pg_files = PgFile.query.all()
    return render_template('public/drawbot.html', pg_files=pg_files, form=form)


@blueprint.route('/queue_length')
def queue_length():
    queue_length = 0
    with celery.pool.acquire(block=True) as conn:
        queue_length = conn.default_channel.client.llen('drawbot')
    ql = [{'queue_length': queue_length}]
    return jsonify({'data': ql})



@blueprint.route('/action/<action_id>/<file>', methods=('GET', 'POST',))
def action(action_id, file=None):
    if action_id == 'setup':
        load_setup.delay()
    elif action_id == 'file':
        load_file.apply_async(args=[file,])
    return redirect(url_for('public.drawbot'))
