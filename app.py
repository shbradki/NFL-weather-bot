import requests
import nfl_data_py as nfl
import tweepy
import json 
from datetime import datetime, timedelta
import pytz
import os

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# Coordinates of each NFL stadium
stadium_dict = {
    'BAL' : (39.278088, -76.623322),
    'BUF' : (42.773773, -78.787460),
    'CAR' : (35.225845, -80.853607),
    'CHI' : (41.862366, -87.617256),
    'CIN' : (39.096306, -84.516846),
    'CLE' : (41.506054, -81.699548),
    'DEN' : (39.744129, -105.020828),
    'GB' : (44.501308, -88.062317),
    'JAX' : (30.323471, -81.636528),
    'KC': (39.048786, -94.484566),
    'MIA' : (25.957960, -80.239311),
    'NYG' : (40.813778, -74.074310),
    'NYJ' : (40.813778, -74.074310),
    'NE' : (42.091, -71.264),
    'PHI' : (39.900898, -75.168098),
    'PIT' : (40.446903, -80.015823),
    'SF' : (37.403158, -121.969831),
    'SEA' : (47.595097, -122.332245),
    'TB' : (27.975958, -82.503693),
    'TEN' : (36.166479, -86.771290),
    'WAS' : (38.90778, -76.86444),
    'ARI': (33.527283, -112.263275),
    'DAL': (32.747841, -97.093628),
    'ATL': (33.755489, -84.401993),
    'DET': (42.340115, -83.046341),
    'HOU': (29.684860, -95.411667),
    'IND': (39.759991, -86.163712),
    'LV': (36.090794, -115.183952),
    'LAC': (33.953587, -118.339630),
    'LA': (33.953587, -118.339630),
    'MIN': (44.973774, -93.258736),
    'NO': (29.951439, -90.081970)
}

weather_reports = []

# General Twitter Client steup
def twitter_api_setup():
    twitter_client = tweepy.Client(
        BEARER_TOKEN, API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
    )

    auth = tweepy.OAuth1UserHandler(
        API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)
    return twitter_client

# Returns current week in the NFL based on current date
def get_current_nfl_week(start_date, current_date):
    days_since_start = (current_date - start_date).days
    return (days_since_start // 7) + 1

# Returns hourly weather report for passed team value using OpenWeatherAPI
def get_weather(team):
    lat = stadium_dict[team][0]
    lon = stadium_dict[team][1]

    url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,alerts&appid={WEATHER_API_KEY}'
    response = requests.get(url)
    return response.json()

# Generates and returns this weeks NFL schedule
def gen_data():
    # Define the start date of the NFL 2024 season (Sept 5, 2024)
    season_start_date = datetime(2024, 9, 5)
    current_date = datetime.now()
    current_week = get_current_nfl_week(season_start_date, current_date)

    nfl_schedule_2024 = nfl.import_schedules(years=[2024])
    schedule = nfl_schedule_2024[nfl_schedule_2024['week'] == current_week]
    home_teams = schedule['home_team']
    away_teams = schedule['away_team']
    gametimes = schedule['gametime']
    dates = schedule['gameday']
    teams_dates_times = list(zip(home_teams, away_teams, dates, gametimes))
    return teams_dates_times

# Uses game date and game time to create datetime object and generate weather report lines based on target times
def get_game_weather(team, game_date, game_time):
    # Fetch weather data for the team's location
    weather_data = get_weather(team)

    # Convert game_date and game_time to datetime (in Eastern Time)
    eastern = pytz.timezone('US/Eastern')
    target_datetime = eastern.localize(datetime.strptime(f"{game_date} {game_time}", "%Y-%m-%d %H:%M"))

    # Generate list of target datetimes (rounded to the start of each hour) for each hour of the game
    target_datetimes = [
        target_datetime.replace(minute=0, second=0, microsecond=0) + timedelta(hours=i) for i in range(4)
    ]

    # Generate weather report by checking weather data for each target hour
    weather_report_lines = ''
    idx = 1

    for hourly in weather_data['hourly']:
        # Convert each hourly timestamp to a datetime object in Eastern Time
        entry_datetime = datetime.fromtimestamp(hourly['dt'], tz=pytz.utc).astimezone(eastern)
        entry_datetime = entry_datetime.replace(minute=0, second=0, microsecond=0)

        # Check if the entry matches any of the target datetimes
        if entry_datetime in target_datetimes:

            if hourly['weather'][0].get('main', 'no main available') == 'Snow':
                weather_type = 'snow'
            else:
                weather_type = 'rain'

            # Extract temperature and other weather data
            temperature = hourly.get('temp', "N/A")  # Temperature in Kelvin
            precipitation_chance = hourly.get('pop', 0) * 100  # Convert 'pop' to percentage
            fahrenheit_temp = (temperature - 273.15) * 9 / 5 + 32
            description = hourly['weather'][0].get('description', 'No description available')

            # Format the report line
            report_line = f"Q{idx}: {round(fahrenheit_temp)}°F, {int(precipitation_chance)}% {weather_type}, {description}"
            idx += 1
            weather_report_lines += report_line + '\n'

    # Check if any report lines were generated; if not, return a message
    if not weather_report_lines:
        return "No matching weather data found for the specified game hours."

    # Return the final report as a formatted string
    return weather_report_lines

# Iterates through each game in the week's schedule to generate weather report, returns list of reports
def gen_reports(day_of_week):
    games_data = gen_data()
    reports = []
    for game_info in games_data:
        try:
            home_team, away_team, game_date, game_time = game_info
            game_date_obj = datetime.strptime(game_date, "%Y-%m-%d")
            
            # Check if the game is on the specified day of the week
            if game_date_obj.strftime("%A") == day_of_week:
                game_weather_report = get_game_weather(home_team, game_date, game_time)
                
                # Format the final report for this game
                report = f"{home_team}(H) vs {away_team}(A) weather report:\n{game_weather_report}"
                reports.append(report)

        except Exception as e:
            print(f"Error generating report for {game_info}: {e}")
            continue
    return reports

# Can run it manually for testing
# twitter_client = twitter_api_setup()
weather_reports = gen_reports('Thursday')
for item in weather_reports:
    print(item)
#     twitter_client.create_tweet(text=item)

# Lambda handler function
def lambda_handler(event, context):
    day_of_week = event.get('day_of_week')  # Pass this from EventBridge
    weather_reports = gen_reports(day_of_week)
    twitter_client = twitter_api_setup()
    for item in weather_reports:
        twitter_client.create_tweet(text=item)
    return {
        'statusCode': 200,
        'body': json.dumps('Tweet(s) posted successfully')
    }
