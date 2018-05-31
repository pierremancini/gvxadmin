#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  Copyright 2018 Yec'han Laizet <y.laizet@bordeaux.unicancer.fr>

"""
Admin interface for GVX.

Manage :
  - users
  - protocols
  - config
  - templates
"""


import os
import shutil
from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.fields import Select2Field, JSONField
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy.ext.automap import automap_base
from wtforms import fields


app = Flask(__name__)


class BaseConfig(object):
    DEBUG = False
    PORT = 5000
    HOST = "localhost"
    SECRET_KEY = '123456789'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///gvx_users.sqlite'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_BINDS = {
        'samples': 'sqlite:///gvx_samples_catalog.sqlite'
    }
    HTML_TEMPLATE_PATH = ''
    JSON_CONFIG_PATH = '/home/pmancini/Code/gvxadmin/data'
    BAM_FILES_PATH = ''
    EXPORT_PATH = ''
    LINKED_DATA_PATH = ''
    HTML_DATA_TYPES = (
        'qc',
        'var',
        'cst',
        'cnv',
        'fus'
    )
    DEFAULT_CONFIG_SRC = [
        ("", ""),
        ("default", "default")
    ]
    DEFAULT_TEMPLATE_SRC = [
        ("", ""),
        ("default", "default")
    ]
    PROTOCOLS_DB_PATH = 'sqlite:///{table_name}.sqlite'

app.config.from_object(BaseConfig())
app.config.from_pyfile('gvx_admin.cfg', silent=True)


db = SQLAlchemy(app)


# Flask views

@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


# Models

