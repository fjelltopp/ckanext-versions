# encoding: utf-8

import datetime
import logging
from collections import OrderedDict

from ckan.model.meta import metadata
from ckan.model.types import UuidType
from sqlalchemy import (Column, DateTime, Unicode,
                        UniqueConstraint, orm, inspect)
from sqlalchemy.ext.declarative import declarative_base

log = logging.getLogger(__name__)

Base = declarative_base(metadata=metadata)


class Version(Base):
    __tablename__ = u'version'
    __table_args__ = (
        UniqueConstraint('package_id', 'resource_id', 'name'),
    )

    id = Column(UuidType, primary_key=True, default=UuidType.default)
    package_id = Column(UuidType, nullable=False)
    resource_id = Column(UuidType, nullable=True)
    activity_id = Column(UuidType, nullable=False)
    name = Column(Unicode, nullable=False)
    notes = Column(Unicode, nullable=True)
    creator_user_id = Column(UuidType, nullable=False)
    created = Column(DateTime, default=datetime.datetime.utcnow)

    def as_dict(self):
        _dict = OrderedDict()
        table = orm.class_mapper(self.__class__).mapped_table
        for col in table.c:
            val = getattr(self, col.name)
            if isinstance(val, datetime.date):
                val = str(val)
            if isinstance(val, datetime.datetime):
                val = val.isoformat()
            _dict[col.name] = val
        return _dict


def create_tables():
    if metadata.bind is None:
        from ckan.model import meta
        engine = meta.engine
    else:
        engine = metadata.bind
    Version.__table__.create(engine, checkfirst=True)


def tables_exist():
    if metadata.bind is None:
        from ckan.model import meta
        engine = meta.engine
    else:
        engine = metadata.bind
    inspector = inspect(engine)
    return inspector.has_table(Version.__tablename__)
