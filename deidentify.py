#!/usr/bin/env python

"""
"""

import argparse
import codecs
import datetime as dt
import json
import os
import struct
import sys
import urlparse
import uuid
import random
import hashlib
import binascii

random.seed(424242)
SALT = "SaltIsNaCl" # Pick your own salt 

from username_statistics import calc_username_statistics

def main():
    # Make stdout output UTF-8, preventing "'ascii' codec can't encode" errors
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    parser = argparse.ArgumentParser(description="Anonymize all one-JSON-object-per-line .tweets files in a series of directories")
    parser.add_argument('input_dirs', nargs='+')
    args = parser.parse_args()

    start =dt.datetime.now()
    last_checkpoint = dt.datetime.now()
    
    for input_dir in args.input_dirs:
        input_path = input_dir.split('/') # Unix specific
        if not input_path[-1]: # Deal with trailing /
            input_path.pop(-1)
        input_path[-1] = 'anonymized_'+input_path[-1]
        output_path = '/'.join(input_path + [''])
        os.system('mkdir -p '+output_path)
        print input_dir
        print output_path

        input_filenames = filter( lambda x: x.endswith('.tweets'), os.listdir(input_dir))
        for input_filename in input_filenames:
            nowish_now = dt.datetime.now()
            print nowish_now - last_checkpoint
            last_checkpoint = nowish_now
            screen_name,extension = input_filename.split('.')
            username_statistics = calc_username_statistics(screen_name)
            anonymized_screen_name = anonymize_username(screen_name)
            print input_dir + input_filename
            print output_path + anonymized_screen_name + "." + extension
            input_file = codecs.open(input_dir + input_filename, 'r', 'utf-8')
            output_file = codecs.open(output_path + anonymized_screen_name + "." + extension, 'w', 'utf-8')

            for line in input_file:
                tweet = json.loads(line)
                anonymized_tweet = anonymize_tweet(tweet)
                anonymized_tweet['screen_name_statistics'] = username_statistics
                # Use the same field separators for JSON stings as the Twitter API
                tweet_string = json.dumps(anonymized_tweet, separators=(', ',': ')) + "\n"
                output_file.write(tweet_string)
            input_file.close()
            output_file.close()

    OUT = codecs.open('deanonymizer_usernames', 'w', 'utf-8')
    for deanon,anon in anonymized_usernames.items():
        OUT.write(u'%s,%s\n' % (deanon,anon))
    OUT.close()

    OUT = codecs.open('deanonymizer_tweet_ids','w', 'utf-8')
    for deanon,anon in anonymize_tweet_id.mapping.items():
        OUT.write(u'%s,%s\n' % (deanon,anon))
    OUT.close()

    OUT = codecs.open('deanonymizer_user_ids','w', 'utf-8')
    for deanon,anon in anonymize_user_id.mapping.items():
        OUT.write('%s,%s\n' % (deanon,anon))
    OUT.close()

    OUT = codecs.open('deanonymizer_urls', 'w', 'utf-8')
    for deanon,anon in anonymized_urls.items():
        OUT.write(u'%s,%s\n' % (deanon,anon))
    OUT.close()
    

