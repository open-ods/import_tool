import sys

import os.path
from sqlalchemy import Column, Integer, String, Boolean, Date

# setup path so we can import our own models and controllers
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from import_tool.models.base import Base


class Role(Base):
    """
    Roles class that keeps track of information about a
    particular Roles. This class uses SQLAlchemy as an ORM

    """
    __tablename__ = 'roles'

    ref = Column(Integer, primary_key=True)
    org_odscode = Column(String(10), index=True)
    code = Column(String(10), index=True)
    primary_role = Column(Boolean)
    unique_id = Column(String(10))
    status = Column(String(10), index=True)
    legal_start_date = Column(Date)
    legal_end_date = Column(Date)
    operational_start_date = Column(Date)
    operational_end_date = Column(Date)

    # Returns a printable version of the objects contents
    def __repr__(self):
        return "<Role(' %s %s %s %s %s %s %s %s %s %s %s')>" % (
            self.ref,
            self.organisation_ref,
            self.org_odscode,
            self.code,
            self.primary_role,
            self.unique_id,
            self.status,
            self.legal_start_date,
            self.legal_end_date,
            self.operational_start_date,
            self.operational_end_date)
