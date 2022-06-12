import matplotlib.pyplot as plt
from sentiment.sentiment_analysis import *
from datetime import datetime
import numpy as np
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import webbrowser

from db_utils.select.sentiment_data_selector import SentimentDataSelector


def get_tweets(db, number_of_tweets=1_000, from_date=None, to_date=None, month_name=None):
    tweets = db.get_tweets_to_sentiment_analysis(number_of_tweets, from_date, to_date)
    return tweets


def create_pie_chart(tw_list):
    # Count_values for sentiment
    count_values_in_column(tw_list, "sentiment")

    # create data for Pie Chart
    pichart = count_values_in_column(tw_list, "sentiment")
    names = pichart.index
    size = pichart["Percentage"]

    # Create a circle for the center of the plot
    my_circle = plt.Circle((0, 0), 0.7, color='white')
    plt.pie(size, labels=names, colors=['green','blue', 'red'])
    p = plt.gcf()
    p.gca().add_artist(my_circle)
    plt.show()


# Function to Create Wordcloud
def create_wordcloud(text, result_filename):
    stopwords = set(STOPWORDS)
    wc = WordCloud(background_color="white",
                   max_words=3000,
                   stopwords=stopwords,
                   repeat=True)
    wc.generate(str(text))
    wc.to_file(result_filename)


def create_wordclouds(tweets):
    # Creating new data frames for all sentiments (positive, negative and neutral)
    tw_list_negative = tweets[tweets["sentiment"] == "negative"]
    tw_list_positive = tweets[tweets["sentiment"] == "positive"]
    tw_list_neutral = tweets[tweets["sentiment"] == "neutral"]

    create_wordcloud(tweets['text'].values, "results/wordcloud_all.png")
    create_wordcloud(tw_list_negative['text'].values, "results/wordcloud_negative.png")
    create_wordcloud(tw_list_positive['text'].values, "results/wordcloud_positive.png")
    create_wordcloud(tw_list_neutral['text'].values, "results/wordcloud_neutral.png")


if __name__ == "__main__":
    db = SentimentDataSelector()
    number_of_tweets = 100_000
    april = {
        "from": datetime.strptime("2022-04-01", "%Y-%m-%d").date(),
        "to": datetime.strptime("2022-04-30", "%Y-%m-%d").date(),
        "name": "april"
    }
    tweets = get_tweets(db=db,
                        number_of_tweets=number_of_tweets,
                        from_date=april["from"],
                        to_date=april["to"],
                        month_name=april["name"]
                        )

    tweets_list = []
    for tweet_id in tweets.keys():
        text = tweets[tweet_id]['text']
        tweets_list.append(text)

    cleaned_tweets = clean_tweets(tweets_list)
    print(len(cleaned_tweets))

    tweets_with_sentiments = calculate_sentiment(cleaned_tweets)
    create_pie_chart(tweets_with_sentiments)
    create_wordclouds(tweets_with_sentiments)

    len, words_count = tweets_means(tweets_with_sentiments)
    len.to_html("results/len_mean.html")
    words_count.to_html("results/count_mean.html")

    tweets = words_collocations(tweets_with_sentiments)
    tweets.to_html("results/tweets_with_stats.html")

    used_words = used_words(tweets)
    used_words.to_html("results/used_words.html")

    # n2_bigram
    n2_bigrams = get_top_n_gram(tweets['text'], (2, 2), 20)
    print(n2_bigrams)

    # n3_trigram
    n3_trigrams = get_top_n_gram(tweets['text'], (3, 3), 20)
    print(n3_trigrams)