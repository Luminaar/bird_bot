#! /usr/bin/python2

import sys
import twitter
import random
import credentials
import os
from datetime import date
import urllib

# changing current working directory so we can
# use local paths when calling script from different place
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

def load_list(file_name):
    """Read lines from a file and return as a list."""
    with open(file_name, 'r') as f:
        return f.read().splitlines()

def get_proverb():
    """Get a randomly generated proverb."""
    birds = load_list('birds.txt')
    proverbs = load_list('proverbs.txt')
    day = date.today().day

    while True:
        bird1 = random.choice(birds).upper()
        bird2 = random.choice(birds).upper()
        output = proverbs[day].format(bird1, bird2)
        if len(output) > 140:
            continue
        else:
            break

    return output

def get_reply(screen_name):
    """Generate a reply to a user. Reply is made of a random
    birds name and a link to its wikipedia page."""

    birds = load_list('birds.txt')
    bird = random.choice(birds)
    url = 'http://en.wikipedia.org/wiki/{}'.format(urllib.quote(bird))

    output =  '@{user} Check out {bird}: {link}'.format(bird=bird.upper(),
                                                      link=url,
                                                      user=screen_name)
    return output

def get_last_status_id(filename='last_status'):
    """Retrun ID of the last status that we replied to."""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except IOError as e:
        return None

def set_last_status_id(status_id, filename='last_status'):
    """Save ID of the last status that we replied to a file."""
    with open(filename, 'w') as f:
        f.write(str(status_id))


if __name__=='__main__':

    api = twitter.Api(consumer_key=credentials.key,
                      consumer_secret=credentials.secret,
                      access_token_key=credentials.token_key,
                      access_token_secret=credentials.token_secret)

    if '--reply' in sys.argv:  # reply to tweets tweeted at me
        since = get_last_status_id()
        mentions = api.GetMentions(since_id=since)
        if len(mentions) > 0:
            set_last_status_id(mentions[0].id)

            for mention in mentions:
               api.PostUpdate(get_reply(mention.user.screen_name))
               print mention.text

    elif '--stream' in sys.argv:  # start a stream that is listening to replies
        stream = api.GetUserStream(withuser='birdproverb')

        for obj in stream:

            try:
                text = obj['text']
                if not 'birdproverb' in text:
                    continue  # it is not a reply to us

                _id = obj['id']
                set_last_status_id(_id)

                user_id = obj['user']['id']

                api.PostUpdate(get_reply(user_id))
                print 'Replied to user {}'.format(obj['user']['screen_name'])

            except KeyError as e:
                print obj


    else:
        api.PostUpdate(get_proverb())
