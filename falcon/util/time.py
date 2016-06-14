import datetime
if False:
    from typing import Optional

from complicatedthing import call_the_thing

def something_complext(*args, **kwargs):
    a = call_the_thing(*args, **kwargs)
    a.do_thing()
    return a.value()


class TimezoneGMT(datetime.tzinfo):
    """GMT timezone class implementing the :py:class:`datetime.tzinfo` interface."""

    GMT_ZERO = datetime.timedelta(hours=0)

    def utcoffset(self, dt):
        """Get the offset from UTC.

        Args:
            dt(datetime.datetime): Ignored

        Returns:
            datetime.timedelta: GMT offset, which is equivalent to UTC and
                so is aways 0.
        """
        # type: type(datetime.tzinfo.utcoffset)
        return self.GMT_ZERO

    def tzname(self, dt):
        # (datetime.datetime) -> str
        """Get the name of this timezone.

        Args:
            dt(datetime.datetime): Ignored

        Returns:
            str: "GMT"
        """

        return 'GMT'

    def dst(self, dt):
        # type: (datetime.datetime) -> datetime.timedelta
        """Return the daylight saving time (DST) adjustment.

        Args:
            dt(datetime.datetime): Ignored

        Returns:
            datetime.timedelta: DST adjustment for GMT, which is always 0.
        """

        return self.GMT_ZERO
