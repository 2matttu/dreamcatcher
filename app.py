from flask import Flask, render_template
from datetime import datetime
import json
import os
import requests
import praw
import pymongo
from pymongo import MongoClient
app = Flask(__name__)

db_uri = os.path.expandvars("$DB_URI")
cluster = MongoClient(db_uri)
db = cluster["dreamcatcher"]
collection = db["dreams"]

#praw
reddit = praw.Reddit(client_id = os.path.expandvars("$REDDIT_ID"), 
                    client_secret = os.path.expandvars("$REDDIT_SECRET"), 
                    password = os.path.expandvars("$REDDIT_PASSWORD"), 
                    user_agent  = "dreamcatcher", 
                    username = os.path.expandvars("$REDDIT_USERNAME"))
dreams_sub = reddit.subreddit('Dreams')

print(reddit.user.me())
print("uri: " + db_uri)
    
@app.route('/')
def hello_world():
    dream_list = list(collection.find()) #find everything
    for dream in dream_list:
        print(dream['title'])
    return render_template('dreams.html', dream_list = dream_list)

@app.route('/function')
def api_func():
    response = requests.get("https://www.reddit.com/r/tifu.json")
    # print(response.text)
    return str(response.status_code)

@app.route('/dbtest')
def db_post():
    post = {"name": "matt", "score": 5}
    collection.insert_one(post)
    return 'success'
    
@app.route('/testpraw')
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
            # collection.insert_one(db_payload)
            db_payload_list.append(db_payload)
            print('yeeted into the database!')
            upload_count += 1
        else:
            print('not yeet')
        seen_count += 1
    collection.insert_many(db_payload_list)
    print('added ' + str(upload_count) + ' new dreams (out of ' + str(seen_count) + ' dreams) to the dreamcatcher!')
    return 'success'
