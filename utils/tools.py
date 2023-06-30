import asyncio
from typing import Any, Callable, Dict, Text
from datetime import datetime
import timezonefinder, pytz

def start_background_task(
    background_process: set,
    target: Callable[..., Any], *args: Any) -> None:
    """Starts a background task."""
    task = asyncio.create_task(target(*args))
    background_process.add(task)
    task.add_done_callback(background_process.discard)


def get_time_by_location(latitude, longitude):
    tf = timezonefinder.TimezoneFinder()
    timezone_str = tf.certain_timezone_at(lat=latitude, lng=longitude)
    if timezone_str is None:
        return None
    timezone = pytz.timezone(timezone_str)
    dt = datetime.utcnow()
    current_time = dt + timezone.utcoffset(dt)
    return current_time.strftime('%Y-%m-%d %H:%M:%S')


def flight_information_parser(flight_detail: Dict[Text, Any]) -> Text:
    """Parses flight information."""
    timezone = pytz.timezone('Asia/Tehran')
    aircraft_history = "\n".join([
        f"\t\t\t - <code>{item.get('origin_airport')} -> "\
                f"{item.get('destination_airport')}</code>"
        for item in flight_detail.get('aircraft_history', [])
    ])
    t_scheduled_departure = flight_detail.get('time_details', {}).get(
        'scheduled', {}).get('departure', "") if isinstance(
        flight_detail.get('time_details', {}), dict) \
        and isinstance(flight_detail.get('time_details', {}).get(
        'scheduled', {}), dict) else ""
    t_scheduled_arrival = flight_detail.get('time_details', {}).get(
        'scheduled', {}).get('arrival', "") if isinstance(
        flight_detail.get('time_details', {}), dict) \
        and isinstance(flight_detail.get('time_details', {}).get(
        'scheduled', {}), dict) else ""
    t_real_departure = flight_detail.get('time_details', {}).get(
        'real', {}).get('departure', "") if isinstance(
        flight_detail.get('time_details', {}), dict) \
        and isinstance(flight_detail.get('time_details', {}).get(
        'real', {}), dict) else ""
    t_real_arrival = flight_detail.get('time_details', {}).get(
        'real', {}).get('arrival', "") if isinstance(
        flight_detail.get('time_details', {}), dict) \
        and isinstance(flight_detail.get('time_details', {}).get(
        'real', {}), dict) else ""
    t_estimated_departure = flight_detail.get('time_details', {}).get(
        'estimated', {}).get('departure', "") if isinstance(
        flight_detail.get('time_details', {}), dict) \
        and isinstance(flight_detail.get('time_details', {}).get(
        'estimated', {}), dict) else ""
    t_estimated_arrival = flight_detail.get('time_details', {}).get(
        'estimated', {}).get('arrival', "") if isinstance(
        flight_detail.get('time_details', {}), dict) \
        and isinstance(flight_detail.get('time_details', {}).get(
        'estimated', {}), dict) else ""

    return f"""<b>Flight Information</b>
<b>Flight ID:</b> {flight_detail.get('id')}
<b>Flight Number:</b> {flight_detail.get('number')}
<b>Flight CallSign:</b> {flight_detail.get('callsign')}
--------------------
<b>Airline Name:</b> {flight_detail.get('airline_name')} ({flight_detail.get('airline_code')})
--------------------
<b>Aircraft Name:</b> {flight_detail.get('aircraft_name')} ({flight_detail.get('aircraft_code')})
--------------------
<b>Origin Airport Country Name:</b> {flight_detail.get('origin_airport_country_name')} ({flight_detail.get('origin_airport_country_code')})
<b>Origin Airport Name:</b> {flight_detail.get('origin_airport_name')} ({flight_detail.get('origin_airport_code')})
--------------------
<b>Destination Airport Country Name:</b> {flight_detail.get('destination_airport_country_name')} ({flight_detail.get('destination_airport_country_code')})
<b>Destination Airport Name:</b> {flight_detail.get('destination_airport_name')} ({flight_detail.get('destination_airport_code')})
--------------------
<b>Altitude:</b> {flight_detail.get('altitude')}
<b>Heading:</b> {flight_detail.get('heading')}
<b>Speed:</b> {flight_detail.get('speed')}
<b>Vertical Speed:</b> {flight_detail.get('vertical_speed')}
<b>Status:</b> {flight_detail.get('status')}
<b>Status Text:</b> {flight_detail.get('status_text')}
--------------------
<b>Time Details:</b>
    Scheduled: 
        Departure: <code>{timezone.localize(datetime.fromtimestamp(
                    int(t_scheduled_departure))).strftime("%Y-%m-%d %H:%M:%S")
                    if t_scheduled_departure and isinstance(t_scheduled_departure, int) 
                    else t_scheduled_departure}</code>
        Arrival: <code>{timezone.localize(datetime.fromtimestamp(
                    int(t_scheduled_arrival))).strftime("%Y-%m-%d %H:%M:%S")
                    if t_scheduled_arrival and isinstance(t_scheduled_arrival, int) 
                    else t_scheduled_arrival}</code>
    Real:
        Departure: <code>{datetime.fromtimestamp(
                    int(t_real_departure)).strftime("%Y-%m-%d %H:%M:%S") 
                    if t_real_departure and isinstance(t_real_departure, int) 
                    else t_real_departure}</code>
        Arrival: <code>{datetime.fromtimestamp(
                    int(t_real_arrival)).strftime("%Y-%m-%d %H:%M:%S") 
                    if t_real_arrival and isinstance(t_real_arrival, int) 
                    else t_real_arrival}</code>
    Estimated:
        Departure: <code>{datetime.fromtimestamp(
                    int(t_estimated_departure)).strftime("%Y-%m-%d %H:%M:%S") 
                    if t_estimated_departure and isinstance(t_estimated_departure, int) 
                    else t_estimated_departure}</code>
        Arrival: <code>{datetime.fromtimestamp(
                    int(t_estimated_arrival)).strftime("%Y-%m-%d %H:%M:%S") 
                    if t_estimated_arrival and isinstance(t_estimated_arrival, int) 
                    else t_estimated_arrival}</code>
--------------------
<b>Aircraft History:</b> \n{aircraft_history}
--------------------
Powered by <code>FlightRadar24</code>
"""