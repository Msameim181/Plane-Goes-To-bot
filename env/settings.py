import environ
from env.logger import logger_creator
from env.ngrok_config import get_ngrok_public_url

logger = logger_creator('plane_goes_to_bot')

env = environ.Env()
environ.Env.read_env()

# Network name
NETWORK_NAME = env('NETWORK_NAME')

REST_API_FREAMWORK = 'fastapi'
APPLICATION_NAME = 'plane_goes_to_bot'
APPLICATION_PORT = int(env('APPLICATION_PORT'))
APPLICATION_HOST_NAME = env('APPLICATION_HOST_NAME')
APPLICATION_HOST = "0.0.0.0"

# Ngrok information
NGROK_AUTHTOKEN = env('NGROK_AUTHTOKEN')
NGROK_HOST_NAME = env('NGROK_HOST_NAME')
NGROK_PORT = env('NGROK_PORT')
NGROK_REGION = env('NGROK_REGION')
NGROK_VERSION = env('NGROK_VERSION')

# Telegram bot information
TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')
TELEGRAM_BOT_USERNAME = env('TELEGRAM_BOT_USERNAME')
TELEGRAM_BOT_WEBHOOK_DISABLE = int(env('TELEGRAM_BOT_WEBHOOK_DISABLE'))
TELEGRAM_BOT_WEBHOOK_URL = get_ngrok_public_url(
    ngrok_url=f'http://{NGROK_HOST_NAME}.{NETWORK_NAME}:{NGROK_PORT}/api/tunnels'
    ) if TELEGRAM_BOT_WEBHOOK_DISABLE else env('TELEGRAM_BOT_WEBHOOK_URL')
if TELEGRAM_BOT_WEBHOOK_URL and TELEGRAM_BOT_WEBHOOK_URL.endswith('/'):
    TELEGRAM_BOT_WEBHOOK_URL = TELEGRAM_BOT_WEBHOOK_URL[:-1]
TELEGRAM_BOT_WEBHOOK_URL = f'{TELEGRAM_BOT_WEBHOOK_URL}/webhooks/telegram/webhook'

TELEGRAM_BOT_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/'

