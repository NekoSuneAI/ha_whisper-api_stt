import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_API_KEY, CONF_LANG, CONF_MODEL, CONF_URL, CONF_PROMPT, CONF_TEMPERATURE

@config_entries.HANDLERS.register(DOMAIN)
class WhisperSTTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Whisper STT."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Whisper STT", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): cv.string,
                vol.Optional(CONF_LANG, default="en-US"): cv.string,
                vol.Optional(CONF_MODEL, default="whisper-1"): cv.string,
                vol.Optional(CONF_URL, default="https://openai.nekosunevr.co.uk/v1/audio/transcriptions"): cv.string,
                vol.Optional(CONF_PROMPT, default=""): cv.string,
                vol.Optional(CONF_TEMPERATURE, default=0): vol.Coerce(float),
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WhisperSTTOptionsFlow(config_entry)


class WhisperSTTOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Whisper STT."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(CONF_LANG, default=options.get(CONF_LANG, "en-US")): cv.string,
                vol.Optional(CONF_MODEL, default=options.get(CONF_MODEL, "whisper-1")): cv.string,
                vol.Optional(CONF_URL, default=options.get(CONF_URL, "https://openai.nekosunevr.co.uk/v1/audio/transcriptions")): cv.string,
                vol.Optional(CONF_PROMPT, default=options.get(CONF_PROMPT, "")): cv.string,
                vol.Optional(CONF_TEMPERATURE, default=options.get(CONF_TEMPERATURE, 0)): vol.Coerce(float),
            })
        )
