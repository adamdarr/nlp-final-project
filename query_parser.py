import nltk
from nltk.corpus import wordnet
# Using the Natural Language Tookit
# http://www.nltk.org/
# https://github.com/nltk/nltk

	
def parse(raw_query, EXPAND_SET = False):
	"""Chunk raw_query based on the rule in master_chunk, return a list of found chunks"""
	
	# tokenize and tag the query using nltk tools, use .lower() to standardize the input
	tokenized_query = nltk.word_tokenize(raw_query.lower())
	tagged_query = nltk.pos_tag(tokenized_query)
	
	#master_chunk = r"Chunk: {(<VB\w?>|<JJ>*|<RB\w?>)<DT>?(<NN\w?>+)}" 
	
	
	# master_chunk now captures prepositional phrase, as they are typically part of one thought.
	
	master_chunk = r"Chunk: {((<JJ\w?>*|<RB\w?>*)<DT>?(<NN\w?>+))(<IN>((<JJ>*|<RB\w?>*)<DT>?(<NN\w?>+)))*}" # Regex to identify chunks that may be useful 
	#					master_chunk breakdown
	#
	#	First half : ((<JJ>*|<RB\w?>*)<DT>?(<NN\w?>+))
	#	<JJ\w?>* | <RB\w>?>* allows an arbitrary number of adjectives to precede the noun
	# 	"\w" is "any character" and  allows the capture of all JJ and RB tags, which include JJ, JJR, JJS, RB, RBR, and RBS
	#	<DT>? allows for exactly one (1) or zero (0) determiner, often this will capture things like "no" and then a noun
	# 	(<NN\w>+) captures one (1) or arbitrarily more nouns
	#	
	#	Second half: (<IN>((<JJ>*|<RB\w?>*)<DT>?(<NN\w?>+)))*
	#	<IN> captures prepostions "of", "with", and so on.
	# 	The rest of the expression is the same as the first half 
	# 	The final * (kleene star) allows zero (0) or more prepositional phrases to be captured
	
	
	master_parser = nltk.RegexpParser(master_chunk) # Create the parser from the Regex
	master = master_parser.parse(tagged_query) # Parse the query previously tagged
	
	chunk_list = []
	keywords = []
	for phrase in master:
		if (not isinstance(phrase, tuple)): # all non-chunks are tuples, a chunk is a nltk.tree type
			chunk_list.append(phrase)
			tmp = ""
			for word in phrase: # generate keyword phrases from the chunks
				tmp += word[0] + " "
			
			tmp = tmp[:-1] # Remove final space
			keywords.append(tmp)
			
	if EXPAND_SET: # defualt is not to expand
		# combine the two lists, using set() to remove any repeated phrases
		return list(set(generate_keywords(chunk_list) + keywords))
	else:
		return keywords
	
	
	
def generate_keywords(parse):
	# A list of temporal expressions that will be captured later and handled differently 
	times = [	'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
			'sun', 'mon', 'tue', 'wed', 'thr', 'fri', 'sat',
			'night', 'nights', 'midnight', 'duskiness', 'evening', 'darkness', 'nighttime',
			'midday', 'dawn', 'teatime']
	keywords = []
	parse = process_list(parse) # process the parse list to contain lists instead of tuples
	
	
	for phrase in parse:
		for word in phrase:
			
			if word[0] in times: # Choosing to not expand on phrases that are temporal to help simplify expansion
				break

			if word[1].startswith("NN"): # Choosing to not expand on anything except for nouns, to limit expansion, may change.
				syns = get_synonyms(word[0])
				# generate as before with synonyms in place of the words 
				for syn in syns:
					word[0] = syn
					tmp = ""
					for word1 in phrase:
						# generate new keyword phrase
						tmp += word1[0] + " "
					tmp = tmp[:-1]
					keywords.append(tmp)
					
	return keywords
		
	
def process_list(parse):
	# nltk returns lists of chunks as tuples.
	# To make the generation of the expanded list easier, make the tuples into lists,
	# so they can be edited, unlike tuples.
	parse1 = [] # new parse list
	for phrase in parse: 
		phrase1 = [] # new phrase list for the current phrase
		for word in phrase: 
			phrase1.append(list(word)) # convert to a list
		parse1.append(phrase1)
		
	return parse1

def get_synonyms(word):
	# Capture all of the synonyms that wordnet has for the given word and return them in a list
	synonyms = []
	for syn in wordnet.synsets(word):
		for l in syn.lemmas():
			synonyms.append(l.name())
	return synonyms	
	
def demo():
	# run a demo
	toParse = "Open wednesday nights, has hot wings, beer, and no smoking."
	print(parse(toParse))
	
if __name__ == "__main__":
	demo()
