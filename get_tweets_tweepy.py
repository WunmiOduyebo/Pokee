import tweepy
import json
import secret_data

#Start getting keys & secrets for running Twitter user, you will need your own user with details saved in a file named 'secret_data.txt' to run this
CONSUMER_KEY = secret_data.CONSUMER_KEY
CONSUMER_SECRET = secret_data.CONSUMER_SECRET
ACCESS_TOKEN = secret_data.ACCESS_TOKEN
ACCESS_SECRET = secret_data.ACCESS_SECRET
#End getting keys & secrets for running Twitter user

#Start cache setup
CACHE_FNAME = 'twitter_cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read() #this is a str
    CACHE_DICTION = json.loads(cache_contents) #this is a dict
    cache_file.close()
except:
    CACHE_DICTION = {}
#End cache setup

#Start OAuth code
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)
#End OAuth code

FILENAME = 'test_tweet_ids.txt' #this is just a sub-set of tweet ids taken from 'training_set_1_ids.txt'
# FILENAME = 'test_tweet_ids_10.txt'

#Start cache check
def get_tweet(found_id):
    if found_id in CACHE_DICTION:
        #if we get strange results in cache like missing child tweets then we may need to add the call to get_tweet() here
        return CACHE_DICTION[found_id]
    else:
        try:
            resp = api.get_status(found_id) #resp is a class 'tweepy.models.Status'
            json_str = json.dumps(resp._json) #json_str var is str type
            json_obj = json.loads(json_str) #json_obj var is dict type
        except Exception as e:
            json_obj = {}
            message = 'No worries. Empty entry has been made in cache.'
            print('Exception in get_tweet:{}\nProblematic Tweet:{}\n\n{}\n'.format(e, found_id,message))
        CACHE_DICTION[found_id] = json_obj #creating new entry in cache dict where key = 'found_id' & value = 'json_obj' which is a dict
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # close the open file

        #start recursive call to get_tweet() a.k.a. this funct if current tweet is in reply to another tweet
        if CACHE_DICTION[found_id]['in_reply_to_status_id_str'] is not None:
            in_reply_id = CACHE_DICTION[found_id]['in_reply_to_status_id_str']
            get_tweet(in_reply_id) 
        #end recursive call to get_tweet()

        return CACHE_DICTION[found_id]
#End cache check

def read_in_tweet_ids():
    with open(FILENAME, 'r') as infile:
        for line in infile:
            found_id = line.split('\t')[0]
            try:
                get_tweet(found_id)
            except:
                pass #having exception message print here was causing duplicate messages when get_tweet failed

if __name__ == "__main__":
    check = read_in_tweet_ids()