
<h1 align="center">✈️ I Wish I Knew Where That Plane Goes To</h1>
<p align="center">
  <img src="https://github.com/Msameim181/Plane-Goes-To-bot/blob/main/assets/a_plane.jpg" alt="AirPlane"/>
</p>

## Online Available

On Telegram: [@PlaneGoesTobot](https://t.me/PlaneGoesTobot)


## How to use

1. Clone the repo

2. Create a .env file with the following variables

```bash
NETWORK_NAME=plane_bot

TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_BOT_USERNAME=your_bot_username
TELEGRAM_BOT_WEBHOOK_URL=https://your.domain.com
TELEGRAM_BOT_WEBHOOK_DISABLE=0 # 0: Using your own domain, 1: Using ngrok domain

APPLICATION_PORT=8000
APPLICATION_HOST_NAME=plane_bot_app

NGROK_AUTHTOKEN=your_ngrok_token
NGROK_HOST_NAME=ngrok
NGROK_PORT=4040
NGROK_REGION=us
NGROK_VERSION="2"
```

3. Build the docker image

```bash
docker build -t plane_bot .
```

4. Create a docker network

```bash
docker network create plane_bot
```

5. Run the `docker compose` command

```bash
docker-compose up -d
```

6. Enjoy
