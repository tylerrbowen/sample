from _deps import Base, Integer, Column, String


class SecGics(Base):
     __tablename__ = 'sec_gics'

     ID = Column(Integer, primary_key=True)
     NAME = Column(String, unique=True)
     DESCRIPTION = Column(String)

     def __init__(self,
                  _id,
                  name,
                  description):
         self.ID = _id
         self.NAME = name
         self.DESCRIPTION = description

     def __repr__(self):
        return "<SecGics('%s','%s','%s')>".format(self.ID.__str__(),
                                                      self.NAME.__str__(),
                                                      self.DESCRIPTION.__str__())




