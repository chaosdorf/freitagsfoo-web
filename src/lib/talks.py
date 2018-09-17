from urllib.parse import quote_plus
from requests import Session
from requests.exceptions import ConnectionError, HTTPError
from .base import result

WIKI_URL_FORMAT = "https://wiki.chaosdorf.de/Freitagsfoo/{}"
JSON_URL = "https://www.chaosdorf.de/~ytvwld/freitagsfoo.json"
session = Session()


def table(date):
    try:
        r = session.get(JSON_URL)
        r.raise_for_status()
        data = r.json()
        talks = data["talks"]
    except (ConnectionError, HTTPError, ValueError):
        return result("error", last_step="fetch-json")
    for talk in talks:
        talk["wiki_link"] = WIKI_URL_FORMAT.format(
            str(date)
            + "#"
            + quote_plus(talk["title"]).replace("+", "_").replace("%", ".")
        )
    return result("ok", data=talks)
