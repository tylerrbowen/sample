

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint
from sqlalchemy import UniqueConstraint
Base = declarative_base()

