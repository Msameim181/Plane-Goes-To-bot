import asyncio
import json
import typing
from typing import Any, Dict, List, Optional, Text, Tuple

import aiohttp
import uvicorn
from aiogram import Bot
from aiogram.bot.api import TELEGRAM_PRODUCTION, TelegramAPIServer
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from aiogram.utils.exceptions import TelegramAPIError
from env.settings import (
    APPLICATION_HOST,
    APPLICATION_PORT,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_BOT_WEBHOOK_URL,
    logger,
)
from fastapi import FastAPI
from fastapi.requests import Request
from FlightRadar24.api import FlightRadar24API
from utils.tools import flight_information_parser, start_background_task

live_locations = {}

class TelegramBot(Bot):

    @classmethod
    def name(cls) -> str:
        return "Telegram"
    
    def __init__(self, 
                 access_token: Optional[Text]):
        self.access_token = access_token
        super().__init__(token=access_token, parse_mode="HTML")

    async def send_text_message(
        self, recipient_id: Text, text: Text, 
        reply_markup=None, **kwargs: Any
    ) -> None:
        """Sends text message."""
        for message_part in text.strip().split("\n\n"):
            await self.send_message(recipient_id, message_part, 
                                    reply_markup=reply_markup, parse_mode="HTML")

    async def send_airplane_information(
        self, recipient_id: Text, flights_detail: List[Dict], 
        message_type: Text, live: bool = False
    ) -> None:
        """Sends text message."""
        for flight_detail in flights_detail:
            logger.debug(f"Sending flight detail: {flight_detail}")
            flight_detail_string = flight_information_parser(flight_detail)
            
            logger.debug(f"Sending flight detail: {flight_detail_string}")
            if message_type == 'message':
                message = await self.send_message(recipient_id, flight_detail_string, 
                                                  parse_mode="HTML")
                if live:
                    live_locations[recipient_id]=message.message_id
            elif message_type == 'edited_message':
                message_id = live_locations.get(recipient_id)
                await self.edit_message_text(flight_detail_string, recipient_id, message_id,
                                             parse_mode="HTML")



