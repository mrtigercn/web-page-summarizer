from __future__ import division
import re
from goose import Goose
import nltk.data
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.tokenize import word_tokenize
import sys

# summarizer class
# the idea behind the class is as following
# 1. split the text into sentences
# 2. create a clean version of the text - remove stop words, and stem the words
#    so when we compare the words we compear between similar words
#    even if originally they were written in different forms
# 3. create sentence dictionary where each word in each sentence get a rank 
#    based on the number of times it appear in the whole text, the idea is if a word
#    appear many times in the text it must be an important word (thats why we 
#    remove the stop words at step 2 so words like 'The', 'a', 'and', 'or' would not affect the result
# 4. run a loop on each paragraph and see if it has sentences with high rank,
#    if so - consider them apart of the summarized text
class summarizer( object ):
    
#   split a paragraph into sentences.
#   you can use the following replace and split functions or the nltk sentence tokenizer
#   content = content.replace("\n", ". ")
#   return content.split(". ")
    def splitToSentences(self, content):
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        return tokenizer.tokenize(content)
       
#    split text into paragraphs
#    need to find out if there is a better way to do this with nltk
    def splitToParagraphs(self, content):
        return content.split("\n\n")
        
        
#   get the intersection between two sentences
#   using python native intersection function 
#   to find if an item of a set exist in another set
    def getIntersection(self, sent1, sent2):
        
#       if you are passing an unsplited sentece this could be done in this form
#       s1 = set( sent1.split(" ") )
#       s2 = set( sent2.split(" ") )
        s1 = set( sent1 )
        s2 = set( sent2 )
        
#       if the senteces are empty the rank of this will be 0
        if ( len(s1) + len(s2) ) == 0:
            return 0
        
#       return the length of the intersection divided by half the length of the two original sentences
        return len(  s1.intersection(s2) ) / ( (len(s1) + len(s2) ) / 2 )
        
        
#   purify a sentence, we use this to create a key for an object form a sentence, 
#   therefor it could not contain spaces or panctuation         
    def purifySentence(self, sentence):
        sentence = re.sub( r'\W+', '', sentence)
        return sentence
    
#     stem a sentence
#    loop through each word and find the stem of it using the 
#    nltk PorterStemmer. you can use a different stemmer if you like
#    like the LancasterStemmer or RegexpStemmer('ing') to remove specific 
#    attributes from a word
    def stemSentence(self, sentence, stemmer):
        words = []
        for word in sentence:
            w = stemmer.stem(word)
            words.append( w )
        return words
    
#    steam and remove any stop words form a sentence
#    this will remove words such as 'The', 'and', 'or' that has 
#    no value in regard to the value of the sentence
    def steamAndRemoveStopWords(self, sentence, stemmer ):  
           s = word_tokenize(sentence)
           s1 = [w for w in s if not w in stopwords.words('english')]
           s2 = self.stemSentence( s1, stemmer )
           return s2
    
#   this function is the heart of the summerize
#   here we'll give each sentence rank based on 
#   how many words it has in similarity to other sentences
    def rankSentences(self, content ):
        
#       create a list of all sentences
        paragraphs = self.splitToParagraphs(content)
        sentences = []
        for p in paragraphs:
            s = self.splitToSentences(p) 
            for x in s:
                sentences.append(x)
            
        n = len( sentences )
        
#       stem and remove stopwords
        stemmer = PorterStemmer()
        clean_sentences = [ self.steamAndRemoveStopWords(x, stemmer) for x in sentences ]
        
#       create an empty values set and fill it with the 
#       intersection value with all the other sentences
        values = [ [0 for x in xrange(n)] for x in xrange(n) ]
        for i in range(0, n):
            for j in range(0, n):
                values[i][j] = self.getIntersection( clean_sentences[i], clean_sentences[j] )
        
#       create sentece dictionary set and fill it with the accumulated value of each sentence
        sentence_dictionary = {}
        for i in range(0, n):
            score = 0
            for j in range(0, n):
                if j == i:
                    continue
                score += values[i][j]
            sentence_dictionary[ self.purifySentence( sentences[i])  ] = score
        
        return sentence_dictionary


#   get the best sentence from each paragraph
    def getBestSentence(self, paragraph, sentence_dictionary):
        
        sentences = self.splitToSentences( paragraph )
        
#       ignore sentences that are too short
        if len( sentences ) < 2:
            return ""
         
        best_sentence = ""
        max_score = 0
        
#       loop through each sentence and find it its value 
#       in the sentence dictionary is the highest in the paragraph
        for s in sentences:
            striped = self.purifySentence(s)
            if striped:
                  if sentence_dictionary[striped] > max_score:
                    max_score = sentence_dictionary[striped]
                    best_sentence = s
        
        return best_sentence
        
        
        
#   summarize the text    
    def summarize(self, content, sentence_dictionary, title):
        
        paragraphs = self.splitToParagraphs( content )
        
        summary = []
        
#       this is actually not recommanded as the title many times is not relevant for the topic
#       or written in a provocative way, many times a title will be the opposite of the subject
        if title:
            summary.append( title.strip() )
            summary.append("")
        
        for p in paragraphs:
            sentence = self.getBestSentence(p, sentence_dictionary)
            if sentence:
                summary.append( sentence )
        
        return ("\n").join(summary)
        
#---------------------------------end of summarizer class ---------------------------------#
   
# using the Goose library to extract the content of a url
# returing the title of it and the content of the page.
# The great thing about using Goose it that it already take
# care of everything related to striping tags and such
def get_content( url ):
    
    g = Goose()
    article = g.extract( url=url )
    
    title = article.title
    content = article.cleaned_text
    
    return title, content



# Summarize the content
def summarize( content, title, summarizer, max_len ):
    
    sentence_dictionary = summarizer.rankSentences( content )  
    summary = summarizer.summarize(content, sentence_dictionary, title)
    
#     if the content is still too long, lets summarize it again
    if len( summary ) > max_len:
        return summarize( summary, False, summarizer, max_len )
    else:
        return summary

# grab the content of a url and return a summarized version of it
def URLSummarizer( url, max_len ):
    
    title, content = get_content( url )
    sm = summarizer()
    summary = summarize( content, title, sm, max_len )

#     # Print the ratio between the summary length and the original length
#     print ""
#     print "Original Length %s" % (len(title) + len(content))
#     print "Summary Length %s" % len(summary)
#     print "Summary Ratio: %s" % (100 - (100 * (len(summary) / (len(title) + len(content)))))
    
    return summary



if __name__ == '__main__':
    
    if len( sys.argv ) > 1:
        url = sys.argv[1]
        max_len = sys.argv[2]
    else:
        url = "http://en.wikipedia.org/wiki/Flatiron_Building"
        max_len = 160
      
    summary = URLSummarizer( url, max_len )
    print summary
