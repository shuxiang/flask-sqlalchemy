#coding=utf8
import inspect
import os

from flask import session
from celery import Task, Celery

from sa_test import db, BINDS_MAP, app
from sa_test import Post, Cate


from restless import APIManager
restless_manager = APIManager()
restless_manager.app = app
restless_manager.init_app(app, flask_sqlalchemy_db=db)

def create_api_blueprint(app):
    bp = restless_manager.create_api_blueprint(
        Post,
        methods=['GET', "POST", 'PATCH', 'PUT'],
        preprocessors={}, postprocessors={},
        results_per_page=50)

    app.register_blueprint(bp, url_prefix="/api")
    return bp

create_api_blueprint(app)


if __name__ == '__main__':
    db.create_all()
    app.run(port=7777, debug=True)