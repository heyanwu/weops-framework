import datetime

from dateutil.parser import parse


class FormatUtils(object):
    TIMEZONE = datetime.timezone(datetime.timedelta(hours=8))

    @classmethod
    def format_utc_time(cls, date_string):
        if not date_string:
            return date_string
        try:
            date_obj = parse(date_string)
        except ValueError:
            return date_string
        utc_time = date_obj.astimezone(cls.TIMEZONE)
        return utc_time.strftime("%Y-%m-%d %H:%M:%S")
