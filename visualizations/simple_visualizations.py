from datetime import datetime

from db_utils.select.data_selector import DataSelector
import plotly.graph_objects as go
import random
from visualizations.utils import save_fig
import statistics as stat


def str_to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d").date()


# todo: update callendar
callendar = {
    # str_to_date('2022-04-05'): "The only day xD",

}


def find_y_of(date, x, y):
    i = 0
    while i < len(x):
        if x[i] == date:
            return y[i]
        i += 1

    return y[-1]


def add_annotations(fig, x, y):
    for date, event in callendar.items():
        pos = find_y_of(date, x, y)
        fig.add_trace(go.Scatter(
            x=[date],
            y=[pos],
            name=event,
            marker_symbol="x",
            marker_size=10
        ))

    return fig


def tweets_per_day(db):
    data = db.get_number_of_tweets_per_day()
    X = [datetime.strptime(d, "%Y-%m-%d").date() for d in data.keys()]
    Y = list(data.values())

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=X,
        y=Y,
        line_color='black',
        opacity=0.99,
        name="Tweets per day"

    ))
    fig.update_layout(
        title_text="Tweets per day",
        xaxis_title="date",
        yaxis_title="number of tweets",
        plot_bgcolor='white'

    )
    return add_annotations(fig, X, Y)


def retweets_per_day(db):
    data = db.get_number_of_retweets_per_day()
    X = [datetime.strptime(d, "%Y-%m-%d").date() for d in data.keys()]
    Y = list(data.values())

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=X,
        y=Y,
        line_color='black',
        opacity=0.99,
        name="Retweets per day"
    ))
    fig.update_layout(
        title_text="Retweets per day",
        xaxis_title="date",
        yaxis_title="number of retweets",
        plot_bgcolor='white'
    )
    return add_annotations(fig, X, Y)


def quotes_per_day(db):
    data = db.get_number_of_quotes_per_day()
    X = [datetime.strptime(d, "%Y-%m-%d").date() for d in data.keys()]
    Y = list(data.values())

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=X,
        y=Y,
        line_color='black',
        opacity=0.99,
        name="Quotes per day"
    ))
    fig.update_layout(
        title_text="Quotes per day",
        xaxis_title="date",
        yaxis_title="number of quotes",
        plot_bgcolor='white'
    )
    return add_annotations(fig, X, Y)


def most_popular_hashtags_per_day(db):
    data = db.get_most_popular_hashtags_per_day()
    fig = go.Figure()
    for tag in data.keys():
        fig.add_trace(
            go.Scatter(
                x=data[tag]['dates'],
                y=data[tag]['numbers'],
                name=tag,
                opacity=0.99
            )
        )
    fig.update_layout(
        title_text="Most popular hashtags per day",
        xaxis_title="date",
        yaxis_title="number of tweets with hashtag",
        plot_bgcolor='white',
    )
    return fig


def most_popular_hashtags(db, from_date=None, to_date=None, month_name=None):
    data = db.get_most_popular_hashtags(from_date, to_date)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(data.keys()),
            y=list(data.values()),
            name='hashtags',
            opacity=0.99
        )
    )
    fig.update_layout(
        title_text="Most popular hashtags" if month_name is None else "Most popular hashtags in " + month_name,
        xaxis_title="hashtag",
        yaxis_title="number of tweets with hashtag",
        plot_bgcolor='white'
    )
    return fig


def popular_users(db):
    data_followers = db.get_most_popular_users_followers()
    data_following = db.get_most_popular_users_following()
    X_followers = list(data_followers.keys())
    Y_followers = list(data_followers.values())
    X_following = list(data_following.keys())
    Y_following = list(data_following.values())

    fig1 = go.Figure()
    fig2 = go.Figure()
    fig1.add_trace(go.Bar(
        x=X_following,
        y=Y_following,
        name='followings'
    ))
    fig2.add_trace(go.Bar(
        x=X_followers,
        y=Y_followers,
        name='followers'
    ))
    fig1.update_layout(
        title_text='Most popular users due to followings',
        xaxis_title="username",
        yaxis_title="number of people",
        plot_bgcolor='white'
    )
    fig2.update_layout(
        title_text='Most popular users due to followers',
        xaxis_title="username",
        yaxis_title="number of people",
        plot_bgcolor='white'
    )
    return fig1, fig2


def most_active_users(db, from_date=None, to_date=None, month_name=None):
    data = db.get_most_active_users(from_date, to_date)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=[name for name in data.keys()],
            y=[number for number in list(data.values())]
        )
    )
    fig.update_layout(
        title_text='Most active users (tweets) since 2020-03-07' if month_name is None else "Most active users (tweets) in " + month_name,
        xaxis_title="username",
        yaxis_title="number of tweets",
        plot_bgcolor='white'
    )
    return fig


def most_active_users_retweets(db, from_date=None, to_date=None, month_name=None):
    data = db.get_most_active_users_retweets(from_date, to_date)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=[name for name in data.keys()],
            y=[number for number in list(data.values())]
        )
    )
    fig.update_layout(
        title_text='Most active users (retweets) since 2020-03-07' if month_name is None else "Most active users (retweets) in " + month_name,
        xaxis_title="username",
        yaxis_title="number of retweets",
        plot_bgcolor='white'
    )
    return fig


def most_active_users_per_day_tweets(db):
    data = db.get_most_active_users_per_day_tweets()
    fig = go.Figure()
    for s_name in data.keys():
        fig.add_trace(
            go.Scatter(
                x=data[s_name]['dates'],
                y=data[s_name]['numbers'],
                name=s_name,
                opacity=0.99
            )
        )
    fig.update_layout(
        title_text="Most active tweeting users per day",
        xaxis_title="date",
        yaxis_title="number of tweets",
        plot_bgcolor='white'
    )
    return fig


