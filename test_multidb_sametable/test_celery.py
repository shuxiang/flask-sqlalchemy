#coding=utf8
import inspect
import os

from flask import session
from celery import Task, Celery

from sa_test import db, BINDS_MAP, app
from sa_test import Post, Cate


class CeleryBase(Celery):

    def init_app(self, app):
        try:# for workers
            self.conf.update(app.config)
        except:pass
        TaskBase = self.Task
        class ContextTask(TaskBase):
            abstract = True
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
        self.Task = ContextTask

class RequestContextTask(Task):
    """Base class for tasks that run inside a Flask request context."""
    abstract = True
    def __call__(self, *args, **kwargs):
        with app.test_request_context():
            # 无法inspect得到test.apply_async的参数, 只能固定tenant参数的位置为第一个
            session['bind'] = args[0]
            return super(RequestContextTask, self).__call__(*args, **kwargs)


SQLALCHEMY_DATABASE_URI = 'mysql://root:870129@127.0.0.1:3306/test?charset=utf8'
CELERY_BROKER_URL = 'sqla+mysql+py' + SQLALCHEMY_DATABASE_URI #'mysql://root:123456@127.0.0.1:3306/wms?charset=utf8'
CELERY_RESULT_BACKEND = 'db+mysql+py' + SQLALCHEMY_DATABASE_URI #'mysql://root:123456@127.0.0.1:3306/wms?charset=utf8'
BROKER_URL = CELERY_BROKER_URL
RESULT_BACKEND = CELERY_RESULT_BACKEND
app.config['CELERY_BROKER_URL'] = BROKER_URL
app.config['CELERY_RESULT_BACKEND'] = RESULT_BACKEND
app.config['BROKER_URL'] = BROKER_URL
app.config['RESULT_BACKEND'] = RESULT_BACKEND

celery = CeleryBase('test_celery')
celery.Task = RequestContextTask

celery.conf.update(CELERY_DEFAULT_QUEUE = os.environ.get('TASK_QUEUE_NAME', 'test'))
celery.init_app(app)

@celery.task
def test(tenant):
    print Post.query.all()
    print Cate.query.all()


@app.route('/celery')
def test_celery():

    test.apply_async(['b2'], expires=5, queue='test')
    return 'done'

if __name__ == '__main__':
    db.create_all()
    app.run(port=7777, debug=True)