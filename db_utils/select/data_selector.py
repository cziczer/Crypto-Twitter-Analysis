from datetime import datetime

from db_utils.db_manager import DBManager

from math import sqrt


class DataSelector(DBManager):
    def __init__(self, manager=None):
        if manager is None:
            super().__init__()
        else:
            self.connection = manager.connection
            self.cur = self.connection.cursor()
        self.graph_users = 1000
        # self.graph_users = 50
        self.graph_nodes = []
        self.is_executed = False

    def get_number_of_tweets_per_day(self):
        select_sql = "SELECT DATE(created_at) as created_at , count(*) AS number FROM tweet " \
                     "WHERE created_at > '2022-03-30'" \
                     "GROUP BY DATE(created_at)"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        result = dict()
        for row in data:
            date = row['created_at']
            num = row['number']
            result[date] = num
        return result

    def get_number_of_retweets_per_day(self):
        select_sql = "SELECT DATE(created_at) as created_at , count(*) AS number FROM retweet r " \
                     "JOIN tweet t on t.id = r.from_id " \
                     "WHERE created_at > '2022-03-30'" \
                     "    AND r.type = 'retweeted'" \
                     "GROUP BY DATE(created_at)"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        result = dict()
        for row in data:
            date = row['created_at']
            num = row['number']
            result[date] = num
        return result


    def get_number_of_quotes_per_day(self):
        select_sql = "SELECT DATE(created_at) as created_at , count(*) AS number FROM retweet r " \
                     "JOIN tweet t on t.id = r.from_id " \
                     "WHERE created_at > '2022-03-30'" \
                     "    AND r.type = 'quoted'" \
                     "GROUP BY DATE(created_at)"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        result = dict()
        for row in data:
            date = row['created_at']
            num = row['number']
            result[date] = num
        return result

    def get_most_popular_hashtags_per_day(self):
        select_sql = "SELECT distinct(h.tag), date(t.created_at) as created_at, count(*) AS number from hashtag h " \
                     "JOIN tweets_hashtags t_h on h.id = t_h.hashtag_id " \
                     "JOIN tweet t on t_h.tweet_id = t.id " \
                     "WHERE t.created_at > '2022-03-30' " \
                     "AND h.tag in " \
                     "    (" \
                     "    SELECT h.tag FROM tweets_hashtags " \
                     "    JOIN hashtag h on h.id = tweets_hashtags.hashtag_id " \
                     "    GROUP BY h.tag " \
                     "    ORDER BY count(*) DESC " \
                     "    LIMIT 5" \
                     "    ) " \
                     "GROUP BY t_h.hashtag_id, date(t.created_at)"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        result = dict()
        for row in data:
            if row['tag'] not in result:
                result[row['tag']] = dict()
                result[row['tag']]['dates'] = []
                result[row['tag']]['numbers'] = []

            result[row['tag']]['dates'].append(datetime.strptime(row['created_at'], "%Y-%m-%d").date())
            result[row['tag']]['numbers'].append(row['number'])

        return result

    def get_most_popular_hashtags(self, from_date=None, to_date=None):
        from_date, to_date = self.parse_from_to_date(from_date, to_date)

        select_sql = "SELECT distinct(h.tag), count(*) AS number from hashtag AS h " \
                     "JOIN tweets_hashtags t_h on h.id = t_h.hashtag_id " \
                     "WHERE t_h.hashtag_id in " \
                     "    (" \
                     "    SELECT hashtag_id " \
                     "    FROM  tweets_hashtags t_h " \
                     "    JOIN tweet t on t.id = t_h.tweet_id " \
                     "    WHERE t.created_at >= '" + from_date + "' " \
                     "        AND t.created_at <= '" + to_date + "' " \
                     "    GROUP BY t_h.hashtag_id " \
                     "    ORDER BY count(*) DESC " \
                     "    LIMIT 10" \
                     "    ) " \
                     "GROUP BY t_h.hashtag_id " \
                     "ORDER BY number DESC"

        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        result = dict()
        for row in data:
            result[row['tag']] = row['number']
        return result

    def get_most_popular_users_followers(self):
        select_sql = "SELECT username, followers_count " \
                     "FROM user ORDER BY followers_count DESC LIMIT 10"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        result = dict()
        for row in data:
            result[row['username']] = row['followers_count']
        return result

    def get_most_popular_users_following(self):
        select_sql = "SELECT username, following_count " \
                     "FROM user ORDER BY following_count DESC LIMIT 10"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        result = dict()
        for row in data:
            result[row['username']] = row['following_count']
        return result

    def get_most_active_users(self, from_date=None, to_date=None):
        from_date, to_date = self.parse_from_to_date(from_date, to_date)

        select_sql = "SELECT u.username, count(*) AS number FROM tweet t " \
                     "JOIN user u on t.author_id = u.id " \
                     "WHERE t.created_at >= '" + from_date + "' " \
                     "    AND t.created_at <= '" + to_date + "' " \
                     "GROUP BY t.author_id " \
                     "ORDER BY count(*) DESC " \
                     "LIMIT 10"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        result = dict()
        for row in data:
            result[row['username']] = row['number']
        return result

    def get_most_retweeted_users(self, from_date=None, to_date=None):
        from_date, to_date = self.parse_from_to_date(from_date, to_date)

        select_sql = "SELECT u.username, count(*) AS number FROM retweet r " \
                     "JOIN tweet t on t.id = r.to_id " \
                     "JOIN user u on t.author_id = u.id " \
                     "WHERE t.created_at >= '" + from_date + "' " \
                     "    AND t.created_at <= '" + to_date + "' " \
                     "GROUP BY t.author_id " \
                     "ORDER BY count(*) DESC " \
                     "LIMIT 10"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        result = dict()
        for row in data:
            result[row['username']] = row['number']
        return result

    def get_most_active_users_per_day_tweets(self):
        select_sql = "SELECT u.username, date(t.created_at) as created_at, count(*) AS number FROM tweet t " \
                     "JOIN user u on t.author_id = u.id " \
                     "WHERE t.created_at > '2022-03-30' " \
                     "    and u.id in " \
                     "      (SELECT t.author_id from tweet t " \
                     "      GROUP BY t.author_id " \
                     "      ORDER BY count(*) DESC " \
                     "      LIMIT 10) " \
                     "GROUP BY t.author_id, date(t.created_at) " \
                     "ORDER BY t.created_at"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()

        result = dict()
        for row in data:
            if row['username'] not in result:
                result[row['username']] = dict()
                result[row['username']]['dates'] = []
                result[row['username']]['numbers'] = []

            result[row['username']]['dates'].append(datetime.strptime(row['created_at'], "%Y-%m-%d").date())
            result[row['username']]['numbers'].append(row['number'])
        return result

    def get_tw_lang_per_day(self):
        select_sql = "SELECT t.language, DATE(t.created_at) AS date, count(*) AS number FROM tweet t " \
                     "WHERE DATE(t.created_at) > '2022-03-30' " \
                     "GROUP BY DATE (t.created_at), t.language;"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()

        result = dict()
        for row in data:
            if row['language'] not in result:
                result[row['language']] = dict()
                result[row['language']]['dates'] = []
                result[row['language']]['numbers'] = []

            result[row['language']]['dates'].append(datetime.strptime(row['date'], "%Y-%m-%d").date())
            result[row['language']]['numbers'].append(row['number'])
        return result


    def get_influencers_per_day(self):
        select_sql = "SELECT u.username, DATE(t.created_at) AS date, count(*) AS number, " \
                     "sum(t.retweet_count) AS retweet_count, sum(t.like_count) AS like_count, " \
                     "sum(t.reply_count) AS reply_count, sum(t.quote_count) AS quote_count " \
                     "from tweet t " \
                     "JOIN user u ON u.id = t.author_id " \
                     "WHERE DATE(t.created_at) <> '2022-03-30' " \
                     "    AND u.username in " \
                     "(" \
                     " 'TheEconomist', 'Reuters', 'washingtonpost', 'Forbes', 'TechCrunch', " \
                     " 'guardian', 'TimesNow', 'htTweets', 'business', " \
                     " 'Telegraph', 'TelegraphWorld', 'jordanbpeterson' " \
                     ") " \
                     "GROUP BY DATE(t.created_at), t.author_id"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()

        result = dict()
        for row in data:
            if row['username'] not in result:
                result[row['username']] = dict()
                result[row['username']]['dates'] = []
                result[row['username']]['numbers'] = []
                result[row['username']]['retweet_count'] = []
                result[row['username']]['reply_count'] = []
                result[row['username']]['quote_count'] = []
                result[row['username']]['like_count'] = []

            result[row['username']]['dates'].append(datetime.strptime(row['date'], "%Y-%m-%d").date())
            result[row['username']]['numbers'].append(row['number'])
            result[row['username']]['retweet_count'].append(row['retweet_count'])
            result[row['username']]['reply_count'].append(row['reply_count'])
            result[row['username']]['quote_count'].append(row['quote_count'])
            result[row['username']]['like_count'].append(row['like_count'])
        return result


    def get_hashtags_cloud(self, from_date=None, to_date=None):
        from_date, to_date = self.parse_from_to_date(from_date, to_date)

        select_sql = "SELECT h.tag, count(ht.hashtag_id) AS popularity  from hashtag h " \
                     "JOIN tweets_hashtags ht on h.id = ht.hashtag_id " \
                     "JOIN tweet t on ht.tweet_id = t.id " \
                     "WHERE t.created_at >= '" + from_date + "' AND t.created_at <= '" + to_date + "'" \
                     "GROUP BY ht.hashtag_id " \
                     "ORDER BY popularity desc " \
                     "LIMIT 10000"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        result = dict()
        for row in data:
            result[row['tag']] = row['popularity']
        return result