def most_retweeted_users(db, from_date=None, to_date=None, month_name=None):
    data = db.get_most_retweeted_users(from_date, to_date)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=[name for name in data.keys()],
            y=[number for number in list(data.values())]
        )
    )
    fig.update_layout(
        title_text='Most retweeted users' if month_name is None else "Most retweeted users in " + month_name,
        xaxis_title="username",
        yaxis_title="number of retweets",
        plot_bgcolor='white'
    )
    return fig


def most_active_users_per_day_tweets(db):
    data = db.get_most_active_users_per_day_tweets()
    fig = go.Figure()
    for s_name in data.keys():
        fig.add_trace(
            go.Scatter(
                x=data[s_name]['dates'],
                y=data[s_name]['numbers'],
                name=s_name,
                opacity=0.99
            )
        )
    fig.update_layout(
        title_text="Most active tweeting users per day",
        xaxis_title="date",
        yaxis_title="number of tweets",
        plot_bgcolor='white'
    )
    return fig


def tw_lang_per_day(db):
    data = db.get_tw_lang_per_day()
    fig = go.Figure()
    for lang in data.keys():
        fig.add_trace(
            go.Scatter(
                x=data[lang]['dates'],
                y=data[lang]['numbers'],
                name=lang,
                opacity=0.99
            )
        )
    fig.update_layout(
        title_text="Tweets in language per day",
        xaxis_title="date",
        yaxis_title="number of tweets",
        plot_bgcolor='white'
    )
    return fig


def influencers_per_day(db):
    data = db.get_influencers_per_day()
    t_fig = go.Figure()
    colors = ['#F39C12', '#E12FBD', '#9E3D64', '#9D22E3', '#F1C40F',
              '#05E5F8', '#E74C3C', '#5F287F', '#6593F5', '#4F820D',
              '#33F805', '#1AB394', '#154EE8', '#2D383C', '#B19CD9']
    i = 0
    for username in data.keys():
        t_fig.add_trace(
            go.Scatter(
                x=data[username]['dates'],
                y=data[username]['numbers'],
                name=username,
                line=dict(
                    color=colors[i]
                ),
                opacity=0.99
            )
        )
        i += 1
    t_fig.update_layout(
        title_text="Influencers' tweets per day",
        xaxis_title="date",
        yaxis_title="number of tweets",
        plot_bgcolor='white'
    )
    rtw_fig = go.Figure()
    i = 0
    for username in data.keys():
        rtw_fig.add_trace(
            go.Scatter(
                x=data[username]['dates'],
                y=data[username]['retweet_count'],
                name=username,
                line=dict(
                    color=colors[i]
                ),
                opacity=0.99
            )
        )
        i += 1
    rtw_fig.update_layout(
        title_text="Retweets of Influencers' tweets per day",
        xaxis_title="date",
        yaxis_title="number of retweets",
        plot_bgcolor='white'
    )
    rep_fig = go.Figure()
    i = 0
    for username in data.keys():
        rep_fig.add_trace(
            go.Scatter(
                x=data[username]['dates'],
                y=data[username]['reply_count'],
                name=username,
                line=dict(
                    color=colors[i]
                ),
                opacity=0.99
            )
        )
        i += 1
    rep_fig.update_layout(
        title_text="Replies to Influencers' tweets per day",
        xaxis_title="date",
        yaxis_title="number of replies",
        plot_bgcolor='white'
    )
    q_fig = go.Figure()
    i = 0
    for username in data.keys():
        q_fig.add_trace(
            go.Scatter(
                x=data[username]['dates'],
                y=data[username]['quote_count'],
                name=username,
                opacity=0.99
            )
        )
        i += 1
    q_fig.update_layout(
        title_text="Quotes of Influencers' tweets per day",
        xaxis_title="date",
        yaxis_title="number of quotes",
        plot_bgcolor='white'
    )

    return t_fig, rtw_fig, rep_fig, q_fig


if __name__ == "__main__":
    db = DataSelector()

    april = (
        datetime.strptime("2022-04-01", "%Y-%m-%d").date(),
        datetime.strptime("2022-04-30", "%Y-%m-%d").date(),
        "april"
    )
    # Tweets/Retweets/Quotes per day
    # tweets_per_day_fig = tweets_per_day(db)
    # tweets_per_day_fig.show()
    #
    # retweets_per_day_fig = retweets_per_day(db)
    # retweets_per_day_fig.show()
    #
    # quotes_per_day_fig = quotes_per_day(db)
    # quotes_per_day_fig.show()


    # Popular
    # popular_users_followings, popular_users_followers = popular_users(db)
    # popular_users_followers.show()
    # popular_users_followings.show()
    #
    # active_users_april_fig = most_active_users(db, *april)
    # active_users_april_fig.show()
    #
    # most_retweeted_users_april_retweets_fig = most_retweeted_users(db, *april)
    # most_retweeted_users_april_retweets_fig.show()


    # Influencers
    # inf_tw_per_day_fig, inf_rtw_per_day_fig, inf_rep_per_day_fig, inf_q_per_day_fig = influencers_per_day(db)
    # inf_tw_per_day_fig.show()
    # inf_rtw_per_day_fig.show()
    # inf_rep_per_day_fig.show()
    # inf_q_per_day_fig.show()


    # Hashtags
    # tags_per_day_fig = most_popular_hashtags_per_day(db)
    # tags_per_day_fig.show()
    #
    # most_popular_hashtags_april_fig = most_popular_hashtags(db, *april)
    # most_popular_hashtags_april_fig.show()

    # Others
    tw_lang_per_day_fig = tw_lang_per_day(db)
    tw_lang_per_day_fig.show()