def anonymize_tweet(tweet):
    """Strips identifying info from a Tweet object created from JSON string

    Tweet object fields:
        https://dev.twitter.com/overview/api/tweets
    """
    fields_to_none = [
        u'geo',
        u'place',
    ]

    fields_to_keep = [
        u'created_at',
        u'entities',
        u'favorite_count',
        u'id',
        u'id_str',
        u'in_reply_to_screen_name',
        u'in_reply_to_status_id',
        u'in_reply_to_status_id_str',
        u'in_reply_to_user_id',
        u'in_reply_to_user_id_str',
        u'lang',
        u'possibly_sensitive',
        u'retweet_count',
        u'retweeted',
        u'retweeted_status',
        u'scopes',
        u'text',
        u'truncated',
        u'user',
    ]

    tweet = clean_twitter_object(tweet, fields_to_none, fields_to_keep)

    tweet[u'id'] = anonymize_tweet_id(tweet[u'id'])
    tweet[u'id_str'] = unicode(tweet[u'id'])

    if u'in_reply_to_screen_name' in tweet and tweet[u'in_reply_to_screen_name']:
        tweet[u'in_reply_to_screen_name'] = anonymize_username(tweet[u'in_reply_to_screen_name'])

    if u'in_reply_to_status_id' in tweet and tweet[u'in_reply_to_status_id']:
        tweet[u'in_reply_to_status_id'] = anonymize_tweet_id(tweet[u'in_reply_to_status_id'])
        tweet[u'in_reply_to_status_id_str'] = unicode(tweet[u'in_reply_to_status_id'])

    if u'in_reply_to_user_id' in tweet and tweet[u'in_reply_to_user_id']:
        tweet[u'in_reply_to_user_id'] = anonymize_user_id(tweet[u'in_reply_to_user_id'])
        tweet[u'in_reply_to_user_id_str'] = unicode(tweet[u'in_reply_to_user_id'])

    if 'retweeted_status' in tweet:
        tweet['retweeted_status'] = anonymize_tweet(tweet['retweeted_status'])

    tweet[u'user'] = anonymize_user(tweet[u'user'])

    if tweet[u'entities']:
        if u'media' in tweet[u'entities']:
            # Fields in Entity Media objects:
            #   https://dev.twitter.com/overview/api/entities#obj-media
            #   - display_url
            #   - expanded_url
            #   - id
            #   - id_str
            #   - indices
            #   - media_url
            #   - media_url_https
            #   - sizes
            #   - source_status_id
            #   - source_status_id_str
            #   - type
            #   - url
            for media_object in tweet[u'entities'][u'media']:
                media_object[u'url'] = anonymize_url(media_object[u'url'])
                media_object[u'display_url'] = anonymize_url(media_object[u'display_url'])
                media_object[u'expanded_url'] = anonymize_url(media_object[u'expanded_url'])
                media_object[u'id'] = anonymize_tweet_id(media_object[u'id'])
                media_object[u'id_str'] = unicode(media_object[u'id'])
                media_object[u'media_url'] = anonymize_url(media_object[u'media_url'])
                media_object[u'media_url_https'] = anonymize_url(media_object[u'media_url_https'])
                if 'source_status_id' in media_object:
                    media_object[u'source_status_id'] = anonymize_tweet_id(media_object[u'source_status_id'])
                    media_object[u'source_status_id_str'] = unicode(media_object[u'source_status_id'])
        if 'text' in tweet:
            tweet['text'] = anonymize_tweet_text(tweet['text'])

        if tweet[u'entities'][u'urls']:
            for url_object in tweet[u'entities'][u'urls']:
                url_object = anonymize_url_object(url_object)
                tweet[u'text'] = tweet[u'text'][0:url_object[u'indices'][0]] + \
                                 url_object[u'url'] + \
                                 tweet[u'text'][url_object[u'indices'][1]:]
        if tweet[u'entities'][u'user_mentions']:
            reversed_mentions = tweet[u'entities'][u'user_mentions']
            reversed_mentions.reverse()
            for user_mention in reversed_mentions:
                user_mention = anonymize_user_mention(user_mention)
    return tweet


def anonymize_tweet_id(tweet_id):
    if not tweet_id:
        return None
    else:
        if tweet_id not in anonymize_tweet_id.mapping:
            anonymize_tweet_id.mapping[tweet_id] = get_random_64_bit_int()
        return anonymize_tweet_id.mapping[tweet_id]
anonymize_tweet_id.mapping = {}


anonymized_urls = {}
def anonymize_url(url):
    if url in anonymized_urls:
        return anonymized_urls[url]
    split_url = url.split("/")
    # Keeps the http:// as well as the domain name.
    if url.startswith("http"):
        new_url = "/".join(split_url[:3])
        the_rest = split_url[3:]
    else:
        new_url = split_url[0]
        the_rest = split_url[1:]
    # Will fail for short urls; handle this case with the
    # except KeyError
    try:
        the_last = the_rest[-1]
        split_the_last = the_last.split(".")
        if len(split_the_last) > 1:
            extension = "." + split_the_last[-1]
        else:
            extension = ""
    except IndexError:
        extension = ""
    anonymize_rest = anonymize_rest_of_url("".join(the_rest))
    new_url += "/" + anonymize_rest + extension
    anonymized_urls[url] = new_url
    return new_url


