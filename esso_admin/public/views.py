# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask.json import jsonify
from werkzeug.utils import secure_filename
import os


from esso_admin.drawbot.forms import PgUploadForm
from esso_admin.drawbot.models import PgFile
from esso_admin.drawbot.tasks import load_setup, load_file
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

