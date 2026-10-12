"""Constants for Denkovi smartDEN IP Devices."""

from datetime import timedelta

DOMAIN = "denkovi-smartden-ip"
NAME = "Denkovi smartDEN IP Devices"
MANUFACTURER = "Denkovi"
MODEL_IP16R = "smartDEN IP-16R"
CONF_MODEL = "model"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 300
UPDATE_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

MODEL_IP16R_ID = "ip16r"
MODEL_IP32IN_ID = "ip32in"
MODEL_IP32IN = "smartDEN IP-32IN"

SUPPORTED_MODELS = {
    MODEL_IP16R_ID: MODEL_IP16R,
    MODEL_IP32IN_ID: MODEL_IP32IN,
}
