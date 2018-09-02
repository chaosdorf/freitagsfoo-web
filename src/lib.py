from os import environ, path
from requests import Session
from requests.exceptions import ConnectionError, HTTPError

INFO_BEAMER_API = "https://info-beamer.com/api/v1/"
session = Session()

if path.exists("info-beamer-api-key"):
    file_name = "info-beamer-api-key"
else:
    file_name = "/run/secrets/INFO_BEAMER_API_KEY"
with open(file_name) as f:
    session.auth = ("", f.readline().strip())

def result(status, *, data=None, reason=None, last_step=None):
    res = dict()
    assert status in ("ok", "error")
    res["status"] = status
    if data:
        res["data"] = data
    if reason:
        assert status == "error"
        res["reason"] = reason
    if last_step:
        assert status == "error"
        res["last_step"] = last_step
    return res


def infobeamer_check(config):
    # Get all available devices.
    try:
        r = session.get(INFO_BEAMER_API + "device/list")
        r.raise_for_status()
    except (ConnectionError, HTTPError, ValueError):
        return result("error", last_step="info-beamer.com")
    # Find the right device.
    for dev in r.json()["devices"]:
        if dev["uuid"] == config["info-beamer_pi_uuid"]:
            device = dev
            break
    else:
        return result(
            "error",
            data={
                "id": int(config["info-beamer_pi_id"]),
                "uuid": config["info-beamer_pi_uuid"],
            },
            last_step="find-device"
        )
    # Check if the device is online and synced.
    if not device["is_online"]:
        return result("error", data=device, last_step="check-device-online")
    if not device["is_synced"]:
        return result("error", data=device, last_step="check-device-synced")
    # Check if the right setup is running.
    if device["setup"]["id"] != int(config["info-beamer_background_setup_id"]):
        return result(
            "error",
            data={
                "device": device,
                "actual": device["setup"],
                "expected": {
                    "id": int(config["info-beamer_background_setup_id"]),
                    "name": config["info-beamer_background_setup_name"],
                },
            },
            last_step="setup"
        )
    return result("ok", data=device)
