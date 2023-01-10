import tweepy
from tweepy_obj import *
import os
import logging
import time
from utils import *
import random
import sqlite3

# setting up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
last_replied_to_id = int(os.environ.get(
    "TWITTER_LAST_REPLIED_TO_ID", 0))

# initialise tweepy class
tw = TweepyObject()
api = tw.get_api()


def init_db():
    """
    Initialize the mentions database.
    Creates a new table called 'mentions'
    'mentions' table has a single column, 'tweet_id', which is an integer.
    """
    conn = sqlite3.connect('mentions.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS mentions (tweet_id INTEGER)''')

    conn.commit()
    conn.close()


def handle_mentions():
    """
    handles mentions
    """

    # connecting to mentions.db
    conn = sqlite3.connect('mentions.db')
    c = conn.cursor()

    # fetching all mentions from Twitter timeline
    mentions = api.mentions_timeline()

    for mention in mentions:
        tweet_id = mention.id
        screen_name = mention.user.screen_name

        # selecting all tweet id's from the database
        c.execute('SELECT * FROM mentions WHERE tweet_id=?', (tweet_id,))
        result = c.fetchone()

        if result is not None:
            # this tweet has been replied
            continue

        # getting response from openai api
        ai_text = get_response(mention.text)

        reply_text = f'@{screen_name} {ai_text}'

        try:
            # replying to the tweet
            api.update_status(status=reply_text,
                              in_reply_to_status_id=tweet_id)
            logger.info(f'Replying: {reply_text}')

            c.execute('INSERT INTO mentions VALUES (?)', (tweet_id,))
        except Exception as exp:
            logger.info(exp)

    conn.commit()
    conn.close()


def reply_tweet(keyword) -> None:
    """
    replying to tweets that match with the keyword
    """
    global last_replied_to_id

    try:
        # fetching all the tweets that match the keyword
        logger.info(f'Searching for tweets containing: "{keyword}"')
        tweets = api.search_tweets(q=keyword, count=5)
    except tweepy.errors.TweepyException as e:
        logger.info(f'search_tweets Error: {e}')
        return

    logger.info(f"Found {len(tweets)} tweets")

    for tweet in tweets:
        username = tweet.user.screen_name
        status_id = tweet.id

        if tweet.id > last_replied_to_id:

            tweet_text = tweet.text

            tweet_text = tweet_text.replace(keyword, "")

            # getting the response from openai api
            response_text = get_response(tweet_text=tweet_text)

            # posting the response on twitter
            post_response(api=api, tweet=tweet,
                          tweet_text=tweet_text, response_text=response_text)


def main():
    # list of keywords
    keywords = ['finance', 'bitcoin', 'money', 'business', 'invest']

    while True:

        init_db()

        handle_mentions()

        reply_tweet(random.choice(keywords))

        time.sleep(60)


if __name__ == '__main__':
    main()
