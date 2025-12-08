# encoding: utf-8

import datetime
import logging
from collections import OrderedDict

from ckan.model.meta import metadata
from ckan.model.types import UuidType
from sqlalchemy import (Column, DateTime, Unicode,
                        UniqueConstraint, orm)
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
    from ckan.model import meta
    Version.__table__.create(bind=meta.engine, checkfirst=True)


def tables_exist():
    from ckan.model import meta
    try:
        engine = meta.engine
        if engine is None:
            return False
        return Version.__table__.exists(bind=engine)
    except Exception:
        # Catch all exceptions during database initialization
        # This can happen when CKAN core tables don't exist yet
        return False
