#SEC_SECURITY2IDKEY
from _deps import Base, Integer, Column, ForeignKey
from sec_security import SecSecurity
from sec_idkey import SecIdKey


class SecSecurity2IdKey(Base):
     __tablename__ = 'sec_security2idkey'

     SECURITY_ID = Column(Integer, ForeignKey('sec_security.id'), primary_key=True)
     IDKEY_ID = Column(Integer, ForeignKey('sec_idkey.id'), primary_key=True)

     def __init__(self,
                  security_id,
                  idkey_id):
         self.SECURITY_ID = security_id
         self.IDKEY_ID = idkey_id

     def __repr__(self):
        return "<SecSecurity2IdKey('%s','%s')>".format(self.SECURITY_ID.__str__(),
                                                       self.IDKEY_ID.__str__())


