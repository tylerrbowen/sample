from _deps import Base, Integer, String, Column, DateTime, ForeignKey, CheckConstraint


class SecSecurity(Base):
     __tablename__ = 'sec_security'

     ID = Column(Integer, primary_key=True)
     OID = Column(Integer, ForeignKey(ID))
     VER_FROM_INSTANT = Column(DateTime)
     VER_TO_INSTANT = Column(DateTime)
     CORR_FROM_INSTANT = Column(DateTime)
     CORR_TO_INSTANT = Column(DateTime)
     NAME = Column(String)
     SEC_TYPE = Column(String)
     DETAIL_TYPE = Column(String)

     CheckConstraint('VER_FROM_INSTANT <= VER_TO_INSTANT', name='SEC_CHK_SEC_VER_ORDER')
     CheckConstraint('CORR_FROM_INSTANT <= CORR_TO_INSTANT', name='SEC_CHK_SEC_CORR_ORDER')
     CheckConstraint("DETAIL_TYPE in (('D'),('M'),('R'))", name='SEC_CHK_DETAIL_TYPE')

     def __init__(self,
                  _id,
                  oid,
                  ver_from_instant,
                  ver_to_instant,
                  corr_from_instant,
                  corr_to_instant,
                  name,
                  sec_type,
                  detail_type):
         self.ID = _id
         self.OID = oid
         self.VER_FROM_INSTANT = ver_from_instant
         self.VER_TO_INSTANT = ver_to_instant
         self.CORR_FROM_INSTANT = corr_from_instant
         self.CORR_TO_INSTANT = corr_to_instant
         self.NAME = name
         self.SEC_TYPE = sec_type
         self.DETAIL_TYPE = detail_type

     def __repr__(self):
        return "<SecSecurity('%s','%s', '%s', '%s', " + \
               "'%s', '%s', '%s', '%s', '%s')>".format(self.ID.__str__(),
                                                       self.OID.__str__(),
                                                       self.VER_FROM_INSTANT.__str__(),
                                                       self.VER_TO_INSTANT.__str__(),
                                                       self.CORR_FROM_INSTANT.__str__(),
                                                       self.CORR_TO_INSTANT.__str__(),
                                                       self.NAME.__str__(),
                                                       self.SEC_TYPE.__str__(),
                                                       self.DETAIL_TYPE.__str__())
