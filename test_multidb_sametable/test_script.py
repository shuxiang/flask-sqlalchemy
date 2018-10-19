#coding=utf8
import os

from sa_test import db, BINDS_MAP, app
from sa_test import Post, Cate
from flask import session, request

print Post, Cate

def test_scripts():
    bind = BINDS_MAP.get('u2')
    # # 对函数外部的变量赋值, 会将这个变量当成本地变量, 出现UnboundLocalError
    print db.session
    print dir(db.session)

    with app.test_request_context('/', headers={'company_id': 555}): # werkzueg will convert to Company-Id
        session['bind'] = 'b2'
        print 'request headers===>', request.headers, request.headers.keys()
        print Post.query.all()
        print Cate.query.all()
        print '============== job ==========', bind
        Cate2 = Cate.database(bind)
        Post2 = Post.database(bind)
        print Post2.query.all()
        print Cate2.query.all()

        print db.session.query(Post2).filter_by(username='u2_1').all()
        print db.session.query(Post2).filter(Post2.username==Cate2.username).all()

        db.session.close()


from flask_apscheduler import APScheduler

def main():
    import logging

    logging.basicConfig()
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    app.config['JOBS'] = [
            {
                "id": "test_jobs",
                "func": "test_jobs:test",
                "trigger": "interval",
                "seconds": 5
            }]

    # 定时任务
    from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
    app.config['SCHEDULER_JOB_DEFAULTS'] = {
        'coalesce': False,
        'max_instances': 1
    }
    app.config['SCHEDULER_EXECUTORS'] = {
        'processpool': ProcessPoolExecutor(os.environ.get('SCHEDULER_EXECUTORS_NUM', 5))
    }

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    return app

if __name__ == '__main__':
    test_scripts()
    #app = main()
    #app.run(port=7777, debug=True)
