from db_utils.db_manager import DBManager


class UserInserter(DBManager):
    def __init__(self, manager=None):
        if manager is None:
            super().__init__()
        else:
            self.connection = manager.connection
            self.cur = self.connection.cursor()

    def save_usermentions(self, tweet):
        um = tweet['users_mentioned']
        um_tw_us = list(map(lambda x: (tweet['id'], x['id']), um))

        insert_sql = "INSERT INTO user_mentions (tweet_id, user_id) VALUES (?, ?)"
        self.cur.executemany(insert_sql, um_tw_us)
        self.connection.commit()

    def update_user(self, new_user, old_user):
        names = []
        vals = []
        fields = ['followers_count', 'friends_count']
        for field in fields:
            if new_user[field] > old_user[field]:
                names.append(field)
                vals.append(new_user[field])

        if len(names) > 0:
            update_sql = "UPDATE user SET "
            for name in names:
                update_sql += name + ' = ?, '
            update_sql = update_sql[:-2]
            update_sql += "WHERE id = " + str(old_user['id'])
            self.cur.execute(update_sql, tuple(vals))
            self.connection.commit()

    def insert_user(self, user):
        # print(user)
        id = user['id']

        select_sql = "SELECT id, followers_count, friends_count FROM user WHERE id = ?"
        self.cur.execute(select_sql, (id,))

        user_db = self.cur.fetchone()
        if user_db is not None:
            self.update_user(user, user_db)
        else:
            insert_sql = "INSERT INTO user " \
                         "(id, screen_name, location, followers_count, friends_count, created_at) VALUES " \
                         "(?, ?, ?, ?, ?, ?)"
            val = (user['id'], user['screen_name'], user['location'], user['followers_count'], user['friends_count'],
                   user['created_at'])
            self.cur.execute(insert_sql, val)
            self.connection.commit()

    def fast_insert_users(self, users):
        insert_sql = "INSERT INTO user (id, name, username, location, " \
                     "followers_count, following_count, listed_count, tweet_count) " \
                     "values (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET " \
                     "followers_count= MAX(excluded.followers_count, user.followers_count)," \
                     "following_count = MAX(excluded.following_count, user.following_count)," \
                     "listed_count = MAX(excluded.listed_count, user.listed_count)," \
                     "tweet_count = MAX(excluded.tweet_count, user.tweet_count)"

        vals = list(map(
            lambda user: (
                user['id'], user['name'], user['username'], user['location'], user['followers_count'],
                user['following_count'], user['listed_count'], user['tweet_count']),
            users)
        )
        self.cur.executemany(insert_sql, vals)
        self.connection.commit()

    def close_db(self):
        self.connection.close()
