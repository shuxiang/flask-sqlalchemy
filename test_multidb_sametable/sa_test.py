#coding=utf8
import sys
sys.path.append('..')

SQLALCHEMY_DATABASE_URI = 'sqlite:////home/sx/soft/flask-sqlalchemy/sa0.db'
SQLALCHEMY_BINDS = {
    'b1':        'sqlite:////home/sx/soft/flask-sqlalchemy/sa1.db',
    'b2':      'sqlite:////home/sx/soft/flask-sqlalchemy/sa2.db'
}
BINDS_MAP = {
    'u1': 'b1',
    'u2': 'b2',
}

import os
from flask import Flask, session
from flask_sqlalchemy import Model, BaseQuery
from new_sqlalchemy import MbSQLAlchemy

sys_type = type

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS
app.config['SECRET_KEY'] = 'xoxo=====================xxxx'

class MyModel(Model):
    # in this case we're just using a custom BaseQuery class,
    # but you can add other stuff as well
    query_class = BaseQuery

    def __new__(cls, *args, **kwargs):
        if not getattr(cls, '__bind_key__', None):
            print '<<<<==========new model class'
            print session['bind']
            Model.__bind_key__ = session['bind']
        return Model.__new__(cls, *args, **kwargs)

    @classmethod
    def database(cls, tenant):
        # tenant to bind
        bind = tenant
        return sys_type(cls.__name__, (cls,), {"__bind_key__": bind})


db = MbSQLAlchemy(app, model_class=MyModel)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return '<User %r>' % self.username


class Post(db.Model):
    __with_binds__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return '<Post %r, %s>' % (self.username, self.id)


class Cate(db.Model):
    __with_binds__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return '<Cate %r, %s>' % (self.username, self.id)


@app.route('/createuser')
def createuser():
    u1 = User(username='u1')
    u2 = User(username='u2')
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()

    session['tenant'] = 'u1'
    session['bind'] = BINDS_MAP.get('u1')

    return 'done'

@app.route('/login')
def login():
    session['tenant'] = 'u1'
    session['bind'] = BINDS_MAP.get('u1')

    return 'done'

@app.route('/createpost')
def createpost():
    print '-----------> post 1', Post
    #print '---------> query: ', Post.query, dir(Post)
    print Post.query.all()
    print '=============== post 1'
    p1_2 = Post.query.filter(Post.username=='u1_1').first()
    if not p1_2:
        p1_2 = Post(username='u1_1')
        db.session.add(p1_2)
        db.session.commit()
    print Post.query.all()

    # print Post.__bind_key__
    #print session['tenant']
    #print Post.__bind_key__

    # p1 = Post(username='u1')
    # p2 = Post(username='u2')
    # db.session.add(p1)
    # db.session.add(p2)
    # db.session.commit()

    return 'done'


@app.route('/login2')
def login2():
    session['tenant'] = 'u2'
    session['bind'] = BINDS_MAP.get('u2')

    return 'done'

@app.route('/createpost2')
def createpost2():
    print '-----------> post 2', Post
    print Post.query.all()
    print '=============== post 2'
    p2_1 = Post.query.filter_by(username='u2_1').first()
    if not p2_1:
        p2_1 = Post(username='u2_1')
        db.session.add(p2_1)
        db.session.commit()
    print Post.query.all()

    print 'db.session.query ------------ '
    if not Cate.query.filter_by(username='u2_1').count():
        c1 = Cate(username='u2_1')
        db.session.add(c1)
        db.session.commit()
    print db.session.query(Post).filter_by(username='u2_1').all()
    print db.session.query(Post).filter(Post.username==Cate.username).all()


    # # different bind tables can't join
    # u21 = User.query.filter_by(username='u2_1').first()
    # if not u21:
    #     u21 = User(username='u2_1')
    #     db.session.add(u21)
    #     db.session.flush()
    # print db.session.query(Post).filter(Post.username==Cate.username, Post.username==User.username).all()

    db.session.commit()

    return 'done'




if __name__ == '__main__':
    db.create_all()
    app.run(port=6666, debug=True)


"""
无法动态增加binds, 因为这已经设计到sqlalchemy与flask架构实现本身;
requirements: sqlalchemy==1.2.0
"""