from requests import Session
from requests.exceptions import ConnectionError, HTTPError
import json

from .state import push_state
from .base import read_secret, result
from .extron import check_pi_is_input

INFO_BEAMER_API = "https://info-beamer.com/api/v1/"
session = Session()


session.auth = ("", read_secret("INFO_BEAMER_API_KEY"))


def infobeamer_check(config, redis_client):
    # Get all available devices.
    try:
        r = session.get(INFO_BEAMER_API + "device/list")
        r.raise_for_status()
        data = r.json()
    except (ConnectionError, HTTPError, ValueError):
        return result("error", last_step="info-beamer.com")
    # Find the right device.
    for dev in data["devices"]:
        if dev["id"] == int(config["INFO-BEAMER_pi-id"]):
            device = dev
            break
    else:
        return result(
            "error",
            data={
                "id": int(config["INFO-BEAMER_pi-id"]),
            },
            last_step="find-device"
        )
    # Check if the right setup is running.
    if device["setup"]["id"] != int(config["INFO-BEAMER_talks-setup-id"]):
        return result(
            "error",
            data={
                "device": device,
                "actual": device["setup"],
                "expected": {
                    "id": int(config["INFO-BEAMER_talks-setup-id"]),
                    "name": config["INFO-BEAMER_talks-setup-name"],
                },
            },
            last_step="setup"
        )
    # Check if the device is online and synced.
    if not device["is_online"]:
        return result("error", data=device, last_step="check-device-online")
    if not device["is_synced"]:
        return result("error", data=device, last_step="check-device-synced")
    # Check if we have a state
    if redis_client.get("info_beamer_state") is None:
        return result("error", data=device, last_step="state")
    if not check_pi_is_input(redis_client):
        return result("error", data=device, last_step="extron")
    return result("ok", data=device)


def infobeamer_assign_correct_setup(config, redis_client):
    res = _infobeamer_assign_setup(
        int(config["INFO-BEAMER_pi-id"]),
        int(config["INFO-BEAMER_talks-setup-id"])
    )
    if res["status"] == "ok":
        redis_client.set("info_beamer_state", json.dumps({
            "is_background": True,
            "announced_talk": None,
        }))
    return res


def get_state(redis_client):
    data = redis_client.get("info_beamer_state")
    if data:
        return result("ok", data=json.loads(data))
    return result("ok", data={
        "is_background": None,
        "announced_talk": None,
    })


def begin_talks(config, redis_client, sse):
    res = _infobeamer_send_command(
        int(config["INFO-BEAMER_pi-id"]),
        "freitagsfoo/screen",
        "title",
    )
    if res["status"] == "ok":
        redis_client.set("info_beamer_state", json.dumps({
            "is_background": False,
            "announced_talk": None,
        }))
        push_state(redis_client, sse)
    return res


def announce_talk(config, redis_client, sse, talk_index):
    if talk_index == -1:
        res = _infobeamer_send_command(
            int(config["INFO-BEAMER_pi-id"]),
            "freitagsfoo/screen",
            "talks"
        )
        if res["status"] == "error":
            return res
        if res["status"] == "ok":
            redis_client.set("info_beamer_state", json.dumps({
                "is_background": False,
                "announced_talk": None,
            }))
        return res
    res = _infobeamer_send_command(
        int(config["INFO-BEAMER_pi-id"]),
        "freitagsfoo/screen",
        "next"
    )
    if res["status"] == "error":
        return res
    res = _infobeamer_send_command(
        int(config["INFO-BEAMER_pi-id"]),
        "next_screen/talk_index",
        talk_index + 1
    )
    if res["status"] == "ok":
        redis_client.set("info_beamer_state", json.dumps({
            "is_background": False,
            "announced_talk": talk_index,
        }))
        push_state(redis_client, sse)
    return res


def end_talks(config, redis_client, sse):
    res = _infobeamer_send_command(
        int(config["INFO-BEAMER_pi-id"]),
        "freitagsfoo/screen",
        "initial"
    )
    if res["status"] == "ok":
        redis_client.set("info_beamer_state", json.dumps({
            "is_background": True,
            "announced_talk": None,
        }))
        push_state(redis_client, sse)
    return res


def _infobeamer_assign_setup(pi_id, setup_id):
    try:
        r = session.post(
            INFO_BEAMER_API + "device/" + str(pi_id),
            data={"setup_id": setup_id},
        )
    except ConnectionError:
        return result("error", last_step="info-beamer.com")
    if not r.ok:
        return result("error", last_step="assign-setup")
    try:
        data = r.json()
    except ValueError:
        return result("error", last_step="info-beamer.com")
    if not data.get("ok"):
        return result("error", last_step="assign-setup")
    return result("ok")


def _infobeamer_send_command(pi_id, path, data):
    try:
        r = session.post(
            INFO_BEAMER_API + "device/" + str(pi_id) + "/node/" + path,
            data={"data": data},
        )
    except ConnectionError:
        return result("error", last_step="info-beamer.com")
    if not r.ok:
        return result("error", last_step="send-command")
    try:
        data = r.json()
    except ValueError:
        return result("error", last_step="info-beamer.com")
    if not data.get("ok"):
        return result("error", last_step="send-command")
    return result("ok")