class PlaneGoesToBot:

    def __init__(self) -> None:
        self.rest_api_app = FastAPI()
        self.create_rest_api_route()
        self._set_telegram_webhook()
        self.background_process = set()

        logger.info("PlaneGoesToBot is ready.")
        logger.info(f"Telegram webhook url: {TELEGRAM_BOT_WEBHOOK_URL}")

    def create_rest_api_route(self):

        default_responses = {
            200: {"description": "Success"},
            400: {"description": "Bad Request"},
            404: {"description": "Not found"},
            403: {"description": "Unauthorized access"},
            422: {"description": "Unprocessable Entity"},
            500: {"description": "Internal Server Error"},
        }

        from pydantic import BaseModel
        class ResponseMessage(BaseModel):
            ok: bool = True
            description: Text = "Success"

            def __init__(self, ok: bool, description: Text):
                super().__init__()
                self.ok = ok
                self.description = description

        @self.rest_api_app.get('/', tags=["main"], responses=default_responses)
        @self.rest_api_app.get('/planeBot', tags=["Root"], responses=default_responses)
        @self.rest_api_app.post('/planeBot', tags=["Root"], responses=default_responses)
        async def rest_api_slack_main() -> ResponseMessage:
            return ResponseMessage(True, "Success")
        
        @self.rest_api_app.get('/planeBot/health', 
                               tags=["Health"], responses=default_responses)
        @self.rest_api_app.post('/planeBot/health', 
                                tags=["Health"], responses=default_responses)
        async def rest_api_slack_health() -> ResponseMessage:
            return ResponseMessage(True, "Success")

        @self.rest_api_app.get('/webhooks/telegram/webhook', 
                               tags=["Webhooks"], responses=default_responses)
        @self.rest_api_app.post('/webhooks/telegram/webhook', 
                                tags=["Webhooks"], responses=default_responses)
        async def rest_api_telegram_webhook(updates: Request) -> ResponseMessage:

            if not updates:
                return ResponseMessage(False, "No updates received.")
            
            try:
                updates = await updates.json()
                if not updates:
                    return ResponseMessage(False, "No updates received.")
            except Exception as e:
                logger.error(f"Failed to parse updates: {e}")
                return ResponseMessage(False, "Failed to parse updates.")
            
            try:
                message = updates.get('message', updates.get('edited_message', {}))
                message_type = 'message' if updates.get('message', None) \
                    else 'edited_message'
                logger.debug(f"Received message: {message}")
                if message.get('location', None) is None:
                    await self.telegram_channel.send_text_message(
                        message.get('chat', {}).get('id', None),
                        "Please share your location to receive flight details."
                    )
                    return ResponseMessage(False, "No location found.")
                
                start_background_task(
                    self.background_process,
                    self.information_retrieval, message, message_type
                )
                return ResponseMessage(True, "Success")
            
            except Exception as e:
                logger.exception(f"Failed to process updates: {e}")
                return ResponseMessage(False, "Failed to process updates.")

    async def information_retrieval(self, message: Dict[Any, Any], message_type: Text):
        user_location = message.get('location')
        if user_location and isinstance(user_location, dict):
            latitude = user_location.get('latitude', None)
            longitude = user_location.get('longitude', None)
            live = bool(user_location.get('live_period', None))

            if latitude and longitude:
                try:
                    if retrieved_information := self.flight_details(
                        (latitude, longitude)
                    ):
                        await self.telegram_channel.send_airplane_information(
                            message.get('chat', {}).get('id', None),
                            retrieved_information,
                            message_type,
                            live
                        )
                    else:
                        await self.telegram_channel.send_text_message(
                            message.get('chat', {}).get('id', None),
                            "No information found at this moment. "\
                                    "Please try again later."
                        )
                    return
                except Exception as e:
                    logger.exception(f"Failed to retrieve information: {e}")
                    await self.telegram_channel.send_text_message(
                        message.get('chat', {}).get('id', None),
                        "Failed to retrieve information. "\
                                "Please try again later."
                    )
                    return

        await self.telegram_channel.send_text_message(
            message.get('chat', {}).get('id', None),
            "Please share your current location with telegram "\
                    "options to receive flight details."
        )
        return
     
    def run(self) -> None:
        uvicorn.run(
            app=self.rest_api_app,
            host=APPLICATION_HOST,
            port=APPLICATION_PORT,
        )

    def _set_telegram_webhook(self) -> None:
        """Sets Telegram webhook."""
        logger.info("Setting Telegram webhook...")
        try:
            self.telegram_channel = TelegramBot(TELEGRAM_BOT_TOKEN)
            asyncio.run(self.telegram_channel.set_webhook(
                url=TELEGRAM_BOT_WEBHOOK_URL, 
                drop_pending_updates=True, 
                max_connections=1000))
            logger.info("Telegram webhook set.")
        except TelegramAPIError as e:
            logger.exception("Failed to set Telegram webhook.")
            raise e

    def flight_details(self, coordinates: Tuple):
        fr_api = FlightRadar24API()
        lat, lon = coordinates
        
        def get_square(lat, lon, distance):
            from geopy import Point as GPoint
            from geopy.distance import geodesic
            location = GPoint(lat, lon)
            north = geodesic(kilometers=distance).destination(location, 0)
            east = geodesic(kilometers=distance).destination(location, 90)
            south = geodesic(kilometers=distance).destination(location, 180)
            west = geodesic(kilometers=distance).destination(location, 270)
            return f"{north.latitude},{south.latitude},{west.longitude},{east.longitude}"
        
        logger.info(f"Getting flight details..., from: {get_square(lat, lon, 50)}")
        flights_detail = fr_api.get_flights(bounds=f"{get_square(lat, lon, 50)}")
        logger.info(f"Founds {len(flights_detail)} flights.")

        flights_information = []
        for flight in flights_detail:
            flight_full_information = fr_api.get_flight_details(flight)
            flight.set_flight_details(flight_full_information)
            flights_information.append({
                'id': flight.id,
                'number': flight.number,
                'callsign': flight.callsign,

                'airline_name': flight.airline_name,
                'airline_code': flight.airline_icao,

                'aircraft_name': flight.aircraft_model,
                'aircraft_code': flight.aircraft_code,
                'aircraft_history': [
                    {
                        'origin_airport': item.get("airport", {}).get(
                            "origin", {}).get("name", ""),
                        'destination_airport': item.get("airport", {}).get(
                            "destination", {}).get("name", "")
                    } for item in flight.aircraft_history if item.get("airport", {}) \
                    and item.get("airport", {}).get("origin", {}) \
                    and item.get("airport", {}).get("destination", {})
                ] if flight.aircraft_history else [],

                "origin_airport_country_name": flight.origin_airport_country_name,
                "origin_airport_country_code": flight.origin_airport_country_code,
                "origin_airport_name": flight.origin_airport_name,
                "origin_airport_code": flight.origin_airport_iata,

                "destination_airport_country_name": flight.destination_airport_country_name,
                "destination_airport_country_code": flight.destination_airport_country_code,
                "destination_airport_name": flight.destination_airport_name,
                "destination_airport_code": flight.destination_airport_iata,

                'altitude': flight.altitude,
                'heading': flight.heading,
                'speed': flight.ground_speed,
                'vertical_speed': flight.vertical_speed,
                'status': "On Ground" if flight.on_ground else "On Air",
                'status_text': flight.status_text,
                'status_icon': flight.status_icon,

                'time_details': flight.time_details,

            })

        return flights_information

