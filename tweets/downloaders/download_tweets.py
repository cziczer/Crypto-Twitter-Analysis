from datetime import datetime, timedelta
from time import sleep
import tweepy
import json
bearer_token='AAAAAAAAAAAAAAAAAAAAAL%2BEbAEAAAAA8At2OR6ga10mmw01V6phaujlXKg%3D26ZFme57gp7WA0rLiUOgoMiIc7pj2sGebiadTwCY90fJhoTmlF'

client = tweepy.Client(bearer_token=bearer_token)
tracklist = ['musk', 'ethereum', 'cardano', 'russia', 'ukraine', 'bitcoin', 'biden', 'crypto', 'dogecoin']

tweets_info = []
users_info = []
retweets_info = []
counter = 0


def append_data(tweet, user, date):
    tweet_info = {
        'id': tweet.id,
        'text': tweet.text,
        'created_at': str(tweet.created_at),
        'retweet_count': tweet.public_metrics['retweet_count'],
        'reply_count': tweet.public_metrics['reply_count'],
        'like_count': tweet.public_metrics['like_count'],
        'quote_count': tweet.public_metrics['quote_count'],
        'entities': tweet.entities,
        'conversation_id': tweet.conversation_id,
        'lang': tweet.lang,
        'author_id': user.id,
    }
    retweet_info = []
    if tweet.referenced_tweets:
        retweet_info = [{
            'from_id': tweet.id,
            'to_id': retweet.id,
            'type': retweet.type,
        } for retweet in tweet.referenced_tweets]

    user_info = {
        'id': user.id,
        'name': user.name,
        'username': user.username,
        'location': user.location,
        'description': user.description,
        'followers_count': user.public_metrics['followers_count'],
        'following_count': user.public_metrics['following_count'],
        'tweet_count': user.public_metrics['tweet_count'],
        'listed_count': user.public_metrics['listed_count']
    }
    save_data_to_json(tweet_info, user_info, retweet_info, date)


def save_data_to_json(tweet, user, retweet, date):
    # with open('tweets.json', 'r') as tweets_file:
    #     current_tweets = json.load(tweets_file)
    #     for tweet in tweets_info:
    #         current_tweets.append(tweet)
    with open(f'../../data/tweets/{date}_tweets.json', 'a') as tweets_file:
        # with open('tweets.json', 'a') as tweets_file:
        with open(f'../../data/users/{date}_users.json', 'a') as users_file:
            with open(f'../../data/retweets/{date}_retweets.json', 'a') as retweets_file:
                tweets_file.write(json.dumps(tweet))
                tweets_file.write(',\n')
                users_file.write(json.dumps(user))
                users_file.write(',\n')
                if retweet:
                    retweets_file.write(json.dumps(retweet))
                    retweets_file.write(',\n')


start_date = datetime.today().date() - timedelta(days=9)
day_count = 5

for query_date in (start_date - timedelta(n) for n in range(day_count)):
    for hour in range(15, 24):
        for search in tracklist:
            last_tweet = None
            tweets = None
            try:
                tweets = client.search_all_tweets(
                    search,
                    max_results=100,
                    expansions='author_id',
                    tweet_fields=["created_at", "public_metrics", "entities",
                                  "conversation_id", "in_reply_to_user_id", "lang", "referenced_tweets"],
                    user_fields=["name", "username", "location", "verified", "description", "public_metrics"],
                    start_time=datetime.strptime(f'{query_date} {hour}:00', '%Y-%m-%d %H:%M'),
                    end_time=datetime.strptime(f'{query_date} {hour}:59', '%Y-%m-%d %H:%M'),
                )
                print(datetime.strptime(f'{query_date} {hour}:00', '%Y-%m-%d %H:%M'))
                for tweet, user in zip(tweets.data, tweets.includes['users']):
                    append_data(tweet, user, query_date)
                last_tweet = tweets
                while 'next_token' in tweets.meta:
                    try:
                        last_tweet = tweets
                        tweets = client.search_all_tweets(
                            search,
                            max_results=100,
                            expansions='author_id',
                            tweet_fields=["created_at", "public_metrics", "entities",
                                          "conversation_id", "in_reply_to_user_id", "lang", "referenced_tweets"],
                            user_fields=["name", "username", "location", "verified", "description", "public_metrics"],
                            start_time=datetime.strptime(f'{query_date} {hour}:00', '%Y-%m-%d %H:%M'),
                            end_time=datetime.strptime(f'{query_date} {hour}:59', '%Y-%m-%d %H:%M'),
                        )
                        for tweet, user in zip(tweets.data, tweets.includes['users']):
                            append_data(tweet, user, query_date)
                        counter += 1
                        if counter >= 1:
                            counter = 0
                            break
                        print(datetime.strptime(f'{query_date} {hour}:00', '%Y-%m-%d %H:%M'))
                    except Exception as e:
                        counter = 0
                        print(e)
                        tweet = last_tweet
                        sleep(300)
            except Exception as e:
                counter = 0
                print(e)
                tweet = last_tweet
                sleep(300)