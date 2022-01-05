from typing import Callable, Any, Dict
from custom_components.hhs_vertretungsplan import HHSDataUpdateCoordinator
from hhs_vertretungsplan_parser.vertretungsplan_parser import Vertretung
from dataclasses import asdict

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry

import logging

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry, async_add_entities: Callable):
    """Setup binary sensor entity."""

    _LOGGER.debug(f"async_setup_entry called")

    entities = []
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities.append(VertretungsStatus(coordinator, entry))
    
    async_add_entities(entities, update_before_add=True)
    return True


class VertretungsStatus(CoordinatorEntity, BinarySensorEntity):
    """Representation of the Vertretung."""

    def __init__(self, coordinator: HHSDataUpdateCoordinator, config: ConfigEntry):
        super().__init__(coordinator)

        # internal
        self._available = True
        self._config = config
        self._tutor_group = self._config.data[CONF_TUTOR_GROUP]

        # attributes
        self._attr_state_class = "measurement"
        self._attr_entity_category = "diagnostic"
        self._attr_name = PREFIX + " " + self._config.data[CONF_TUTOR_GROUP]
        self._attr_unique_id = hash(self._attr_name)
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def is_on(self) -> bool:
        return self._tutor_group in self.coordinator.data

    @property
    def state(self) -> str:
        """The sensor is on, when there is a Vertretung published."""
        if self.is_on:
            return "Vertretung"
        else:
            return "Regulär"

    @property
    def icon(self) -> str:
        """Return icon depending on state."""
        if self.is_on:
            return "mdi:bell-circle"
        else:
            return "mdi:checkbox-blank-circle-outline"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Store all Vertretungen in a dynamic"""
        extra_state = {ATTR_KEY: list(Vertretung)}
        if self._tutor_group in self.coordinator.data:
            extra_state = {ATTR_KEY: self.coordinator.data[self._tutor_group]}
        #     vertretungen = self.coordinator.data[self._tutor_group]
        #     num = 0
        #     for vertretung in vertretungen:
        #         key = ATTR_KEY + f"_{num}"
        #         extra_state[key] = asdict(vertretung)
        #         num += 1
        
        return  extra_state