from db_utils.db_manager import DBManager


class RetweetInserter(DBManager):
    def __init__(self, manager=None):
        if manager is None:
            super().__init__()
        else:
            self.connection = manager.connection
            self.cur = self.connection.cursor()

    def insert_retweets(self, retweets):
        insert_sql = "INSERT OR IGNORE INTO retweet" \
                     " (from_id, to_id, type) " \
                     "VALUES (?,?,?)"

        vals = []
        for tweet_retweets in retweets:
            for retweet in tweet_retweets:
                vals.append((retweet['from_id'], retweet['to_id'], retweet['type']))
        self.cur.executemany(insert_sql, vals)
        self.connection.commit()

    def close_db(self):
        self.connection.close()
