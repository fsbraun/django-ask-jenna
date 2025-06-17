import os

from django.conf import settings


ASK_JENNA_API_KEY = getattr(settings, 'ASK_JENNA_API_KEY', os.environ.get('ASK_JENNA_API_KEY'))
ASK_JENNA_SERVICE = getattr(settings, 'ASK_JENNA_SERVICE', os.environ.get('ASK_JENNA_SERVICE', 'openai'))
ASK_JENNA_MODEL = getattr(settings, 'ASK_JENNA_MODEL', os.environ.get('ASK_JENNA_MODEL', 'gpt-3.5-turbo'))
ASK_JENNA_MAX_TOKENS = int(getattr(settings, 'ASK_JENNA_MAX_TOKENS', os.environ.get('ASK_JENNA_MAX_TOKENS', 1000)))
ASK_JENNA_TEMPERATURE = float(getattr(settings, 'ASK_JENNA_TEMPERATURE', os.environ.get('ASK_JENNA_TEMPERATURE', 0.7)))
ASK_JENNA_TOP_P = float(getattr(settings, 'ASK_JENNA_TOP_P', os.environ.get('ASK_JENNA_TOP_P', 1.0)))
ASK_JENNA_FREQUENCY_PENALTY = float(getattr(settings, 'ASK_JENNA_FREQUENCY_PENALTY', os.environ.get('ASK_JENNA_FREQUENCY_PENALTY', 0.0)))
ASK_JENNA_PRESENCE_PENALTY = float(getattr(settings, 'ASK_JENNA_PRESENCE_PENALTY', os.environ.get('ASK_JENNA_PRESENCE_PENALTY', 0.0)))
ASK_JENNA_TIMEOUT = int(getattr(settings, 'ASK_JENNA_TIMEOUT', os.environ.get('ASK_JENNA_TIMEOUT', 10)))
