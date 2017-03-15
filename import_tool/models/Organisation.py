import sys

import os.path
from sqlalchemy import Column, Integer, String, Date, Boolean

# setup path so we can import our own models and controllers
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from import_tool.models.base import Base


class Organisation(Base):
    """
    Organisations class that keeps track of information about a
    particular organisations. This class uses SQLAlchemy as an ORM

    """
    __tablename__ = 'organisations'

    ref = Column(Integer, primary_key=True)
    odscode = Column(String(10))
    name = Column(String(200))
    status = Column(String(10))
    record_class = Column(String(10))
    last_changed = Column(String)
    legal_start_date = Column(Date)
    legal_end_date = Column(Date)
    operational_start_date = Column(Date)
    operational_end_date = Column(Date)
    ref_only = Column(Boolean)
    post_code = Column(String(15))

    # Returns a printable version of the objects contents
    def __repr__(self):
        return "<Organisation('{ref} {ods_code} {name} {status} {record_class} {last_changed} {legal_start_date} " \
               "{legal_end_date} {operational_start_date} {operational_end_date} {ref_only} {post_code}'\)>".format(
                ref=self.ref,
                ods_code=self.odscode,
                name=self.name,
                status=self.status,
                record_class=self.record_class,
                last_changed=self.last_changed,
                legal_start_date=self.legal_start_date,
                legal_end_date=self.legal_end_date,
                operational_start_date=self.operational_start_date,
                operational_end_date=self.operational_end_date,
                ref_only=self.ref_only,
                post_code=self.post_code
        )
