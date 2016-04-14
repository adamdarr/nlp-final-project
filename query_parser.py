import nltk
# Using the Natural Language Tookit
# http://www.nltk.org/
# https://github.com/nltk/nltk

def parseQuery(raw_query):
	"""Chunk raw_query based on the rule in master_chunk, return a list of found chunks"""
	tokenized_query = nltk.word_tokenize(raw_query.lower())
	tagged_query = nltk.pos_tag(tokenized_query)
	
	master_chunk = r"Chunk: {(<VB\w?>|<JJ>*|<RB\w?>)<DT>?(<NN\w?>+)}" # Regex to identify chunks that may be useful
	master_parser = nltk.RegexpParser(master_chunk) # Create the parser from the Regex
	master = master_parser.parse(tagged_query) # Parse the query previously tagged
	
	keyword_list = []
	for itm in master:
		if not isinstance(itm, tuple): # all non-chunks are tuples, a chunk is a nltk.tree type
			tmp = ""
			# Create a string for each keyword phrase, and add it to the list
			for key in itm:
				tmp += key[0] + " "
			tmp = tmp[:-1]
			keyword_list.append(tmp)
	return keyword_list


def demo():
	# run a demo
	toParse = "Open wednesday nights, has buffalo wings, beer, and no smoking."
	print(parseQuery(toParse))
	
if __name__ == "__main__":
	demo()
