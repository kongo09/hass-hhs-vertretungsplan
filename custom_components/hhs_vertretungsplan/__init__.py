"""The HHS Vertretungsplan component."""
from __future__ import annotations
from typing import Dict
from datetime import datetime, timedelta
from dataclasses import asdict

from hhs_vertretungsplan_parser.vertretungsplan_parser import AuthenticationException, HHSVertretungsplanParser

from .const import *

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup HHS Vertretungsplan from a config entry."""

    # setup the parser
    session = async_get_clientsession(hass)
    user = entry.data[CONF_USER]
    password = entry.data[CONF_PASS]
    hhs = HHSVertretungsplanParser(session, user, password)
    await hhs.load_data()

    # setup a coordinator
    coordinator = HHSDataUpdateCoordinator(hass, _LOGGER, hhs, timedelta(seconds=POLLING_INTERVAL))

    # refresh coordinator for the first time to load initial data
    await coordinator.async_config_entry_first_refresh()
    
    # store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # setup sensors
    for p in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, p)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    
    for p in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, p)

    hass.data[DOMAIN].pop(entry.entry_id)

    return True


class HHSDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Vertretungsplan data from the HHS."""

    def __init__(self, hass: HomeAssistant, _LOGGER, hhs: HHSVertretungsplanParser, update_interval: timedelta) -> None:
        """Initialize."""

        self.hhs = hhs
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)


    async def _async_update_data(self) -> Dict:
        """Update data via library."""

        try:
            """Ask the library to reload fresh data."""
            await self.hhs.load_data()
        except (ConnectionError, AuthenticationException) as error:
            raise UpdateFailed(error) from error

        """Let's return the raw list of all Vertretungen."""
        vertretungen = self.hhs.vertretungen
        klassenliste = {}
        for vertretung in vertretungen:
            if vertretung.klasse in klassenliste:
                klassenliste[vertretung.klasse].append(asdict(vertretung))
            else:
                klassenliste[vertretung.klasse] = [asdict(vertretung)]
        return self.beautify_data(klassenliste)


    def beautify_data(self, klassenliste: Dict) -> Dict:
        """Make the date better readable and combine Text and Nach fields."""
        for klasse in klassenliste.keys():
            for vertretung in klassenliste[klasse]:
                vertretung['datum'] = datetime.strptime(vertretung['datum'], '%Y-%m-%d').strftime('%A, %-d. %b')
                if len(vertretung['text']) > 0:
                    if len(vertretung['nach']) > 0:
                        vertretung['text'] = ', '.join([vertretung['text'], vertretung['nach']])
                else:
                    vertretung['text'] = vertretung['nach']

        return klassenliste