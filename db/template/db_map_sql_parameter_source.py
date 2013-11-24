from db.date_utils import DbDateUtils
from db.template.map_sql_parameter_source import MapSqlParameterSource
from db.template.types import Types


class DbMapSqlParameterSource(MapSqlParameterSource):
    def __init__(self,
                 param_name='',
                 value=None,
                 values=None):
        super(DbMapSqlParameterSource, self).__init__(param_name,
                                                      value,
                                                      values)

    def add_timestamp(self,
                      name,
                      instant):
        self.add_value(name, DbDateUtils.to_sql_timestamp(instant))
        return self

    def add_time_stamp_null_future(self,
                                   name,
                                   instant):
        if instant is None:
            self.add_value(name, DbDateUtils.MAX_SQL_TIMESTAMP)
        else:
            self.add_timestamp(name, instant)
        return self

    def add_date(self,
                 name,
                 date):
        self.add_value(name, DbDateUtils.to_sql_date(date))
        return self

    def add_time(self,
                 name,
                 time):
        self.add_value(name, DbDateUtils.to_sql_timestamp_from_time(time))
        return self

    def add_timestamp_null_ignored(self,
                                   name,
                                   instant):
        if instant is not None:
            self.add_timestamp(name, instant)
        return self


    def add_timestamp_allow_null(self,
                                   name,
                                   instant):
        if instant is not None:
            self.add_timestamp(name, instant)
        else:
            self.add_value(name, None, Types.TIMESTAMP)
        return self

    def add_date_allow_null(self, name, date):
        if date is not None:
            self.add_date(name, date)
        else:
            self.add_value(self, name, None, Types.DATE)
        return self

    def add_time_allow_null(self, name, time):
        if time is not None:
            self.add_time(name, time)
        else:
            self.add_value(self, name, None, Types.TIME)
        return self

    def add_date_null_ignored(self, name, date):
        if date is not None:
            self.add_date(name, date)
        return self

    def add_time_null_ignored(self, name, time):
        if time is not None:
            self.add_time(name, time)
        return self

    def add_value_null_ignored(self, name, value):
        if value is not None:
            self.add_value(name, value)
        return self

    def add_date_time(self, name, date_time):
        value = date_time.strftime('%Y-%m-%d %H:%M:%S')
        self.add_value(name, value, None, Types.DATE)
        return self

    def add_date_time_null_future(self, name, date_time):
        if date_time is not None:
            self.add_date_time(name, date_time)
        else:
            self.add_value(self, name, None, Types.TIME)
        return self

    def add_date_time_null_ignored(self, name, date_time):
        if date_time is not None:
            self.add_date_time(name, date_time)
        return self

    def add_date_time_allow_null(self, name, date_time):
        if date_time is not None:
            self.add_date_time(name, date_time)
        return self

    def __str__(self):
        return 'Parameters'+self.get_values().__str__()