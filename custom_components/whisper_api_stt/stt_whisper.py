from typing import AsyncIterable
import aiohttp
import os
import tempfile
import voluptuous as vol
from homeassistant.components.stt import (
    AudioBitRates,
    AudioChannels,
    AudioCodecs,
    AudioFormats,
    Provider,
    SpeechMetadata,
    SpeechResult,
    SpeechResultState,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
import wave
import io
from .const import DOMAIN, CONF_API_KEY, CONF_LANG, CONF_MODEL, CONF_URL, CONF_PROMPT, CONF_TEMPERATURE

DEFAULT_LANG = "en-US"
OPENAI_STT_URL = "https://openai.nekosunevr.co.uk/v1/audio/transcriptions"

async def async_setup_entry(hass: HomeAssistant, config_entry):
    """Set up Whisper API STT from a config entry."""
    hass.data[DOMAIN] = OpenAISTTProvider(hass, config_entry)
    return True

class OpenAISTTProvider(Provider):
    """The Whisper API STT provider."""

    def __init__(self, hass, config_entry):
        """Initialize Whisper API STT provider."""
        self.hass = hass
        self._api_key = config_entry.data[CONF_API_KEY]
        self._language = config_entry.data.get(CONF_LANG, DEFAULT_LANG)
        self._model = config_entry.data.get(CONF_MODEL, 'whisper-1')
        self._url = config_entry.data.get(CONF_URL, OPENAI_STT_URL)
        self._prompt = config_entry.data.get(CONF_PROMPT, "")
        self._temperature = config_entry.data.get(CONF_TEMPERATURE, 0)

    @property
    def default_language(self) -> str:
        return self._language.split(',')[0]

    @property
    def supported_languages(self) -> list[str]:
        return self._language.split(',')

    @property
    def supported_formats(self) -> list[AudioFormats]:
        return [AudioFormats.WAV]

    @property
    def supported_codecs(self) -> list[AudioCodecs]:
        return [AudioCodecs.PCM]

    @property
    def supported_bit_rates(self) -> list[AudioBitRates]:
        return [AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[AudioSampleRates]:
        return [AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[AudioChannels]:
        return [AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(self, metadata: SpeechMetadata, stream: AsyncIterable[bytes]) -> SpeechResult:
        data = b''
        async for chunk in stream:
            data += chunk

        if not data:
            return SpeechResult("", SpeechResultState.ERROR)

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                with wave.open(temp_file, 'wb') as wav_file:
                    wav_file.setnchannels(metadata.channel)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(metadata.sample_rate)
                    wav_file.writeframes(data)
                temp_file_path = temp_file.name

            headers = {'Authorization': f'Bearer {self._api_key}'}
            form = aiohttp.FormData()
            form.add_field('file', open(temp_file_path, 'rb'), filename='audio.wav', content_type='audio/wav')
            form.add_field('language', self._language)
            form.add_field('model', self._model)
            if self._prompt:
                form.add_field('prompt', self._prompt)
            form.add_field('temperature', str(self._temperature))

            async with aiohttp.ClientSession() as session:
                async with session.post(self._url, data=form, headers=headers) as response:
                    if response.status == 200:
                        json_response = await response.json()
                        return SpeechResult(json_response.get("text", ""), SpeechResultState.SUCCESS)
                    else:
                        return SpeechResult("", SpeechResultState.ERROR)
        finally:
            os.remove(temp_file_path)
