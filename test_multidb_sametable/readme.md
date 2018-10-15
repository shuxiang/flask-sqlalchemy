
## imports:
    无法动态增加binds, 因为这已经设计到sqlalchemy与flask架构实现本身;
    只能用company_id作为多租户分库,不能用完整的tenant, 因为存在__all__的情况
    table.__with_binds__ 区分是否采用binds, docker的环境变量控制是否启用

## no_supports:
    no support db.engine.execute(mover_sql)
    app/__init__.py P180 automap

## changes:
    requirements: sqlalchemy==1.2.0
    migration: 逐个db未升级? 未解决.  升级失败, 可以手动解决
    restless: 因为restless中无法获得tenant, 无法与之兼容. 修改后, restless注册blueprint时, 忽略tenant的过滤, 也可以支持. 需要同时修改restless与MbSQLAlchemy
    celery: 无法inspect得到xxxfunc.apply_async的参数, 只能固定tenant参数的位置为第一个
    apps: 无tenant, 需要手动加入
    manage command: with app.test_request_context
    superset: 每个公司都要配一次