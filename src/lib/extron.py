from typing import Dict, List
from urllib.parse import urljoin
from requests import Session
from requests.exceptions import ConnectionError, HTTPError
import json
from .base import result
from .state import push_state

session = Session()


def fetch_available_inputs(config) -> List[dict]:
    inputs = []
    for idx in range(1, config["EXTRON_num-inputs"]+1):
        input = query_resource(config["EXTRON_url"], f"/video/in/{idx}")
        inputs.append({
            "name": input["name"],
            "active": input["detected_format"] != "No Signal",
        })
    return inputs


def fetch_selected_inputs(config) -> Dict[str, int]:
    result = query_resource(config["EXTRON_url"], f"/av/out/1/input")
    return {
        "audio": result["audio"],
        "video": result["main_video"],
    }


def fetch_state(config, redis_client, sse):
    print("fetching av data")
    state = {
        "available_inputs": fetch_available_inputs(config),
        "selected_inputs": fetch_selected_inputs(config),
        "info_beamer_at_port": config["INFO-BEAMER_extron-port"],
    }
    redis_client.set("extron_state", json.dumps(state))
    push_state(redis_client, sse)


def get_state(redis_client):
    data = redis_client.get("extron_state")
    if data:
        return result("ok", data=json.loads(data))
    return result("ok", data=None)


def check_pi_is_input(redis_client) -> bool:
    state = get_state(redis_client)
    assert state["status"] == "ok"
    return state["data"]["selected_inputs"]["video"] == state["data"]["info_beamer_at_port"]


def switch_to_pi(config, redis_client, sse):
    return switch_to_input(config, redis_client, sse, config["INFO-BEAMER_extron-port"])


def switch_to_input(config, redis_client, sse, port):
    resp = set_resource(config["EXTRON_url"], "/av/out/1/input/main", port)
    fetch_state(config, redis_client, sse)
    return resp


def query_resource(base_url: str, resource_uri: str) -> dict:
    return session.get(
        urljoin(base_url, "api/swis/resources"),
        params={"uri": resource_uri},
    ).json()[0]["result"]


def set_resource(base_url: str, resource_uri: str, value: object) -> dict:
    print([{"uri": resource_uri, "value": value}])
    response = session.post(
        urljoin(base_url, "api/swis/resources"),
        json=[{"uri": resource_uri, "value": value}],  # type: ignore
    ).json()[0]
    if "status" in response["meta"].keys():
        return result("error", reason=response["meta"]["status"], last_step="extron")
    return result("ok", data=response)
