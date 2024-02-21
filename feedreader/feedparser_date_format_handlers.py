import re


PAP_MEDIAROOM_DATE_FORMAT = re.compile(
    r"(\w{,3})\.,\s*(\d{2})/(\d{2})/(\d{4})\s*-\s*(\d{2}):(\d{2})"
)


def pap_mediaroom_date_format_handler(aDateString):
    """parse a UTC date in `pon., 02/12/2024 - 12:22` format"""
    _, month, day, year, hour, minute = PAP_MEDIAROOM_DATE_FORMAT.search(
        aDateString
    ).groups()
    return (int(year), int(month), int(day), int(hour), int(minute), 0, 0, 0, 0)
