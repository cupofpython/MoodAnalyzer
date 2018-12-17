import json
import nltk 
import requests 
import operator
from requests_oauthlib import OAuth1
from nltk.corpus import sentiwordnet as s

""" Utilizing SentiWordNet lexical resource for opinion mining. This resource rates words based on positivity, negativity, and objectivity. 
	It can be found in the Natural Language Toolkit Corpus (NLTK) library. """

def process(text):
	while True:
		word, space, text = text.partition(' ')
		if space:
			yield word
		else: 
			return 

def update_dic(item, dic):
	try:
		dic[item]+=1
	except:
		dic[item]=1

""" Morning = 4am to 12pm
	Afternoon = 12pm to 8pm
	Night = 8pm to 4am """
def get_time(hour):
	hour = int(hour)
	if hour in range(4, 12):
		return 'morning'
	elif hour in range(12, 20):
		return 'afternoon'
	elif hour in range(20, 24) or hour in range (0, 4):
		return 'night'


def setup(url, auth):
	requests.get(url, auth=auth)

def checkin(screen_name, auth):
	tweets_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name='+screen_name+'&count=all'
	tweets = requests.get(tweets_url, auth=auth)
	name_url = 'https://api.twitter.com/1.1/users/lookup.json?screen_name='+screen_name 
	user = requests.get(name_url, auth=auth)

	count = 0
	total_pos = 0
	total_neg = 0 
	day_dic = {}
	month_dic = {}
	time_dic = {}
	loc_dic = {} 

	for tweet in tweets.json():
		word_gen = process(tweet['text'])
		pos_tweet = 0
		neg_tweet = 0 
		i = 0 
		for w in word_gen:
			w = w.lower()
			word = s.senti_synsets(w, 'a')
			if len(word) > 0: 
				if word[0].neg_score() > word[0].pos_score():
					total_neg+=1
					neg_tweet+=1
					count+=1
				elif word[0].neg_score() < word[0].pos_score():
					total_pos+=1
					pos_tweet+=1
					count+=1
				else:
					count+=1
		if neg_tweet > pos_tweet:
			creation_info = tweet['created_at'].split()
			update_dic(creation_info[0],day_dic)
			update_dic(creation_info[1],month_dic)
			hour = creation_info[3].split(':')[0]
			time = get_time(hour)
			update_dic(time,time_dic)
			if tweet['coordinates'] != None: 
				update_dic(tweet['coordinates'], loc_dic) 
	if len(loc_dic) > 0: 
		support_time = max(time_dic.iteritems(), key=operator.itemgetter(1))[0]
	else: 
		support_time = "ignore"

	return {'name':user.json()[0]['name'], 
			'pos_per':(float(total_pos)/float(count))*100, 
			'neg_per':(float(total_neg)/float(count))*100, 
			'total_word':count, 
			'most_distress':max(time_dic.iteritems(), key=operator.itemgetter(1))[0],
			'support': support_time}
	#return user.json()[0]['name'], (float(total_pos)/float(count))*100, (float(total_neg)/float(count))*100, count, max(time_dic.iteritems(), key=operator.itemgetter(1))[0],support_time
	#if len(loc_dic) > 0: 
		#print "Needs support at:",max(time_dic.iteritems(), key=operator.itemgetter(1))[0]
	"""
	print "Name:",user.json()[0]['name']
	print "Positive Word Percentage: ",(float(total_pos)/float(count))*100
	print "Negative Word Percentage: ",(float(total_neg)/float(count))*100
	print "Total Words Recognized: ",count
	print "Most distressed at:",max(time_dic.iteritems(), key=operator.itemgetter(1))[0]
	if len(loc_dic) > 0: 
		print "Needs support at:",max(time_dic.iteritems(), key=operator.itemgetter(1))[0]
	"""