def anonymize_url_object(url_object):
    # List of fields in URL objects
    #   https://dev.twitter.com/overview/api/entities#obj-url
    #   - display_url
    #   - expanded_url
    #   - indices
    #   - url
    url_object[u'display_url'] = anonymize_url(url_object[u'display_url'])
    url_object[u'expanded_url'] = anonymize_url(url_object[u'expanded_url'])
    url_object[u'url'] = anonymize_url(url_object[u'url'])
    return url_object


def anonymize_user(user):
    """Strips identifying info from a Twitter User object created from JSON string

    Twitter User object fields:
        https://dev.twitter.com/overview/api/users
    """
    fields_to_none = [
        u'url',
    ]

    fields_to_keep = [
        u'created_at',
        u'favourites_count',
        u'followers_count',
        u'friends_count',
        u'geo_enabled',
        u'lang',
        u'listed_count',
        u'statuses_count',
        u'time_zone',
        u'utc_offset',
        u'verified',
        u'screen_name',
    ]
    
    user = clean_twitter_object(user, fields_to_none, fields_to_keep)
    if u'screen_name' in user: 
        user[u'screen_name'] = anonymize_username(user[u'screen_name'])

    return user


def anonymize_user_id(user_id):
    if not user_id:
        return None
    else:
        if user_id not in anonymize_user_id.mapping:
            anonymize_user_id.mapping[user_id] = get_random_64_bit_int()
        return anonymize_user_id.mapping[user_id]
anonymize_user_id.mapping = {}


import math

anonymized_usernames = {}

username_input_chars = list('abcdefghijklmnopqrstuvwxyz0123456789_')
username_output_chars = list('abcdefghijklmnopqrstuvwxyz0123456789_ABCDEFGHIJKLMNOPQRSTUVWXYZ')
username_alphabet = len(username_output_chars)
user2i = dict(zip(username_input_chars,range(len(username_input_chars))))
i2user = dict(zip(range(len(username_output_chars)),username_output_chars))
def int2base_user(x, base):
    if x < 0: sign = -1
    elif x==0: return '0'
    else: sign = 1
    x *= sign
    digits = []
    while x:
        digits.append(i2user[math.floor(x % base)])
        x /= base
    if sign < 0:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)

def anonymize_username(username_anycase):
    """
    Given a username, lowercase it, put it through a 
    salted SHA1 hash, then use the output of that hash
    to generate valid username characters. Reverse them
    such that the least significant bits come first 
    (unclear if that matters), then take the first `n`
    characters (where `n=len(username_anycase)`) as
    the anonymized screen_name
    """
    
    username = username_anycase.lower()
    if username in anonymized_usernames:
        return anonymized_usernames[username]
    hashed = hashlib.pbkdf2_hmac('sha1', username.lower(), SALT, 100)
    hashed_str = int2base_user(int(binascii.hexlify(hashed),16),username_alphabet)[-27:]
    anonymized_username = (hashed_str * 2) [:len(username_anycase)]
    anonymized_usernames[username] = anonymized_username
    return anonymized_username




# url_chars = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~:/?#[]@!$&()*+,;='+"'")
url_chars = list('abcdefghijklmnopqrstuvwxyz0123456789_ABCDEFGHIJKLMNOPQRSTUVWXYZ~-:') #not using some that might cause havoc later to parse
url_alphabet = len(url_chars)
url2i = dict(zip(url_chars,range(len(url_chars))))
i2url = dict(zip(range(len(url_chars)),url_chars))

def int2base_url(x, base,charbase=i2url):
    if x < 0: sign = -1
    elif x==0: return '0'
    else: sign = 1
    x *= sign
    digits = []
    while x:
        digits.append(charbase[math.floor(x % base)])
        x /= base
    if sign < 0:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)



