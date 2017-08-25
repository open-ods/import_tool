import sys

import os.path
from sqlalchemy import Column, Integer, String

# setup path so we can import our own models and controllers
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from import_tool.models.base import Base


class Address(Base):
    """
    Addresses class that keeps track of information about a
    particular Addresses. This class uses SQLAlchemy as an ORM

    """
    __tablename__ = 'addresses'

    addresses_ref = Column(Integer, primary_key=True)
    org_odscode = Column(String(10), index=True)
    address_line1 = Column(String(75))
    address_line2 = Column(String(75))
    address_line3 = Column(String(75))
    town = Column(String(75))
    county = Column(String(75))
    post_code = Column(String(15))
    country = Column(String(50))

    # Returns a printable version of the objects contents
    def __repr__(self):
        return "<Addresses(%s %s %s %s %s %s %s %s %s %s %s\)>" \
            % (
                self.addresses_ref,
                self.organisation_ref,
                self.org_odscode,
                self.address_line1,
                self.address_line2,
                self.address_line3,
                self.town,
                self.county,
                self.post_code,
                self.uprn,
                self.location_id)
