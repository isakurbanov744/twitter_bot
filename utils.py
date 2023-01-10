import tweepy
import os
import logging
import openai
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

openai.api_key = os.environ['OPENAI_API_KEY']

def post_response(tweet, api, tweet_text, response_text):
    global last_replied_to_id

    username = tweet.user.screen_name
    status_id = tweet.id

    try:
        api.update_status(
            f"@{username} {response_text}",
            in_reply_to_status_id=status_id
        )
    except tweepy.errors.TweepyException as e:
        logger.info(f"Error: {e}")
        response_text = "I'm sorry, I'm not sure how to answer that. Please ask me something else."

    logger.info(
        f'\nReplied to: {username}\nTweet text: {tweet_text}\nResponse text: {response_text}\n')

    last_replied_to_id = tweet.id
    os.environ['TWITTER_LAST_REPLIED_TO_ID'] = str(last_replied_to_id)


def get_response(tweet_text):
    tweet_text = f'please answer following question in english, third person and keep the response less than 270 characters. {tweet_text}'
    # logger.info(f"OpenAI prompt: {tweet_text}")
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=tweet_text,
        temperature=0.7,
        max_tokens=128,
    )
    response_text = response['choices'][0]['text']

    return response_text
