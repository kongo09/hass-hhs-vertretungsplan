from typing import final


DOMAIN = "hhs_vertretungsplan"
PLATFORMS = ["binary_sensor"]
DATA_CONFIG_ENTRY = "config_entry"
ATTRIBUTION = "Data provided by Heinrich-Hertz-Schule, Hamburg"

CONF_TUTOR_GROUP = "tutor_group"
CONF_USER = "user"
CONF_PASS = "password"

# set polling interval to 5 mins
POLLING_INTERVAL = 300

# configuration parameters
DEFAULT_NAME = "HHS Vertretungsplan"
PREFIX = "hhs"

# data keys
ATTR_VERTRETUNG = "vertretung"
ATTR_STATUS = "status"