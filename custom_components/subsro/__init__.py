import logging
import aiohttp
import async_timeout
from aiohttp import web

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.components.webhook import async_register as webhook_register
from homeassistant.components.webhook import async_unregister as webhook_unregister

from .const import DOMAIN, CONF_URL, CONF_SECRET, PLATFORMS, WEBHOOK_ID, SIGNAL_UPDATE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    
    hass.data.setdefault(DOMAIN, {})
    
    url = entry.data[CONF_URL]
    secret = entry.data[CONF_SECRET]
    
    hass.data[DOMAIN][entry.entry_id] = {
        "url": url,
        "secret": secret,
        "session": async_get_clientsession(hass)
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_webhook(hass, webhook_id, request):
        try:
            data = await request.json()
        except ValueError:
            return web.Response(status=400)

        if data.get("secret") != secret:
            _LOGGER.warning("Tentativă neautorizată de acces la webhook addon Subs.ro Plex Subtitle Downloader")
            return web.Response(status=401)

        async_dispatcher_send(hass, SIGNAL_UPDATE, data)
        return web.Response(text="OK")

    webhook_register(
        hass, DOMAIN, "Subs.ro Plex Subtitle Downloader Reverse API", WEBHOOK_ID, handle_webhook
    )

    async def handle_search(call: ServiceCall):
        keywords = call.data.get("keywords")
        if not keywords:
            _LOGGER.error("Lipsesc cuvintele cheie pentru căutare")
            return

        headers = {"X-Auth-Token": secret, "Content-Type": "application/json"}
        payload = {"keywords": keywords}
        api_endpoint = f"{url}/search_and_download"

        try:
            session = hass.data[DOMAIN][entry.entry_id]["session"]
            async with async_timeout.timeout(10):
                async with session.post(api_endpoint, json=payload, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error("Eroare API: %s", response.status)
                    else:
                        _LOGGER.info("Comanda de căutare pentru '%s' a fost trimisă.", keywords)
        except Exception as e:
            _LOGGER.error("Eroare la conectarea cu addon-ul Subs.ro Plex Subtitle Downloader: %s", e)

    hass.services.async_register(DOMAIN, "search_and_download", handle_search)

    async def handle_search_delete(call: ServiceCall):
        keywords = call.data.get("keywords")
        if not keywords:
            _LOGGER.error("Lipsesc cuvintele cheie pentru căutare")
            return

        headers = {"X-Auth-Token": secret, "Content-Type": "application/json"}
        payload = {"keywords": keywords}
        api_endpoint = f"{url}/search_and_delete_subtitles"

        try:
            session = hass.data[DOMAIN][entry.entry_id]["session"]
            async with async_timeout.timeout(10):
                async with session.post(api_endpoint, json=payload, headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error("Eroare API: %s", response.status)
                    else:
                        _LOGGER.info("Comanda de ștergere pentru '%s' a fost trimisă.", keywords)
        except Exception as e:
            _LOGGER.error("Eroare la conectarea cu addon-ul Subs.ro Plex Subtitle Downloader: %s", e)

    hass.services.async_register(DOMAIN, "search_and_delete", handle_search_delete)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    webhook_unregister(hass, WEBHOOK_ID)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok