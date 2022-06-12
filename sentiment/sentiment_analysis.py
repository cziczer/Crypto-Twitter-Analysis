# Import Libraries

from textblob import TextBlob
import sys
import tweepy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import nltk
import pycountry
import re
import string

from wordcloud import WordCloud, STOPWORDS
from PIL import Image
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from langdetect import detect
from nltk.stem import SnowballStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer


# Sentiment Analysis
def percentage(part, whole):
    return 100 * float(part) / float(whole)


def count_values_in_column(data, feature):
    total = data.loc[:, feature].value_counts(dropna=False)
    percentage = round(data.loc[:, feature].value_counts(dropna=False, normalize=True) * 100, 2)
    return pd.concat([total, percentage], axis=1, keys=['Total', 'Percentage'])


# Removing Punctuation
def remove_punct(text):
    text = "".join([char for char in text if char not in string.punctuation])
    text = re.sub('[0-9]+', '', text)
    return text


# Appliyng tokenization
def tokenization(text):
    text = re.split('\W+', text)
    return text


# Removing stopwords
def remove_stopwords(text):
    text = [word for word in text if word not in STOPWORDS]
    return text


# Appliyng Stemmer
def stemming(text):
    ps = nltk.PorterStemmer()
    text = [ps.stem(word) for word in text]
    return text


# Cleaning Text
def clean_text(text):
    ps = nltk.PorterStemmer()
    text_lc = "".join([word.lower() for word in text if word not in string.punctuation])  # remove puntuation
    text_rc = re.sub('[0-9]+', '', text_lc)
    tokens = re.split('\W+', text_rc)  # tokenization
    text = [ps.stem(word) for word in tokens if word not in STOPWORDS]  # remove stopwords and stemming
    return text


def clean_tweets(tweets):
    tweet_list = pd.DataFrame(tweets)
    tweet_list.drop_duplicates(inplace=True)

    # Cleaning Text (RT, Punctuation etc)
    # Creating new dataframe and new features
    tw_list = pd.DataFrame(tweet_list)
    tw_list["text"] = tw_list[0]

    # Removing RT, Punctuation etc
    remove_rt = lambda x: re.sub("RT @\w+: ", "", x)
    rt = lambda x: re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", x)

    tw_list["text"] = tw_list.text.map(remove_rt).map(rt)
    tw_list["text"] = tw_list.text.str.lower()

    return tw_list


def calculate_sentiment(tw_list):
    # Calculating Negative, Positive, Neutral and Compound values
    tw_list[['polarity', 'subjectivity']] = \
        tw_list['text'].apply(lambda Text: pd.Series(TextBlob(Text).sentiment))

    for index, row in tw_list['text'].iteritems():
        score = SentimentIntensityAnalyzer().polarity_scores(row)
        neg = score['neg']
        neu = score['neu']
        pos = score['pos']
        comp = score['compound']

        if neg > pos:
            tw_list.loc[index, 'sentiment'] = "negative"
        elif pos > neg:
            tw_list.loc[index, 'sentiment'] = "positive"
        else:
            tw_list.loc[index, 'sentiment'] = "neutral"

        tw_list.loc[index, 'neg'] = neg
        tw_list.loc[index, 'neu'] = neu
        tw_list.loc[index, 'pos'] = pos
        tw_list.loc[index, 'compound'] = comp

    return tw_list


def tweets_means(tweets):
    # Calculating tweet's lenght and word count
    tweets['text_len'] = tweets['text'].astype(str).apply(len)
    tweets['text_word_count'] = tweets['text'].apply(lambda x: len(str(x).split()))

    tweets_len = round(pd.DataFrame(tweets.groupby("sentiment").text_len.mean()), 2)
    tweets_words_count = round(pd.DataFrame(tweets.groupby("sentiment").text_word_count.mean()), 2)

    return tweets_len, tweets_words_count


def words_collocations(tweets):
    tweets['punct'] = tweets['text'].apply(lambda x: remove_punct(x))
    tweets['tokenized'] = tweets['punct'].apply(lambda x: tokenization(x.lower()))
    tweets['nonstop'] = tweets['tokenized'].apply(lambda x: remove_stopwords(x))
    tweets['stemmed'] = tweets['nonstop'].apply(lambda x: stemming(x))

    return tweets


def used_words(tweets):
    countVectorizer = CountVectorizer(analyzer=clean_text)
    countVector = countVectorizer.fit_transform(tweets['text'])
    count_vect_df = pd.DataFrame(countVector.toarray(), columns=countVectorizer.get_feature_names())

    # Most Used Words
    count = pd.DataFrame(count_vect_df.sum())
    countdf = count.sort_values(0, ascending=False)
    return countdf


# Function to ngram
def get_top_n_gram(corpus, ngram_range, n=None):
    vec = CountVectorizer(ngram_range=ngram_range, stop_words='english').fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    return words_freq[:n]