from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo
import async_timeout
import logging
from .const import DOMAIN, DEVICE_NAME

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    config = hass.data[DOMAIN][entry.entry_id]
    buttons = [
        ("Download for Latest Video", "/download_subtitle_for_latest_video", "mdi:file-video"),
        ("Download Missing Subtitles", "/download_missing_subtitles", "mdi:subtitles"),
        ("Cleanup Orphaned Subtitles", "/cleanup_orphaned_subtitles", "mdi:broom"),
    ]
    async_add_entities([SubsroButton(config, entry, *b) for b in buttons])

class SubsroButton(ButtonEntity):
    _attr_has_entity_name = True
    def __init__(self, config, entry, name, endpoint, icon):
        self._config, self._entry, self._endpoint = config, entry, endpoint
        self._attr_name, self._attr_icon = name, icon
        self._attr_unique_id = f"subsro_{endpoint}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=DEVICE_NAME,
        )

    async def async_press(self) -> None:
        headers = {"X-Auth-Token": self._config["secret"]}
        try:
            async with async_timeout.timeout(10):
                await self._config["session"].post(
                    f"{self._config['url']}{self._endpoint}", 
                    headers=headers
                )
        except Exception as e:

            _LOGGER.error("Eroare buton %s: %s", self._attr_name, e)






