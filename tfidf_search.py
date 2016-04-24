#!/usr/bin/python
import string
import copy
import math
import sys
import json
import heapq

from collections import deque

# JSON file containing yelp dataset challenge reviews
REVIEW_FILE = ('/Users/adam/Downloads/yelp_dataset_challenge_' +
               'academic_dataset/yelp_academic_dataset_review.json')

# Specifies the amount of reviews to be read from the beginning of the file
REVIEWS_TO_READ = 20000

# Specifies the number of results to be returned
NUM_RESULTS = 20

class InvertedIndexEntry:
    def __init__(self, term):
        self.term = term
        self.freq = 1
        self.postings_list = deque([])
        self.doc_positions = {}

    def increment_freq(self):
        self.freq += 1

    def append_posting(self, doc_id):
        self.postings_list.append(doc_id)

    def append_position(self, doc_id, pos):
        if doc_id in self.doc_positions:
            self.doc_positions[doc_id].append(pos)
        else:
            self.doc_positions[doc_id] = [pos]

class DocInfo:
    def __init__(self):
        self.index_counts = {}
        self.doc_lengths = {}
        self.business_id = {}

    def add_entries(self, business_id, doc_id, tokens):
        self.doc_lengths[doc_id] = len(tokens)
        self.business_id[doc_id] = business_id

        pos = 0
        for token in tokens:
            if token in self.index_counts:
                index_entry = self.index_counts[token]
                index_entry.increment_freq()

                if index_entry.postings_list[-1] < doc_id:
                    index_entry.append_posting(doc_id)

                index_entry.append_position(doc_id, pos)
            else:
                index_entry = InvertedIndexEntry(token)
                index_entry.append_posting(doc_id)
                index_entry.append_position(doc_id, pos)

                self.index_counts[token] = index_entry

            pos += 1

    def intersect(self, w1, w2):
        p1 = self.index_counts[w1].postings_list
        p2 = self.index_counts[w2].postings_list

        t1 = copy.copy(p1)
        t2 = copy.copy(p2)

        answer = []
        while len(p1) != 0 and len(p2) != 0:
            doc_id1 = p1[0]
            doc_id2 = p2[0]

            if doc_id1 == doc_id2:
                answer.append(doc_id1)
                p1.popleft()
                p2.popleft()
            elif doc_id1 < doc_id2:
                p1.popleft()
            else:
                p2.popleft()

        self.index_counts[w1].postings_list = t1
        self.index_counts[w2].postings_list = t2

        return answer

    def positional_intersect(self, w1, w2, k):
        if w1 in self.index_counts and w2 in self.index_counts:
            p1 = self.index_counts[w1].postings_list
            p2 = self.index_counts[w2].postings_list
        else:
            return {}

        t1 = copy.copy(p1)
        t2 = copy.copy(p2)

        answer = {}
        while len(p1) != 0 and len(p2) != 0:
            doc_id1 = p1[0]
            doc_id2 = p2[0]

            if doc_id1 == doc_id2:
                l = []
                pp1 = self.index_counts[w1].doc_positions[doc_id1]
                pp2 = self.index_counts[w2].doc_positions[doc_id2]

                pp1_idx = 0
                pp2_idx = 0

                while pp1_idx < len(pp1):
                    if abs(pp1[pp1_idx] - pp2[pp2_idx]) < k:
                        l.append(pp2[0])
                    elif pp2[pp2_idx] > pp1[pp1_idx]:
                        break

                    pp2_idx += 1

                    while len(l) != 0 and (l[0] - pp1[pp1_idx]) > k:
                        l.pop(0)

                    for pos in l:
                        answer[doc_id1] = pp1[pp1_idx], pos

                    pp1_idx += 1

                    if pp2_idx >= len(pp2):
                        break

                p1.popleft()
                p2.popleft()
            elif doc_id1 < doc_id2:
                p1.popleft()
            else:
                p2.popleft()

        self.index_counts[w1].postings_list = t1
        self.index_counts[w2].postings_list = t2

        return answer

    def tf(self, term, doc_id):
        if term in self.index_counts and doc_id in self.index_counts[term].doc_positions:
            doc_positions = self.index_counts[term].doc_positions[doc_id]
            term_appearances = len(doc_positions)
            total_terms = self.doc_lengths[doc_id]

            return float(term_appearances) / float(total_terms)
        else:
            return 0.0

    def idf(self, term):
        if term in self.index_counts:
            total_documents = len(self.doc_lengths)
            documents_with_term = len(self.index_counts[term].postings_list)

            return math.log(total_documents / documents_with_term)
        else:
            return 0.0

    def tfidf(self, term, doc_id):
        return self.tf(term, doc_id) * self.idf(term)

def main():
    print "INITIALIZING DATA ..."

    data = []
    count = 0
    with open(REVIEW_FILE) as f:
        for line in f:
            data.append(json.loads(line))

            if count == REVIEWS_TO_READ:
                break

            count += 1

    docs = {}
    for review in data:
        business_id = review['business_id']

        if business_id in docs:
            docs[business_id] += ' ' + review['text'].encode('utf-8')
        else:
            docs[business_id] = review['text'].encode('utf-8')

    doc_info = DocInfo()
    
    index = 0
    for business_id, review in docs.items():
        review = review.lower()
        review = review.translate(string.maketrans("",""), string.punctuation)

        tokens = review.split(' ')

        doc_info.add_entries(business_id, index, tokens)

        index += 1

    print "DATA INITIALIZED.\n"

    while True:
        query = raw_input("Please enter your search query: ")
        query_tokens = query.lower().split(' ')

        if len(query_tokens) > 1:
            intersections = []
            for i in range(len(query_tokens) - 1):
                intersection = doc_info.positional_intersect(query_tokens[i], query_tokens[i+1], 2)
                intersections.append(intersection)

            for i in range(len(query_tokens) - 1):
                if i == 0:
                    keys_intersections = set(intersections[i].keys())
                else:
                    keys_intersections = keys_intersections & set(intersections[i].keys())

            s = ''
            for key in keys_intersections:
                s += doc_info.business_id[key] + ', '

            if s != '':
                print 'Exact matches: %s' % s
            else:
                print 'No exact matches.'

        query_tfidfs = {}
        for i in range(len(docs)):
            query_tfidfs[i] = 0
            for token in query_tokens:
                query_tfidfs[i] += doc_info.tfidf(token, i)

        results = heapq.nlargest(NUM_RESULTS, query_tfidfs, key=query_tfidfs.get)

        print '-----------------------------------------------'
        print '\tBusiness ID\t\tTF-IDF'

        count = 1
        for result in results:
            print '%s.\t%s\t%s' % (count, doc_info.business_id[result], query_tfidfs[result])
            count += 1

        print '-----------------------------------------------\n'

def test():
    doc_info = DocInfo()
    doc_info.add_entries(1, 1, ['the', 'bride', 'to', 'be', 'to', 'be'])
    doc_info.add_entries(2, 2, ['to', 'be'])

    print(doc_info.positional_intersect('to', 'be', 2))

if __name__ == "__main__": main()
