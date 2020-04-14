import sys
import time
import tweepy
import configparser


def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)
        except IOError:
            time.sleep(60*5)
            continue
        except StopIteration:
            break


config = configparser.ConfigParser()
config.read('.twitter')
twitter_account = config['source']['account_screen_name']

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(config['consumer']['key'], config['consumer']['secret'])
auth.set_access_token(config['access']['token'], config['access']['token_secret'])

# Creation of the actual interface, using authentication
api = tweepy.API(auth)
saveFile = open('./tweets/%s.txt'%twitter_account, 'w')

for status in limit_handled(tweepy.Cursor(api.user_timeline, screen_name=twitter_account, tweet_mode="extended").items()):
    print(status.full_text)
    saveFile.write("%s\n"%status.full_text)

saveFile.close()

print("")
print("====================")
print("Extraction finished!")
print("====================")
