
from _deps import Base, Integer, Column, String, ForeignKey, UniqueConstraint


class SecCurrency(Base):
     __tablename__ = 'sec_currency'

     ID = Column(Integer, primary_key=True, unique=True)
     NAME = Column(String, unique=True)

     def __init__(self,
                  _id,
                  name):
         self.ID = _id
         self.NAME = name

     def __repr__(self):
        return "<SecCurrency('%s','%s')>".format(self.ID.__str__(),
                                                 self.NAME.__str__())



