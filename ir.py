#!/usr/bin/python

import argparse, os, nltk, pymongo
from math import log10, sqrt

corpus = os.getcwd()+'/corpus/'
stopwords = open('stopwords').read().split('\n')
tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')

def parse_args(args=None):
	
	"""
	Parse command line arguments.
	"""

	parser = argparse.ArgumentParser(description="A text based search.")
	parser.add_argument("--index", action="store_true", help="Build Index.")

	if args:
		return parser.parse_args(args)
	return parser.parse_args()



def probe_corpus():
	
	file_stack = []

	for path, subdirs, files in os.walk(corpus):
		for name in files:
			file_stack.append(os.path.join(path, name))
	
	return file_stack



def tokenize(text):
	
	'''
	tokenization and stopword exclusion	
	'''
		
	words = [ word for word in tokenizer.tokenize(text) if len(word)>1 and not word.isdigit() and word not in stopwords ] #tokenize non digit with length more than 1
	words += [ nltk.PorterStemmer().stem_word(word) for word in words ] #add stemmed words along

	return words


def word_cloud(text):
	
	cloud = {}

	for word in tokenize(text):
		if word in cloud.keys():
			cloud[word] += 1
		else:
			cloud[word] = 1
	
	return cloud


def indexing():
	
	client = pymongo.MongoClient('localhost', 27017)
	client.drop_database('Search_Engine')
	db = client.Search_Engine
	fw_index = db.fw_index
	
	for file_name in probe_corpus():
		
		index = {}
		text = open(file_name).read().lower()
		title = text.split('\n')[0]
			
		index['file_name'] = file_name
		index['title'] = title
		index['terms'] = word_cloud(text)

			
		fw_index.insert_one(index).inserted_id


def search(keywords):
	
	client = pymongo.MongoClient('localhost', 27017)
	db = client.Search_Engine
	fw_index = db.fw_index
	terms = word_cloud(keywords)
	n = {}
	relevances = {}

	for term in terms:
		n[term] = 0

	for an_index in fw_index.find():
		for term in terms:
			if term in an_index['terms']:
				n[term]+=1

	for an_index in fw_index.find():
		no_of_terms = len(an_index['terms'])
		relevances[an_index['file_name']] = 0
		for term in terms:
			no_of_occurence = 0
			if term in an_index['terms']:
				no_of_occurence = an_index['terms'][term]
			TF = log10(1+no_of_occurence*1.00/no_of_terms)
			IDF = 1.00/n[term]

			relevances[an_index['file_name']] += TF*IDF
	
	for link in sorted(relevances, key=relevances.get)[::-1][:10]:
		if relevances[link]!=0:
			print link, relevances[link]


if __name__ == '__main__':
	args = parse_args()
	if args.index:
		indexing()
	else:
		search(raw_input("Enter_keywords: "))

