from datetime import datetime

# import country_converter as coco
# import geolocation.us_states as states_mapper

from db_utils.select.data_selector import DataSelector

from math import sqrt


class NetworkDataSelector(DataSelector):
    def __init__(self, manager=None):
        if manager is None:
            super().__init__()
        else:
            self.connection = manager.connection
            self.cur = self.connection.cursor()
        self.graph_users = 50_000
        # self.graph_users = 50
        self.graph_nodes = []
        self.is_executed = False

    def get_graph_nodes(self):
        if len(self.graph_nodes) == 0:
            select_sql = "SELECT t.author_id AS id from tweet t " \
                         "JOIN Retweet r on (r.to_id = t.id or r.from_id = t.id)" \
                         "GROUP BY t.author_id " \
                         "ORDER BY count(*) DESC " \
                         "LIMIT " + str(self.graph_users)
            self.cur.execute(select_sql)
            data = self.cur.fetchall()
            print(data)
            data = [u['id'] for u in data]
            self.graph_nodes = str(tuple(data))
            return self.graph_nodes
        else:
            return self.graph_nodes

    def get_user_nodes(self):
        select_sql = "SELECT u.id, u.username, u.followers_count, u.following_count, u.tweet_count, u.listed_count " \
                     "FROM user u " \
                     "WHERE u.id IN" + self.get_graph_nodes()
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        return data

    def get_nodes_weights(self):
        select_sql = "SELECT " \
                     "t.author_id AS author_id, " \
                     "sum(t.quote_count) AS quotes, " \
                     "sum(t.reply_count) AS replies, " \
                     "sum(t.retweet_count) AS retweets, " \
                     "sum(t.like_count) AS likes " \
                     "FROM tweet t " \
                     "WHERE t.author_id IN " + self.get_graph_nodes() + " GROUP BY t.author_id;"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        return data

    def get_followers_weights(self):
        select_sql = "SELECT u.id AS user_id, u.followers_count AS number FROM user u " \
                     "WHERE u.id IN " + self.get_graph_nodes()
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        return data

    def get_usermentions_weights(self):
        select_sql = "SELECT um.user_id AS user_id, count(*) AS number FROM users_mentioned um " \
                     "WHERE um.user_id IN " + self.get_graph_nodes() + " GROUP BY um.user_id;"
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        return data

    def get_retweet_edges(self, from_date=None, to_date=None):
        from_date, to_date = self.parse_from_to_date(from_date, to_date)
        print(from_date)
        print(to_date)

        select_sql = "SELECT " \
                     "  from_t.author_id AS user_A, " \
                     "  to_t.author_id AS user_B " \
                     "FROM retweet r " \
                     "JOIN tweet from_t on r.from_id = from_t.id " \
                     "JOIN tweet to_t on r.to_id = to_t.id " \
                     "WHERE r.type = 'retweeted' " \
                     "  AND from_t.author_id <> to_t.author_id " \
                     "  AND from_t.created_at >= '" + from_date + "' AND from_t.created_at <= '" + to_date + "'" + \
                     "  AND from_t.author_id IN " + self.get_graph_nodes() + \
                     "  AND to_t.author_id IN " + self.get_graph_nodes()
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        print(data)
        return data

    def get_quote_edges(self, from_date=None, to_date=None):
        from_date, to_date = self.parse_from_to_date(from_date, to_date)

        select_sql = "SELECT DISTINCT  from_t.author_id AS user_A, to_t.author_id AS user_B FROM retweet r " \
                     "JOIN tweet from_t on r.from_id = from_t.id " \
                     "JOIN tweet to_t on r.to_id = to_t.id " \
                     "WHERE r.type = 'quoted' " \
                     "  AND from_t.author_id <> to_t.author_id " \
                     "  AND from_t.created_at >= '" + from_date + "' AND from_t.created_at <= '" + to_date + "'" + \
                     "  AND from_t.author_id IN " + self.get_graph_nodes() + \
                     "  AND to_t.author_id IN " + self.get_graph_nodes()
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        return data

    def get_replies_edges(self, from_date=None, to_date=None):
        from_date, to_date = self.parse_from_to_date(from_date, to_date)

        select_sql = "SELECT DISTINCT  from_t.author_id AS user_A, to_t.author_id AS user_B FROM retweet r " \
                     "JOIN tweet from_t on r.from_id = from_t.id " \
                     "JOIN tweet to_t on r.to_id = to_t.id " \
                     "WHERE r.type = 'replied_to' " \
                     "  AND from_t.author_id <> to_t.author_id " \
                     "  AND from_t.created_at >= '" + from_date + "' AND from_t.created_at <= '" + to_date + "'" + \
                     "  AND from_t.author_id IN " + self.get_graph_nodes() + \
                     "  AND to_t.author_id IN " + self.get_graph_nodes()
        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        return data
