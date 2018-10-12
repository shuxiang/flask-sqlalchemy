#coding=utf8

from sa_test import db, BINDS_MAP, app
from sa_test import Post, Cate




def test():
    print '================== test jobs ==================='
    bind = BINDS_MAP.get('u2')
    print '============== job ==========', bind
    Post2 = Post.database(bind)
    Cate2 = Cate.database(bind)
    print Post2.query.all()
    print Cate2.query.all()

    print db.session.query(Post2).filter_by(username='u2_1').all()
    print db.session.query(Post2).filter(Post2.username==Cate2.username).all()

    db.session.close()

    print '============== job finish ============='