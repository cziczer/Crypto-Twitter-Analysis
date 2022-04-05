from db_utils.db_manager import DBManager


class TweetInserter(DBManager):
    def __init__(self, manager=None):
        if manager is None:
            super().__init__()
        else:
            self.connection = manager.connection
            self.cur = self.connection.cursor()

    def fast_insert_user_mentions(self, tweets):
        insert_sql = "INSERT OR IGNORE INTO users_mentioned (tweet_id, user_id) VALUES (?, ?)"
        vals = []
        for tweet in tweets:
            if tweet.get('entities') and tweet['entities'].get('mentions'):
                for user in tweet['entities']['mentions']:
                    vals.append((tweet['id'], user['id']))
        self.cur.executemany(insert_sql, vals)
        self.connection.commit()

    def fast_insert_hashtags(self, tweets):
        hashtag_tweets = dict()
        for tweet in tweets:
            if tweet.get('entities') and tweet['entities'].get('hashtags'):
                for tag in tweet['entities']['hashtags']:
                    txt = tag['tag']
                    if txt not in hashtag_tweets.keys():
                        hashtag_tweets[txt] = []
                    hashtag_tweets[txt].append(tweet['id'])

        insert_h_sql = "INSERT OR IGNORE INTO hashtag (tag) VALUES (?)"
        vals = list(map(lambda x: (x,),
                        hashtag_tweets.keys()))
        self.cur.executemany(insert_h_sql, vals)
        self.connection.commit()

        h = list(hashtag_tweets.keys())
        tags = []
        MAX_VARIABLES_NUMBER = 900
        if len(h) > MAX_VARIABLES_NUMBER:
            for i in range(0, len(h), MAX_VARIABLES_NUMBER):
                questionmarks = '?' * len(h[i:i + MAX_VARIABLES_NUMBER])
                select_h_sql = "SELECT id, tag FROM hashtag WHERE tag IN ({})".format(','.join(questionmarks))
                self.cur.execute(select_h_sql, h[i:i + MAX_VARIABLES_NUMBER])
                tags = tags + self.cur.fetchall()

        else:
            questionmarks = '?' * len(h)
            select_h_sql = "SELECT id, tag FROM hashtag WHERE tag IN ({})".format(','.join(questionmarks))
            self.cur.execute(select_h_sql, h)
            tags = self.cur.fetchall()

        h_id_tw_id = []
        for tag in tags:
            for tweet_id in hashtag_tweets[tag['tag']]:
                h_id_tw_id.append((tag['id'], tweet_id))

        insert_h_tw_sql = "INSERT OR IGNORE INTO tweets_hashtags (hashtag_id, tweet_id)  VALUES (?, ?)"
        self.cur.executemany(insert_h_tw_sql, h_id_tw_id)
        self.connection.commit()

    def fast_insert_tweets(self, tweets):
        insert_sql = "INSERT INTO tweet (id, text, conversation_id, created_at," \
                     "retweet_count, like_count, reply_count, quote_count, " \
                     "language, author_id)" \
                     "values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET " \
                     "quote_count= MAX(excluded.quote_count, tweet.quote_count)," \
                     "reply_count= MAX(excluded.reply_count, tweet.reply_count)," \
                     "retweet_count= MAX(excluded.retweet_count, tweet.retweet_count)," \
                     "like_count= MAX(excluded.like_count, tweet.like_count)"

        vals = list(
            map(
                lambda tweet: (
                    tweet['id'], tweet['text'], tweet['conversation_id'], self.parse_to_datetime(tweet['created_at']),
                    tweet['retweet_count'], tweet['like_count'], tweet['reply_count'], tweet['quote_count'],
                    tweet['lang'], tweet['author_id']),
                tweets
            )
        )
        self.cur.executemany(insert_sql, vals)
        self.connection.commit()
        self.fast_insert_user_mentions(tweets)
        self.fast_insert_hashtags(tweets)

    def close_db(self):
        self.connection.close()
