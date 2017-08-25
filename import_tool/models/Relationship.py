import sys

import os.path
from sqlalchemy import Column, Integer, String, Date

# setup path so we can import our own models and controllers
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from import_tool.models.base import Base


class Relationship(Base):
    """
    Relationships class that keeps track of information about a
    particular Relationships. This class uses SQLAlchemy as an ORM

    """
    __tablename__ = 'relationships'

    ref = Column(Integer, primary_key=True)
    code = Column(String(10), index=True)
    target_odscode = Column(String(50), index=True)
    org_odscode = Column(String(10), index=True)
    legal_start_date = Column(Date)
    legal_end_date = Column(Date)
    operational_start_date = Column(Date)
    operational_end_date = Column(Date)
    status = Column(String(10))
    unique_id = Column(String)

    # Returns a printable version of the objects contents
    def __repr__(self):
        return "<Relationship('%s %s %s %s %s %s %s %s %s %s %s'\
            )>" % (
            self.ref,
            self.organisation_ref,
            self.relationship_code,
            self.target_odscode,
            self.org_odscode,
            self.legal_start_date,
            self.legal_end_date,
            self.operational_start_date,
            self.operational_end_date,
            self.status,
            self.uid)
