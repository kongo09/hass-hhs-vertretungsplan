from typing import Callable, Any, Dict
from custom_components.hhs_vertretungsplan import HHSDataUpdateCoordinator
from hhs_vertretungsplan_parser.const import KEY_ALLE

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.util import slugify

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
        self._attr_attribution = ATTRIBUTION
        self._attr_state_class = "measurement"
        self._attr_entity_category = "diagnostic"
        self._attr_name = self._tutor_group
        self._attr_unique_id = self._tutor_group
        self.entity_id = "." + slugify(PREFIX + "_" + self._tutor_group)
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def is_on(self) -> bool:
        return self._tutor_group in self.coordinator.data[ATTR_VERTRETUNG]

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
        vertretung_state = {}
        vertretungen = self.coordinator.data[ATTR_VERTRETUNG]
        if self._tutor_group in vertretungen:
            vertretung_state = vertretungen[self._tutor_group]

        # add catch-all items for the whole year
        year = ''.join(filter(str.isdigit, self._tutor_group)) + KEY_ALLE
        if year in vertretungen:
            vertretung_state.extend(vertretungen[year])

        # add catch-all items for the whole school
        if KEY_ALLE in vertretungen:
            vertretung_state.extend(vertretungen[KEY_ALLE])
        
        return  {
            ATTR_STATUS: self.coordinator.data[ATTR_STATUS],
            ATTR_VERTRETUNG: vertretung_state
        }