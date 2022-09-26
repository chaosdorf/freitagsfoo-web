from datetime import date
from urllib.parse import quote_plus
from requests import Session
from requests.exceptions import ConnectionError, HTTPError
import json
from .base import result
from .state import push_state

WIKI_URL_FORMAT = "https://wiki.chaosdorf.de/Freitagsfoo/{}"
JSON_URL = "https://www.chaosdorf.de/~ytvwld/freitagsfoo.json"
session = Session()


def fetch_for_date(date):
    try:
        r = session.get(JSON_URL)
        r.raise_for_status()
        data = r.json()
    except (ConnectionError, HTTPError, ValueError):
        return result("error", last_step="fetch-json")
    data["wiki_link"] = WIKI_URL_FORMAT.format(data["date"])
    for talk in data["talks"]:
        talk["wiki_link"] = WIKI_URL_FORMAT.format(
            str(date)
            + "#"
            + quote_plus(talk["title"]).replace("+", "_").replace("%", ".")
        )
    return result("ok", data=data)


def fetch(redis_client, sse):
    result = fetch_for_date(date.today())
    if result["status"] == "ok":
        print("fetched talks data")
        redis_client.set("talks", json.dumps(result["data"]))
        push_state(redis_client, sse)
    else:
        print("error: failed to fetch talks data")


def list(redis_client):
    data = redis_client.get("talks")
    if data is None:
        return result("error", last_step="fetch-json")
    return result("ok", data=json.loads(data))
