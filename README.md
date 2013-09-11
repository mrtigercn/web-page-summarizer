web-page-summarizer
===================

Web page text summarizer with nltk and goose

adopted from the original tokenizer code - https://gist.github.com/shlomibabluki/5473521 to include nltk functions and goose integration to pull content from a url

The idea behind the class is as following

1. split the text into sentences

2. create a clean version of the text - remove stop words, and stem the words so when we compare the words we compear between similar words even if originally they were written in different forms

3. create sentence dictionary where each word in each sentence get a rank based on the number of times it appear in the whole text, the idea is if a word appear many times in the text it must be an important word (thats why we  remove the stop words at step 2 so words like 'The', 'a', 'and', 'or' would not affect the result

4. run a loop on each paragraph and see if it has sentences with high rank, if so - consider them apart of the summarized text


Modified methods – Use nltk to:

1. remove stop words form each sentence, since we are looking to rank sentences based on repeated words, if we wont filter words like ‘and’, ‘the’, ‘or’, ‘a’ we will effect the value of the sentence, there for we use nltk stopwords class, if we find a word that is included in the stop words we won’t include it in the value of the sentence.

2. stem the sentence, writing is often inconsistent, many times we write the same word in different forms, while the word actually has the same value, for example ‘read’ and ‘reading’ or ‘car’ and ‘cars’, when we stem a word we find the root of the word and will use it to create the rank – intersection with other words of the same stem.

#    stem a sentence
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
           
Extracting the content of a url is easy when you are using Goose
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
