# command is: python manage.py refresh_token

import os
import json
import requests
import time
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from apps.iPM.models import Token

class Command(BaseCommand):
    help = 'Runs a background service to refresh tokens periodically'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting token maintenance cycle...'))
        token_maintenance_cycle()

def get_new_token():
    # Load environment variables
    token_url = os.getenv('token_url')
    app_key = os.getenv('app_key')
    app_secret = os.getenv('app_secret')

    # Debugging print statements (commented out for production use)
    # print(f"Token URL: {token_url}")
    # print(f"App Key: {app_key}")
    # print(f"App Secret: {app_secret}")

    if not token_url or not app_key or not app_secret:
        print("Missing environment variables. Please check .env file.")
        return None

    # Prepare request body for the POST request
    request_body = {
        "app_key": app_key,
        "app_secret": app_secret
    }

    try:
        # Make a POST request to the token URL (Disable SSL verification with 'verify=False')
        response = requests.post(token_url, json=request_body, verify=False)

        if response.status_code == 200:
            data = response.json()  # Parse the JSON response
            access_token = data.get('AccessToken')  # Get the AccessToken
            create_time_unix = int(data.get('CreateTime'))  # Unix timestamp
            expiration_seconds = int(data.get('Expires'))  # Expiration time in seconds

            # Convert create time from unix epoch to datetime (UTC) and then add 8 hours to convert to Philippine Time
            create_time = datetime.utcfromtimestamp(create_time_unix) + timedelta(hours=8)

            # Subtract 2 minutes from expiration and calculate new expiration time
            expiration_minutes = (expiration_seconds // 60) - 2
            expiration_time = create_time + timedelta(minutes=expiration_minutes)

            # Ensure only one token exists by either updating or creating a single record
            token_record, created = Token.objects.update_or_create(
                id=1,  # Assuming that you always want to have only one record with a specific ID (1)
                defaults={
                    'token': access_token,
                    'create_time': create_time,
                    'expiration': expiration_minutes
                }
            )
            # Log token generation success
            # print(f"Token saved: {access_token}, expires in {expiration_minutes} minutes.")
            print(f"Token generated, expires in {expiration_minutes} minutes (Philippine Time).")
            return expiration_time

        else:
            # Log if the token request fails with a non-200 status code
            print(f"Failed to retrieve token. Status code: {response.status_code}")
            return None

    except Exception as e:
        # Catch and log any errors during the token request
        print(f"An error occurred: {e}")
        return None

def token_maintenance_cycle():
    # Get the initial token and its expiration time
    expiration_time = get_new_token()

    while True:
        if expiration_time:
            # Get the current time in UTC and manually add 8 hours to convert to Philippine Time
            now = datetime.utcnow() + timedelta(hours=8)
            time_remaining = expiration_time - now  # Calculate the remaining time

            # Check if it's time to refresh the token (1 minute before expiration)
            if time_remaining.total_seconds() <= 60:
                # Refresh the token if it's about to expire
                expiration_time = get_new_token()
            else:
                # Sleep until it's time to refresh the token
                sleep_duration = time_remaining.total_seconds() - 60
                print(f"Sleeping for {sleep_duration} seconds until token renewal...")
                time.sleep(sleep_duration)
        else:
            # If no valid expiration time, retry token retrieval after 60 seconds
            print("No valid expiration time. Retrying token retrieval in 60 seconds.")
            time.sleep(60)

