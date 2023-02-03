from datetime import date, datetime
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
    old_data = json.loads(redis_client.get("talks"))
    result = fetch_for_date(date.today())
    if result["status"] == "ok":
        print("fetched talks data")
        if old_data is not None:
            result["data"]["current"] = old_data.get("current")
        else:
            result["data"]["current"] = None
        redis_client.set("talks", json.dumps(result["data"]))
        push_state(redis_client, sse)
    else:
        print("error: failed to fetch talks data")


def _set_current_talk(redis_client, sse, to_set):
    data = json.loads(redis_client.get("talks"))
    if data is None:
        return result("error", last_step="fetch-json")
    data["current"] = to_set
    redis_client.set("talks", json.dumps(data))
    push_state(redis_client, sse)
    return result("ok")


def begin_talk(redis_client, sse, index):
    return _set_current_talk(redis_client, sse, {
        "index": index,
        "started_at": datetime.now().timestamp(),
    })


def end_talk(redis_client, sse):
    return _set_current_talk(redis_client, sse, None)


def list(redis_client):
    data = redis_client.get("talks")
    if data is None:
        return result("error", last_step="fetch-json")
    return result("ok", data=json.loads(data))
