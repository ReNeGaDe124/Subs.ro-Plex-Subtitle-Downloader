from homeassistant.components.text import TextEntity
from homeassistant.helpers.entity import DeviceInfo
import async_timeout
import logging
from .const import DOMAIN, DEVICE_NAME

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    config = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SubsroSearchDownloadInput(config, entry),
        SubsroSearchDeleteInput(config, entry)
    ])


class SubsroSearchDownloadInput(TextEntity):
    _attr_has_entity_name = True

    def __init__(self, config, entry):
        self._config = config
        self._entry = entry
        self._attr_name = "Search & Download Subtitles"
        self._attr_unique_id = "subsro_search_and_download_subtitles"
        self._attr_icon = "mdi:magnify"
        self._attr_mode = "text"
        self._attr_native_value = "" 

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=DEVICE_NAME,
        )

    async def async_set_value(self, value: str) -> None:
        if not value:
            return

        self._attr_native_value = value
        self.async_write_ha_state()

        headers = {
            "X-Auth-Token": self._config["secret"],
            "Content-Type": "application/json",
        }

        try:
            async with async_timeout.timeout(10):
                await self._config["session"].post(
                    f"{self._config['url']}/search_and_download_subtitles",
                    json={"keywords": value},
                    headers=headers,
                )
        except Exception as e:
            _LOGGER.error("Eroare căutare: %s", e)
        
        self._attr_native_value = ""
        self.async_write_ha_state()

class SubsroSearchDeleteInput(TextEntity):
    _attr_has_entity_name = True

    def __init__(self, config, entry):
        self._config = config
        self._entry = entry
        self._attr_name = "Search & Delete Subtitles"
        self._attr_unique_id = "subsro_search_and_delete_subtitles"
        self._attr_icon = "mdi:trash-can"
        self._attr_mode = "text"
        self._attr_native_value = "" 

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=DEVICE_NAME,
        )

    async def async_set_value(self, value: str) -> None:
        if not value:
            return

        self._attr_native_value = value
        self.async_write_ha_state()

        headers = {
            "X-Auth-Token": self._config["secret"],
            "Content-Type": "application/json",
        }

        try:
            async with async_timeout.timeout(10):
                await self._config["session"].post(
                    f"{self._config['url']}/search_and_delete_subtitles",
                    json={"keywords": value},
                    headers=headers,
                )
        except Exception as e:
            _LOGGER.error("Eroare ștergere: %s", e)
        
        self._attr_native_value = ""
        self.async_write_ha_state()