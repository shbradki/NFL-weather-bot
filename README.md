NFL Weather Bot

A Python-based AWS Lambda function that generates weather reports for NFL games and automatically tweets them using the Twitter API. This project leverages the nfl_data_py library for NFL schedules, the OpenWeather API for weather data, and AWS Lambda for serverless deployment.

Features

- Fetches up-to-date NFL schedules using nfl_data_py.
- Retrieves accurate weather data for NFL game locations using the OpenWeather API.
- Automatically generates and posts weather reports for NFL games to Twitter.
- Configured for AWS Lambda with Python 3.12 runtime and arm64 architecture.
- Uses an AWS Lambda layer for efficient handling of numpy and pandas.
- Supports AWS EventBridge Schedule (Cron) for automatic invocation.

Installation

Requirements:
- Python 3.12
- AWS account with permissions to create Lambda functions and layers
- Twitter Developer account for API keys
- OpenWeather API key

Clone the Repository

git clone https://github.com/<your-username>/NFL-weather-bot.git
cd NFL-weather-bot

Environment Variables

Set up the following environment variables in AWS Lambda or a .env file locally:

WEATHER_API_KEY: Your OpenWeather API key.
API_KEY: Twitter API key.
API_KEY_SECRET: Twitter API key secret.
BEARER_TOKEN: Twitter Bearer token.
ACCESS_TOKEN: Twitter access token.
ACCESS_TOKEN_SECRET: Twitter access token secret.

Deployment

Prepare Dependencies:

1. Create a virtual environment:
   python3 -m venv venv
   source venv/bin/activate

2. Install required dependencies:
   pip install -r requirements.txt -t .
   
3. Remove numpy and pandas directories (these will be provided via a Lambda layer):
   rm -rf numpy*
   rm -rf pandas*
   
Package the application

1. Zip the application and dependencies:
   zip -r lambda_deployment.zip .
   
2.Add the main application file:
   zip -g lambda_deployment.zip app.py

Deploy to AWS

1. Log in to the AWS Lambda Console and create a new function.
   
2. Set the runtime to Python 3.12 and architecture to arm64.
 
3. Upload the lambda_deployment.zip file as the function code.
   
4. Attach the AWS Lambda layer for numpy and pandas:
   arn:aws:lambda:<region>:724772057174:layer:Python312-Numpy-Pandas:1

5. Add the environment variables under the Configuration tab.

Usage

Manually Run Locally

Run the script locally for testing:
python app.py
The script will generate weather reports for NFL games on a specified day (e.g., Thursday) and print them to the console (you can uncomment out the "twitter_client = twitter_api_setup()
" and "twitter_client.create_tweet(text=item)" lines to also post the tweets manually)

Invoke on AWS Lambda

Set up an EventBridge rule or manually trigger the function with the following sample event:
{
  "day_of_week": "Thursday"
}

The Lambda function will:
Fetch the schedule for the specified day.
Generate weather reports.
Tweet the reports via the configured Twitter account.

Automate Invocation with AWS EventBridge Schedule (Cron)
1. Go to the AWS EventBridge Console and create a new rule.
2. Choose Event Source → Schedule.
3. Use a Cron Expression to define the schedule for invoking the function:
   - Example (Every Thursday at 10:00 AM UTC):
    0 10 ? * 5 *
4. Set the target to your deployed Lambda function.
5. Save the rule, and your function will now automatically run as scheduled.

Key Components

app.py
- The main script that handles:
  - Fetching NFL schedules.
  - Retrieving weather data for game locations.
  - Generating formatted weather reports.
  - Posting tweets via the Twitter API.
requirements.txt
- Contains the list of Python dependencies:
  requests
  nfl_data_py
  tweepy
  pytz
  datetime

Project Architecture
- NFL Schedules: Pulled using nfl_data_py.
- Weather Data: Retrieved for each stadium using the OpenWeather API.
- Twitter Integration: Posts game-specific weather updates to a Twitter account.




