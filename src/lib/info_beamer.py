from requests import Session
from requests.exceptions import ConnectionError, HTTPError
from .base import read_secret, result

INFO_BEAMER_API = "https://info-beamer.com/api/v1/"
session = Session()


session.auth = ("", read_secret("INFO_BEAMER_API_KEY"))


def infobeamer_check(config):
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
    return result("ok", data=device)


def infobeamer_assign_correct_setup(config):
    return _infobeamer_assign_setup(
        int(config["INFO-BEAMER_pi-id"]),
        int(config["INFO-BEAMER_talks-setup-id"])
    )


def get_state():
    return result("ok", data="background")  # TODO


def begin_talks(config):
    return _infobeamer_send_command(
        int(config["INFO-BEAMER_pi-id"]),
        "freitagsfoo/screen",
        "title",
    )


def end_talks(config):
    return _infobeamer_send_command(
        int(config["INFO-BEAMER_pi-id"]),
        "freitagsfoo/screen",
        "initial"
    )


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