protocol_users = db.Table('protocol_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('protocol_id', db.Integer, db.ForeignKey('protocol.id'), primary_key=True)
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    admin = db.Column(db.Boolean())

    def __str__(self):
        return self.username


class Protocol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    users = db.relationship('User', secondary=protocol_users, lazy='subquery')

    def __str__(self):
        return self.name


class Samples(db.Model):
    __bind_key__ = 'samples'
    sample_name = db.Column(db.String(), primary_key=True)
    sample_category = db.Column(db.String(), primary_key=True)
    sample_fullname = db.Column(db.String())
    status = db.Column(db.String())
    last_export_date = db.Column(db.DateTime())
    validator = db.Column(db.String())
    validation_date = db.Column(db.DateTime())
    import_date = db.Column(db.DateTime())

# Create database here because required in ProtocolModelView
db.create_all()

# Admin views

class ProtocolModelView(ModelView):

    #@action('edit_config', 'Edit config', 'Are you sure you want to copy selected protocol?')
    #def action_copy(self, ids):
        #print(ids)

    edit_template = 'protocol_json_edit.html'


    form_create_rules = ('name', 'users', 'config_source', 'template_source')
    form_edit_rules = ('name', 'users', 'config_json', 'template_qc', 'template_var', 'template_cst', 'template_cnv', 'template_fus')

    form_extra_fields = {
        'config_source': Select2Field(label='Config source', choices=app.config['DEFAULT_CONFIG_SRC'] + [(c[0], c[0]) for c in db.session.query(Protocol.name)]),
        'template_source': Select2Field(label='Template source', choices=app.config['DEFAULT_TEMPLATE_SRC'] + [(c[0], c[0]) for c in db.session.query(Protocol.name)]),
        'config_json': JSONField('Config JSON'),
        'template_qc': fields.TextAreaField('Template QC'),
        'template_var': fields.TextAreaField('Template VAR'),
        'template_cst': fields.TextAreaField('Template CST'),
        'template_cnv': fields.TextAreaField('Template CNV'),
        'template_fus': fields.TextAreaField('Template FUS')
    }

    #def on_model_change(self, form, instance):
        #pass

    def propose(self):
        return app.config['DEFAULT_CONFIG_SRC'] + [(c[0], c[0]) for c in self.session.query(Protocol.name)]

    def on_form_prefill(self, form, id):
        # Fill up json config field from file
        file_path = os.path.join(app.config['JSON_CONFIG_PATH'], "%s.json" % form.data['name'])
        if os.path.isfile(file_path):
            form.config_json.raw_data = (open(file_path).read(), )

        # Fill up html templates field from file
        for data_type in app.config['HTML_DATA_TYPES']:
            file_path = os.path.join(app.config['HTML_TEMPLATE_PATH'], "%s.%s.html" % (form.data['name'], data_type))
            if os.path.isfile(file_path):
                form['template_%s' % data_type].data = open(file_path).read()


    def after_model_change(self, form, model, is_created):
        if is_created:
            # Copy json config from selected project
            src_path = os.path.join(app.config['JSON_CONFIG_PATH'], "%s.json" % form.data['config_source'])
            dest_path = os.path.join(app.config['JSON_CONFIG_PATH'], "%s.json" % form.data['name'])
            if form.data["config_source"] and os.path.isfile(src_path) and not os.path.isfile(dest_path):
                shutil.copy(
                    src_path,
                    dest_path
                )
                shutil.chown(dest_path, user=-1, group="www-data")
                flash("%s config file duplicated from %s" % (form.data['name'], form.data['config_source']), 'info')

            # Copy html templates from selected project
            for data_type in app.config['HTML_DATA_TYPES']:
                src_path = os.path.join(app.config['HTML_TEMPLATE_PATH'], "%s.%s.html" % (form.data['template_source'], data_type))
                dest_path = os.path.join(app.config['HTML_TEMPLATE_PATH'], "%s.%s.html" % (form.data['name'], data_type))
                if form.data["template_source"] and os.path.isfile(src_path) and not os.path.isfile(dest_path):
                    shutil.copy(
                        src_path,
                        dest_path
                    )
                    shutil.chown(dest_path, user=-1, group="www-data")
                    flash("%s %s template file duplicated from %s" % (data_type.upper(), form.data['name'], form.data['config_source']), 'info')

            # Create protocol data directories
            dir_path = os.path.join(app.config['BAM_FILES_PATH'], form.data['name'])
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            dir_path = os.path.join(app.config['EXPORT_PATH'], form.data['name'])
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            for data_type in app.config['HTML_DATA_TYPES']:
                dir_path = os.path.join(app.config['LINKED_DATA_PATH'], form.data['name'], data_type)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
        else:
            # Save json config field to file
            file_path = os.path.join(app.config['JSON_CONFIG_PATH'], "%s.json" % form.data['name'])
            open(file_path, 'w').write(form.config_json.raw_data[0])
    
            # Save html templates field to file
            for data_type in app.config['HTML_DATA_TYPES']:
                file_path = os.path.join(app.config['HTML_TEMPLATE_PATH'], "%s.%s.html" % (form.data['name'], data_type))
                open(file_path, 'w').write(form['template_%s' % data_type].data)


class SamplesModelView(ModelView):
    column_display_pk = True
    column_filters = ('sample_name', 'sample_category')
    column_searchable_list = ('sample_name', 'sample_category')
    form_choices = {
        'status': [
            (u'pending', u'Pending'),
            (u'ongoing', u'Ongoing'),
            (u'interpreted', u'Interpreted'),
            (u'validated', u'Validated'),
            (u'exported', u'Exported')
        ]
    }

    def after_model_delete(self, model):
        """Remove table containing data of the sample delete from the catalog."""
        protocol_db = app.config['PROTOCOLS_DB_PATH'].format(table_name=model.sample_category)
        engine = create_engine(protocol_db)
        base = automap_base()
        base.prepare(engine, reflect=True)
        meta = MetaData()
        table_to_delete = Table(model.sample_name, meta, autoload=True, autoload_with=engine)
        table_to_delete.drop(engine)
        flash("data table for %s from %s has been successfully deleted" % (model.sample_name, model.sample_category), 'info')

        # TODO: Manage absent table : OperationalError: (sqlite3.OperationalError) no such table: SARC3-001H_CNV [SQL: u'\nDROP TABLE "SARC3-001H_CNV"']

admin = Admin(app, name='GVX Admin', template_mode='bootstrap2')
admin.add_view(ModelView(User, db.session))
admin.add_view(ProtocolModelView(Protocol, db.session))
admin.add_view(SamplesModelView(Samples, db.session))

if __name__ == '__main__':

    # Create DB
    db.create_all(bind=['samples'])

    # Start app
    app.run(debug=app.config['DEBUG'], port=app.config['PORT'], host=app.config['HOST'])
