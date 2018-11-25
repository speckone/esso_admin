# -*- coding: utf-8 -*-
"""Public forms."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, FileField
from wtforms.validators import DataRequired





class PgUploadForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    file = FileField('File', validators=[DataRequired()])
