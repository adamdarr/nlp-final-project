#!/usr/bin/python
import string
import copy
import math
import sys
import json
import heapq
import re
import temp_tfidf_search

from collections import deque

# JSON Business Listings
BUSINESS_LISTINGS = ('/Users/DoctorProteus/Documents/Classes/HumanLanguageTech/nlp-final-project/yelp_dataset_challenge_' +
               'academic_dataset/yelp_academic_dataset_business.json')

# Number of Listings to search
NUM_LISTINGS = 50000

# K, the number of results to return
THRESHOLD = 5000


class BusinessEntry:
    def __init__(self, biz_info, biz_attr, tok):
        self.id = biz_info[0]
        self.name = biz_info[1]
        self.address = biz_info[2]
        self.neighborhoods = biz_info[3]
        self.hours = biz_info[4]
        self.categories = biz_info[5]
        self.tokens = tok
        self.attributes = biz_attr

    def match(self, words):
        for word in words:
            if word in self.tokens:
                return True
        return False

class BizFilter:
    def __init__(self, query_tokens):
        self.tokens = query_tokens
        self.businesses = {}
        self.query_matches = {}
        self.intersection_matches = []
        print "Building business data..."
        self.initialize_data()
        print "DATA INITIALIZED.\n"
        self.get_matches()


    def initialize_data(self):
        count = 0
        data = []
        with open(BUSINESS_LISTINGS) as f:
            for line in f:
                data.append(json.loads(line))
                if count == NUM_LISTINGS:
                    break
                count += 1

        for biz in data:
            info = ""
            business_id = biz['business_id']
            business_name = biz['name']
            info += (" " + business_name)
            address = biz['full_address']
            info += (" " + address)
            neighborhoods = biz['neighborhoods']
            for neighborhood in neighborhoods:
                info += (" " + neighborhood)
            categories = biz['categories']
            for category in categories:
                info += (" " + category)
            hours = biz['hours']
            attributes = dict((k.lower(), v) for k, v in biz['attributes'].iteritems())
            tokens = words(info)
            business_info = (business_id, business_name, address, neighborhoods, hours, categories)
            business = BusinessEntry(business_info, attributes, tokens)
            self.businesses[business_id] = business

    def get_matches(self):
        for k, v in self.businesses.items():
            if v.match(self.tokens):
                self.query_matches[k] = v

    def get_intersection(self, results, doc_info):

        print 'finding intersection of lists\n'
        for result in results:
            if doc_info.business_id[result] in self.query_matches:
                self.intersection_matches.append(self.query_matches[doc_info.business_id[result]])
        return self.intersection_matches



def words(text):
    """An iterator over tokens (words) in text. Replace this with a
    stemmer or other smarter logic.
    """

    for word in text.split(" "):
        # normalize words by lowercasing and dropping non-alpha
        # characters
        normed = re.sub('[^a-z]', '', word.lower())

        if normed:
            yield normed


def main():
    revs = []
    count = 0
    print "Prepping reviews..."
    with open(temp_tfidf_search.REVIEW_FILE) as file:
        for line in file:
            revs.append(json.loads(line))
            if count == temp_tfidf_search.REVIEWS_TO_READ:
                break
            count += 1

    docs = {}
    for review in revs:
        business_id = review['business_id']

        if business_id in docs:
            docs[business_id] += ' ' + review['text'].encode('utf-8')
        else:
            docs[business_id] = review['text'].encode('utf-8')

    doc_info = temp_tfidf_search.DocInfo()

    index = 0
    for business_id, review in docs.items():
        review = review.lower()
        review = review.translate(string.maketrans("",""), string.punctuation)

        tokens = review.split(' ')

        doc_info.add_entries(business_id, index, tokens)

        index += 1

    print "DATA INITIALIZED.\n"
    print "Building business data..."

    data = []
    count = 0
    with open(BUSINESS_LISTINGS) as file:
        for line in file:
            data.append(json.loads(line))
            if count == NUM_LISTINGS:
                break
            count += 1

    businesses = {}
    for biz in data:
        info = ""
        business_id = biz['business_id']
        business_name = biz['name']
        info += (" " + business_name)
        address = biz['full_address']
        info += (" " + address)
        neighborhoods = biz['neighborhoods']
        for neighborhood in neighborhoods:
            info += (" " + neighborhood)
        categories = biz['categories']
        for category in categories:
            info += (" " + category)
        hours = biz['hours']
        attributes = dict((k.lower(), v) for k, v in biz['attributes'].iteritems())
        tokens = words(info)
        business_info = (business_id, business_name, address, neighborhoods, hours, categories)
        business = BusinessEntry(business_info, attributes, tokens)
        businesses[business_id] = business

    print "DATA INITIALIZED.\n"

    while True:
        query = raw_input("Please enter your search query: ")
        query_tokens = query.lower().split(' ')

        query_matches = {}
        count = 0
        print '-----------------------------------------------'
        print '\tBusiness Name'
        for k, v in businesses.items():
            if v.match(query_tokens):
                query_matches[k] = v
                if count < THRESHOLD:
                    print '%s.\t%s\t' % (count + 1, v.name)
                    count += 1
        print '-----------------------------------------------\n'

if __name__ == "__main__": main()
