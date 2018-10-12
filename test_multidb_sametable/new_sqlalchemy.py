#coding=utf8
from flask import session
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy import orm

from flask_sqlalchemy import SQLAlchemy, itervalues

sys_type = type


class _QueryProperty(object):
    def __init__(self, sa):
        self.sa = sa

    def __get__(self, obj, type):
        try:
            # 非app的http请求里, 存在无法获得tenant的问题; 只能用multi_db那种方式手动传入
            if not getattr(type, '__bind_key__', None):
                bind = session['bind']
                classname = str(type).split('.')[-1][:-2]
                type = sys_type(classname, (type,), {"__bind_key__": bind})
            mapper = orm.class_mapper(type)
            if mapper:
                return type.query_class(mapper, session=self.sa.session())
        except UnmappedClassError:
            return None


class MbSQLAlchemy(SQLAlchemy):
    """support multi db for binds; binds have some tables"""

    def get_model_by_tablename(self, tablename):
        for c in self.Model._decl_class_registry.values():
            if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
                return c

    def get_tables_for_bind(self, bind=None):
        """Returns a list of all tables relevant for a bind."""
        result = []
        for table in itervalues(self.Model.metadata.tables):
            if table.info.get('bind_key') == bind:
                result.append(table)

            m = self.get_model_by_tablename(table.name)
            if bind is not None and getattr(m, '__with_binds__', None):
                result.append(table)

        return result



