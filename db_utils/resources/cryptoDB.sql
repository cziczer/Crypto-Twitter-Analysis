-- tables
-- Table: Hashtag
CREATE TABLE Hashtag (
    id integer NOT NULL CONSTRAINT Hashtag_pk PRIMARY KEY,
    tag varchar(255) NOT NULL
);

-- Table: Retweet
CREATE TABLE Retweet (
    id integer NOT NULL CONSTRAINT Retweet_pk PRIMARY KEY,
    from_id integer NOT NULL,
    to_id integer NOT NULL,
    type varchar(255) NOT NULL,
    CONSTRAINT from_id UNIQUE (from_id),
    CONSTRAINT to_id UNIQUE (to_id),
    CONSTRAINT Retweet_Tweet FOREIGN KEY (from_id)
    REFERENCES Tweet (id)
);

-- Table: Tweet
CREATE TABLE Tweet (
    id integer NOT NULL CONSTRAINT Tweet_pk PRIMARY KEY,
    text text NOT NULL,
    conversation_id integer,
    created_at datetime NOT NULL,
    language varchar(255),
    retweet_count integer NOT NULL,
    like_count integer NOT NULL,
    reply_count integer NOT NULL,
    quote_count integer NOT NULL,
    author_id integer NOT NULL,
    CONSTRAINT author_ref FOREIGN KEY (author_id)
    REFERENCES User (id),
    CONSTRAINT Tweet_Retweet FOREIGN KEY (id)
    REFERENCES Retweet (to_id)
);

-- Table: Tweets_Hashtags
CREATE TABLE Tweets_Hashtags (
    id integer NOT NULL CONSTRAINT Tweets_Hashtags_pk PRIMARY KEY,
    tweet_id integer NOT NULL,
    hashtag_id integer NOT NULL,
    CONSTRAINT Tweets_Hashtags_Tweet FOREIGN KEY (tweet_id)
    REFERENCES Tweet (id),
    CONSTRAINT Tweets_Hashtags_Hashtag FOREIGN KEY (hashtag_id)
    REFERENCES Hashtag (id)
);

-- Table: User
CREATE TABLE User (
    id integer NOT NULL CONSTRAINT User_pk PRIMARY KEY,
    name varchar(255) NOT NULL,
    username varchar(255) NOT NULL,
    location varchar(255),
    followers_count integer NOT NULL,
    following_count integer NOT NULL,
    tweet_count integer NOT NULL,
    listed_count integer NOT NULL
);

-- Table: Users_Mentioned
CREATE TABLE Users_Mentioned (
    id integer NOT NULL CONSTRAINT Users_Mentioned_pk PRIMARY KEY,
    tweet_id integer NOT NULL,
    user_id integer NOT NULL,
    CONSTRAINT user_id UNIQUE (user_id),
    CONSTRAINT Table_8_Tweet FOREIGN KEY (tweet_id)
    REFERENCES Tweet (id),
    CONSTRAINT User_Table_8 FOREIGN KEY (user_id)
    REFERENCES User (id)
);

