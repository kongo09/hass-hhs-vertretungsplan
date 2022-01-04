from typing import Callable, Any, Dict
from custom_components.hhs_vertretungsplan import HHSDataUpdateCoordinator, HHSVertretungsEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.config_entries import ConfigEntry

import logging

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry, async_add_entities: Callable):
    """Setup binary sensor entity."""

    _LOGGER.debug(f"async_setup_entry called")

    entities = []
    coordinator = hass.data[DOMAIN][entry.entry_id]

    vertretungsStatus = VertretungsStatus(coordinator, entry)
    entities.append(vertretungsStatus)
    
    async_add_entities(entities, update_before_add=True)
    return True


class VertretungsStatus(HHSVertretungsEntity, BinarySensorEntity):
    """Representation of the Vertretung."""

    def __init__(self, coordinator: HHSDataUpdateCoordinator, config: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = None
        self._attr_state_class = "measurement"
        self._attr_entity_category = "diagnostic"
        self._config = config
        self._tutor_group = self._config.data[CONF_TUTOR_GROUP]
        self._attr_name = self._config.data[CONF_TUTOR_GROUP]
        self._attr_unique_id = self._attr_name

    @property
    def is_on(self) -> bool:
        return self._tutor_group in self.coordinator.data

    @property
    def state(self) -> str:
        """The sensor is on, when there is a Vertretung published."""
        if self.is_on:
            return "Notice"
        else:
            return "Nothing"

    @property
    def icon(self) -> str:
        """Return icon depending on state."""
        if self.is_on:
            return "mdi:checkbox-bell-circle-outline"
        else:
            return "mdi:bell-circle"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Only display at maximum 3 Vertretungen per tutor group."""
        vertretungen = self.coordinator.data[self._tutor_group]
        extra_state = {
            ATTR_KLASSE: "",
            ATTR_STUNDE: "",
            ATTR_FACH: "",
            ATTR_VERTRETER: "",
            ATTR_RAUM: "",
            ATTR_NACH: "",
            ATTR_TEXT: ""
        }
        num = vertretungen.count()
        if (num >=1):
            extra_state = vertretungen[1]
        return extra_state