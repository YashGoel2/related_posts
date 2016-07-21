from nltk import word_tokenize
from nltk.corpus import stopwords

english_stopwords = stopwords.words('english')    # get english stop words

# test document
document = '''A moody child and wildly wise
Pursued the game with joyful eyes
'''
print type(document)
# first tokenize your document to a list of words
words = word_tokenize(document)
print(words)

# the remove all stop words
content = [w for w in words if w.lower() not in english_stopwords]
print(content)
