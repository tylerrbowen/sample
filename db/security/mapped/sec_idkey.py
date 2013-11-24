from _deps import Base, Integer, String, Column, UniqueConstraint


class SecIdKey(Base):
     __tablename__ = 'sec_idkey'

     ID = Column(Integer, primary_key=True)
     KEY_SCHEME = Column(String)
     KEY_VALUE = Column(String)
     UniqueConstraint('KEY_SCHEME', 'KEY_VALUE', 'SEC_CHK_IDKEY')

     def __init__(self,
                  _id,
                  key_scheme,
                  key_value):
         self.ID = _id
         self.KEY_SCHEME = key_scheme
         self.KEY_VALUE = key_value

     def __repr__(self):
        return "<SecIdKey('%s','%s', '%s'')>".format(self.ID.__str__(),
                                                       self.KEY_SCHEME.__str__(),
                                                       self.KEY_VALUE.__str__())

