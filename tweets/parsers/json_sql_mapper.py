import json
import os
from file_parser import parse_file
from db_utils.insert.user_inserter import UserInserter
from db_utils.insert.tweet_inserter import TweetInserter
from db_utils.insert.retweet_inserter import RetweetInserter

tw_data_dir = '../../data/tweets/'
rtw_data_dir = '../../data/retweets/'
usr_data_dir = '../../data/users/'
data_dirs = [usr_data_dir, tw_data_dir]


def parse_files_in_dir(data_dir):
    db_user_inserter = UserInserter()
    db_tweet_inserter = TweetInserter()
    db_retweets_inserter = RetweetInserter()
    filenames = []

    for filename in os.listdir(data_dir):
        if '.DS' not in filename and '_in' not in filename:
            filenames.append(filename)

    # for filename in filenames:
    #     parse_file(data_dir + filename)

    for filename in filenames:
        print(data_dir + filename)
        with open(data_dir + filename) as f:
            data = json.load(f)
            if 'retweets' in data_dir:
                db_retweets_inserter.insert_retweets(data)
            elif 'users' in data_dir:
                db_user_inserter.fast_insert_users(data)
            elif 'tweets' in data_dir:
                db_tweet_inserter.fast_insert_tweets(data)


# parse_files_in_dir(usr_data_dir)
# parse_files_in_dir(tw_data_dir)
# parse_files_in_dir(rtw_data_dir)
