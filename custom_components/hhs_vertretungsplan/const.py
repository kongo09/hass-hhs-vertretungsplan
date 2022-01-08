"""Constants for integration"""

DOMAIN = "hhs_vertretungsplan"
PLATFORMS = ["binary_sensor"]
DATA_CONFIG_ENTRY = "config_entry"
ATTRIBUTION = "Data provided by Heinrich-Hertz-Schule, Hamburg"

CONF_TUTOR_GROUP = "tutor_group"
CONF_USER = "user"
CONF_PASS = "password"

# set polling interval to 5 mins
POLLING_INTERVAL = 300

# but only in the morning between 6:00 and 15:00, format needs to be "%H:%M"
POLLING_START = "06:00"
POLLING_END = "15:00"

# configuration parameters
DEFAULT_NAME = "HHS Vertretungsplan"
PREFIX = "hhs"

# data keys
ATTR_VERTRETUNG = "vertretung"
ATTR_STATUS = "last_updated"