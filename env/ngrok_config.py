
import requests

def get_ngrok_public_url(ngrok_url: str):
    response = requests.get(ngrok_url)
    if response.status_code == 200:
        return response.json()['tunnels'][0]['public_url']
    else:
        return None


def fix_ngrok_configs(APP_ENV_DIR: str):
    import os
    import sys
    from pathlib import Path
    import environ
    import yaml

    env = environ.Env()
    environ.Env.read_env()
    NETWORK_NAME = env('NETWORK_NAME')
    NGROK_AUTHTOKEN = env('NGROK_AUTHTOKEN')
    NGROK_REGION = env('NGROK_REGION')
    NGROK_VERSION = env('NGROK_VERSION')
    APPLICATION_PORT = env('APPLICATION_PORT')
    APPLICATION_HOST_NAME = env('APPLICATION_HOST_NAME')
    ngrok_config = {
        'authtoken': NGROK_AUTHTOKEN,
        'region': NGROK_REGION,
        'version': NGROK_VERSION,
        'tunnels': {
            'telegram': {
                'addr': f"{APPLICATION_HOST_NAME}.{NETWORK_NAME}:{APPLICATION_PORT}",
                'proto': 'http',
            }
        },
    }
    with open(os.path.join(APP_ENV_DIR, 'ngrok.yml'), 'w') as f:
        yaml.dump(ngrok_config, f)

if __name__ == '__main__':
    from pathlib import Path
    import os
    fix_ngrok_configs(os.path.join(Path(__file__).parent.parent, 'env'))