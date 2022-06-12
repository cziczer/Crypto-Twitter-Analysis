from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime

from db_utils.select.data_selector import DataSelector


def hashtag_cloud(db, from_date=None, to_date=None, month_name=None):
    most_popular_hastags = db.get_hashtags_cloud(from_date, to_date)

    wordcloud = WordCloud(background_color="white", width=1600, height=800).generate_from_frequencies(most_popular_hastags)

    plt.figure(figsize=(20, 10))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("Hashtags in " + month_name)
    plt.savefig('results/wordcloud_hashtags_'+month_name+'.png', bbox_inches='tight')
    plt.show()


if __name__ == '__main__':
    db = DataSelector()

    april = datetime.strptime("2022-04-01", "%Y-%m-%d").date(), datetime.strptime("2022-04-30", "%Y-%m-%d").date(), "april"

    hashtag_cloud(db, *april)