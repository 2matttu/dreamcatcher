from flask import Flask, render_template
from datetime import datetime, timedelta, date
import json
import os
import requests
import random
import praw
import tweepy
import pymongo
from pymongo import MongoClient
app = Flask(__name__)

db_uri = os.path.expandvars("$DB_URI")
cluster = MongoClient(db_uri)
db = cluster["dreamcatcher"]
collection = db["dreams"]
twitter_dreams = db["twitter"]

#praw
reddit = praw.Reddit(client_id = os.path.expandvars("$REDDIT_ID"), 
                    client_secret = os.path.expandvars("$REDDIT_SECRET"), 
                    password = os.path.expandvars("$REDDIT_PASSWORD"), 
                    user_agent  = "dreamcatcher", 
                    username = os.path.expandvars("$REDDIT_USERNAME"))
dreams_sub = reddit.subreddit('Dreams')

#tweepy
tw_auth = tweepy.AppAuthHandler(os.path.expandvars("$TWITTER_KEY"), os.path.expandvars("$TWITTER_SECRET"))
tw_api = tweepy.API(tw_auth)

print(reddit.user.me())
print("uri: " + db_uri)
    
@app.route('/')
def hello_world():
    latest_dream = twitter_dreams.find_one(sort=[("date_time", -1)])
    print(latest_dream['date'])

    dream_list = list(twitter_dreams.find( { "date": latest_dream['date'], "truncated": False } )) #find everything
    random.shuffle(dream_list)

    return render_template('typed.html', dream_list = dream_list, date = latest_dream['date'])

@app.route('/all')
def typed():
    latest_dream = twitter_dreams.find_one(sort=[("date_time", -1)])
    print(latest_dream['date'])

    dream_list = list(twitter_dreams.find( { "date": latest_dream['date'], "truncated": False } )) #find everything
    random.shuffle(dream_list)

    return render_template('dreams.html', dream_list = dream_list, date = latest_dream['date'])
    
@app.route('/reddit')
def test_praw():
    date_str = datetime.today().strftime('%Y-%m-%d')
    print("today is " + date_str)
    daily_dreams = dreams_sub.top(limit=1000, time_filter='day')
    upload_count = 0
    seen_count = 0
    db_payload_list = []
    for post in daily_dreams:
        post_title = post.title
        post_text = post.selftext
        post_length = len(post_text)
        post_flair = str(post.link_flair_text)
        post_upvotes = post.score

        # debug stuff
        print(post_title)
        print("flair: " + post_flair + ", Upvotes: " + str(post_upvotes))
        print(len(post_text))
        
        if (post_flair == "None" or post_flair == "Short Dream" or post_flair == "Long Dream") and post_length > 0 and post_upvotes > 0:
            db_payload = {"date": date_str, "origin": "Reddit", "title": post_title, "text": post_text, "length": post_length, "score": post_upvotes}
            db_payload_list.append(db_payload)
            print('yeeted into the database!')
            upload_count += 1
        else:
            print('not yeet')
        seen_count += 1
    return 'success'

@app.route(os.path.expandvars("/$UPDATE_ROUTENAME"))
def test_tweepy():
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    latest_dream = twitter_dreams.find_one(sort=[("date_time", -1)])
    print(latest_dream['date'])
    if latest_dream['date'] == str(yesterday) or latest_dream['date'] == str(today):
        return "nothing to update"

    count = 0
    count_truncated = 0
    char_count = 0
    tweets_to_upload = []
    #searches for dream-related tweets the day before
    for tweet in tweepy.Cursor(tw_api.search, q='"i dreamed about" OR "i had a dream about" OR "i had a nightmare about" OR "i dreamed that" -filter:retweets -filter:media -filter:links -filter:replies since:' + yesterday.strftime('%Y-%m-%d') + ' until:' + today.strftime('%Y-%m-%d')).items(1000):
        try: 
            tweet_to_add = {"date": str(yesterday), "date_time": str(tweet.created_at), "tweet_id": tweet.id, "text": str(tweet.text), "truncated": tweet.truncated}
            if tweet.truncated:
                count_truncated += 1
            tweets_to_upload.append(tweet_to_add)
            count += 1
            char_count += len(str(tweet.text))
        except:
            print('\n[something went wrong]')
    #status report
    print(count, " dreams collected")
    #metadata
    db['metadata'].insert_one({"date": str(yesterday), "total": count, "trunc": count_truncated})
    twitter_dreams.insert_many(tweets_to_upload)
    return 'done'
