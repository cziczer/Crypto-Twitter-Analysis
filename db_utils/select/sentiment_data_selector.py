from db_utils.select.data_selector import DataSelector

class SentimentDataSelector(DataSelector):
    def __init__(self, manager=None):
        if manager is None:
            super().__init__()
        else:
            self.connection = manager.connection
            self.cur = self.connection.cursor()
        self.graph_users = 100_000
        # self.graph_users = 50
        self.graph_nodes = []
        self.is_executed = False

    def get_tweets_to_sentiment_analysis(self, noOfTweet=20_000, from_date=None, to_date=None, month_name=None):
        from_date, to_date = self.parse_from_to_date(from_date, to_date)

        select_sql = "SELECT t.id, t.text, t.created_at " \
                     "FROM Tweet t " \
                     "WHERE  t.language = 'en' " \
                     "LIMIT " + str(noOfTweet)

        self.cur.execute(select_sql)
        data = self.cur.fetchall()
        result = dict()

        for row in data:
            result[row['id']] = dict()
            result[row['id']]['text'] = row['text']
            result[row['id']]['created_at'] = row['created_at']

        return result
