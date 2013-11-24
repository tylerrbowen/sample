from ids.external_id_bundle import ExternalId

__author__ = 'Tyler'
from external_scheme import ExternalScheme
import re


class ExternalSchemes(object):

    ISIN = ExternalScheme.of('ISIN')
    CUSIP = ExternalScheme.of('CUSIP')
    SEDOL1 = ExternalScheme.of('SEDOL1')
    BLOOMBERG_BUID = ExternalScheme.of('BLOOMBERG_BUID')
    BLOOMBERG_BUID_WEAK = ExternalScheme.of('BLOOMBERG_BUID_WEAK')
    BLOOMBERG_TICKER = ExternalScheme.of('BLOOMBERG_TICKER')
    BLOOMBERG_TICKER_WEAK = ExternalScheme.of('BLOOMBERG_TICKER_WEAK')
    BLOOMBERG_TCM = ExternalScheme.of('BLOOMBERG_TCM')
    RIC = ExternalScheme.of('RIC')
    ACTIVFEED_TICKER = ExternalScheme.of('ACTIVFEED_TICKER')
    SURF = ExternalScheme.of('SURF')
    ICAP = ExternalScheme.of('ICAP')
    MARKIT_RED_CODE = ExternalScheme.of('MARKIT_RED_CODE')
    GMI = ExternalScheme.of('GMI')
    ISO_COUNTRY_ALPHA2 = ExternalScheme.of('ISO_COUNTRY_ALPHA2')
    ISO_CURRENCY_ALPHA3 = ExternalScheme.of('ISO_CURRENCY_ALPHA3')
    COPP_CLARK_LOCODE = ExternalScheme.of('COPP_CLARK_LOCODE')
    UN_LOCODE_2010_2 = ExternalScheme.of('UN_LOCODE_2010_2')
    TZDB_TIME_ZONE = ExternalScheme.of('TZDB_TIME_ZONE')
    FINANCIAL = ExternalScheme.of('FINANCIAL')
    ISO_MIC = ExternalScheme.of('ISO_MIC')

    @classmethod
    def isin_security_id(cls, code):
        if len(code) == 0:
            raise Exception('invalide isin')
        return ExternalId.of(cls.ISIN, code)

    @classmethod
    def cusip_security_id(cls, code):
        if len(code) == 0:
            raise Exception('invalide cusip')
        return ExternalId.of(cls.CUSIP, code)

    @classmethod
    def sedol1_security_id(cls, code):
        if len(code) == 0:
            raise Exception('invalide sedol')
        return ExternalId.of(cls.SEDOL1, code)

    @classmethod
    def bloomberg_build_security_id(cls,
                                   buid_code=None,
                                   ticker=None):
        if not buid_code and not ticker:
            raise Exception('must provide either code or ticker')
        if buid_code:
            if len(buid_code) == 0:
                raise Exception('invalid buid code')
            return ExternalId.of(cls.BLOOMBERG_BUID, buid_code)
        else:
            if len(ticker) == 0:
                raise Exception('invalid ticker')
            return ExternalId.of(cls.BLOOMBERG_TICKER, ticker)

    @classmethod
    def financial_region_id(cls, code):
        if not re.match('[A-Z+]+', code):
            raise Exception('invalide financial region code')
        return ExternalId.of(cls.FINANCIAL, code)

    @classmethod
    def time_zone_region_id(cls, zone):
        return ExternalId.of(cls.TZDB_TIME_ZONE, zone.get_id())

    @classmethod
    def currency_region_id(cls, currency):
        return ExternalId.of(cls.ISO_CURRENCY_ALPHA3, currency.get_code())

    @classmethod
    def country_region_id(cls, country):
        return ExternalId.of(cls.ISO_COUNTRY_ALPHA2, country.get_code())


