"""The HHS Vertretungsplan component."""
from __future__ import annotations
from typing import Dict
from datetime import date, datetime, timedelta
from babel.dates import format_date, format_datetime
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
        today = datetime.strftime(date.today(), '%Y-%m-%d')
        vertretungen = self.hhs.vertretungen
        klassenliste = {}
        for vertretung in vertretungen:
            # skip old stuff before today
            if vertretung.datum < today:
                next
            # add to our list
            if vertretung.klasse in klassenliste:
                klassenliste[vertretung.klasse].append(asdict(vertretung))
            else:
                klassenliste[vertretung.klasse] = [asdict(vertretung)]
        klassenliste = self.beautify_data(klassenliste)

        """Now also get the status date of the data."""
        _LOGGER.debug(f"_asnyc_update_data: self.hhs.status={self.hhs.status}")
        raw_status = self.hhs.status
        time = datetime.strptime(raw_status, '%Y-%m-%d %H:%M')
        _LOGGER.debug(f"_asnyc_update_data: time={time}")
        status = format_datetime(time, 'EEEE H:mm', locale='de')
        _LOGGER.debug(f"_asnyc_update_data: status={status}")

        extra_states = {
            ATTR_VERTRETUNG: klassenliste,
            ATTR_STATUS: status
        }
        return extra_states


    def beautify_data(self, klassenliste: Dict) -> Dict:
        """Add day field."""
        for klasse in klassenliste.keys():
            for vertretung in klassenliste[klasse]:
                vertretung['day'] = format_date(datetime.strptime(vertretung['datum'], '%Y-%m-%d'), 'EEEE', locale='de')
        return klassenliste