def anonymize_rest_of_url(url_remainder):
    """
    Given the remainder of the URL (beyond domain name),
    put it through a salted SHA1 hash, then use the output 
    of that hash to generate valid url characters. Reverse them
    such that the least significant bits come first 
    (unclear if that matters), then take the first `n`
    characters (where `n=len(url_remainder)`) as
    the anonymized screen_name
    """

    try:
        hashed = hashlib.pbkdf2_hmac('sha1', url_remainder, SALT, 100)
    except UnicodeEncodeError, e:
        try:
            hashed = hashlib.pbkdf2_hmac('sha1', url_remainder[:-1]+"0", SALT, 100) #elipsis?
        except UnicodeEncodeError, e:
            print e
            BAD_URL = 'BROKENUNICODE'*10
            return BAD_URL[:len(url_remainder)]
    hashed_str = int2base_url(int(binascii.hexlify(hashed),16),url_alphabet)[-27:]
    anonymized_url = (hashed_str * 2)[-27:]
    new_url = anonymized_url[-1*len(url_remainder):]
    return new_url


def anonymize_user_mention(user_mention):
    user_mention[u'id'] = anonymize_user_id(user_mention[u'id'])
    user_mention[u'id_str'] = unicode(user_mention[u'id'])
    user_mention[u'name'] = u''
    user_mention[u'screen_name'] = anonymize_username(user_mention[u'screen_name'])
    return user_mention

import re
username_ex = re.compile(r'@[a-zA-Z0-9_]+')
url_ex = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
def anonymize_tweet_text(text):
    # Usernames
    for match in re.finditer(username_ex, text):
        if match:
            start_index = match.start() + 1 #Account for the @
            end_index = match.end()
            unmasked_username = text[start_index:end_index] 
            masked_username = anonymize_username(unmasked_username)
            text = text[:start_index] + masked_username + text[end_index:]
    # URLs
    for match in re.finditer(url_ex, text):
        if match:
            start_index = match.start() 
            end_index = match.end()
            unmasked_url = text[start_index:end_index] 
            masked_url = anonymize_url(unmasked_url)
            text = text[:start_index] + masked_url + text[end_index:]
    return text


def clean_twitter_object(twitter_object, fields_to_none, fields_to_keep):
    for key in twitter_object.keys():
        if key in fields_to_none:
            twitter_object[key] = None
        elif key not in fields_to_keep:
            del twitter_object[key]
    return twitter_object


used_64_ints = set([])
def get_random_64_bit_int():
    """Generates random 64 bit ints, though makes sure they 
    fit into an <int>, to make it play nice with various
    databases.
    """
    new_int = random.getrandbits(64) % sys.maxint
    return new_int


def validate_tweet(tweet):
    valid = True
    if tweet[u'entities']:
        if tweet[u'entities'][u'hashtags']:
            for hashtag in tweet[u'entities'][u'hashtags']:
                # The '+1' removes the '#' prefix from the hashtag
                sliced_tag = tweet[u'text'][hashtag[u'indices'][0]+1:hashtag[u'indices'][1]]
                if sliced_tag != hashtag[u'text'] and hashtag[u'indices'][1] < 140:
                    valid = False
                    print "Hashtag mismatch.  From entity mention: '%s'  From string offsets: '%s'  End Index: %s" % \
                        (hashtag[u'text'], sliced_tag, hashtag[u'indices'][1])
        if tweet[u'entities'][u'user_mentions']:
            for user_mention in tweet[u'entities'][u'user_mentions']:
                # The '+1' removes the '@' prefix from the username
                screen_name = tweet[u'text'][user_mention[u'indices'][0]+1:user_mention[u'indices'][1]]
                if screen_name != user_mention[u'screen_name'] and user_mention[u'indices'][1] <140:
                    valid = False
                    print "Screen name mismatch.  From entity mention: '%s'  From string offsets: '%s'  End Index: %s" % \
                        (user_mention[u'screen_name'], screen_name, user_mention[u'indices'][1])
    return valid



if __name__ == "__main__":
    main()
