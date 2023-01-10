import tweepy
from dotenv import load_dotenv
import os

load_dotenv()

class TweepyObject:
    __api_key = os.environ['API_KEY']
    __api_key_secret = os.environ['API_KEY_SECRET']

    __access_token = os.environ['ACCESS_TOKEN']
    __access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

    def __init__(self):
        self.auth = tweepy.OAuthHandler(self.__api_key, self.__api_key_secret)
        self.auth.set_access_token(
            self.__access_token, self.__access_token_secret)
        api = tweepy.API(self.auth)
        self.api = api

    def get_api(self):
        return self.api

    def get_auth(self):
        return self.auth
