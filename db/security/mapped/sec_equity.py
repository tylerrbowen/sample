from _deps import Base, Integer, Column, String, Boolean, ForeignKey


class SecEquity(Base):
    __tablename__ = 'sec_equity'

    SECURITY_ID = Column(Integer,
                         ForeignKey('sec_security.id',
                                    name='SEC_FK_EQUITY2SEC'),
                         primary_key=True)
    SHORTNAME = Column(String)
    COMPANYNAME = Column(String)
    EXCHANGE_ID = Column(Integer,
                         ForeignKey('sec_exchange.id',
                                    name='SEC_FK_EQUITY2EXCHANGE'))
    CURRENCY_ID = Column(Integer,
                         ForeignKey('sec_currency.id',
                                    name='SEC_FK_EQUITY2CURRENCY'))
    GICSCODE_ID = Column(Integer,
                         ForeignKey('sec_gics.id',
                                    name='SEC_FK_EQUITY2GICS'))
    PREFERRED = Column(Boolean)

    def __init__(self,
                 _id,
                 shortname,
                 company_name,
                 exchange_id,
                 currency_id,
                 gicscode_id,
                 preferred):
     self.ID = _id
     self.SHORTNAME = shortname
     self.COMPANYNAME = company_name
     self.EXCHANGE_ID = exchange_id
     self.CURRENCY_ID = currency_id
     self.GICSCODE_ID = gicscode_id
     self.PREFERRED = preferred

    def __repr__(self):
        return "<SecEquity('%s','%s','%s','%s','%s','%s','%s')>".format(self.ID.__str__(),
                                                                        self.SHORTNAME.__str__(),
                                                                        self.COMPANYNAME.__str__(),
                                                                        self.EXCHANGE_ID.__str__(),
                                                                        self.CURRENCY_ID.__str__(),
                                                                        self.GICSCODE_ID.__str__(),
                                                                        self.PREFERRED.__str__())