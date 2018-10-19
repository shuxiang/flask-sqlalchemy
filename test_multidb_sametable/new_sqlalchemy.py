#coding=utf8
from flask import session
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy import orm
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from flask_sqlalchemy import SQLAlchemy, itervalues, string_types, BaseQuery, Model
from flask_sqlalchemy.model import DefaultMeta

sys_type = type


class _QueryProperty(object):
    def __init__(self, sa):
        self.sa = sa

    def __get__(self, obj, type):
        try:
            # 非app的http请求里, 存在无法获得tenant的问题; 只能用multi_db那种方式手动传入
            print obj, type, "__bind_key__", getattr(type, '__bind_key__', None), '__restless__', getattr(type, '__restless__', False), '__with_binds__', getattr(type, '__with_binds__', False)
            if getattr(type, '__bind_key__', None) is None and not getattr(type, '__restless__', False) and getattr(type, '__with_binds__', False):
                bind = session['bind']
                print '=======bind:', bind
                classname = str(type).split('.')[-1][:-2]
                type = sys_type(classname, (type,), {"__bind_key__": bind})
            mapper = orm.class_mapper(type)
            if mapper:
                query =  type.query_class(mapper, session=self.sa.session())
                query.model_class = type
                return query
        except UnmappedClassError:
            return None


class MbSQLAlchemy(SQLAlchemy):
    """support multi db for binds; binds have some tables"""
    def __init__(self, app=None, *args, **kwargs):

        super(MbSQLAlchemy, self).__init__(app=app, *args, **kwargs)
        # 要初始化metadata, must init meta
        if app:
            self._get_metadata_for_all_tables(app)

    def init_app(self, app=None):
        self.app = app
        super(MbSQLAlchemy, self).init_app(app)
        self._get_metadata_for_all_tables(app)


    def get_model_by_tablename(self, tablename):
        for c in self.Model._decl_class_registry.values():
            if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
                return c

    def _get_metadata_for_all_tables(self, app, bind='__all__', skip_tables=False):
        app = self.get_app(app)

        if bind == '__all__':
            binds = [None] + list(app.config.get('SQLALCHEMY_BINDS') or ())
        elif isinstance(bind, string_types) or bind is None:
            binds = [bind]
        else:
            binds = bind

        for bind in binds:
            extra = {}
            if not skip_tables:
                tables = self.get_tables_for_bind(bind)
                extra['tables'] = tables

            self.get_metadata(bind=bind)

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

    def make_declarative_base(self, model, metadata=None):
        """Creates the declarative base that all models will inherit from.

        :param model: base model class (or a tuple of base classes) to pass
            to :func:`~sqlalchemy.ext.declarative.declarative_base`. Or a class
            returned from ``declarative_base``, in which case a new base class
            is not created.
        :param: metadata: :class:`~sqlalchemy.MetaData` instance to use, or
            none to use SQLAlchemy's default.

        .. versionchanged 2.3.0::
            ``model`` can be an existing declarative base in order to support
            complex customization such as changing the metaclass.
        """
        if not isinstance(model, DeclarativeMeta):
            model = declarative_base(
                cls=model,
                name='Model',
                metadata=metadata,
                metaclass=DefaultMeta
            )

        # if user passed in a declarative base and a metaclass for some reason,
        # make sure the base uses the metaclass
        if metadata is not None and model.metadata is not metadata:
            model.metadata = metadata

        if not getattr(model, 'query_class', None):
            model.query_class = self.Query

        model.query = _QueryProperty(self)
        return model



