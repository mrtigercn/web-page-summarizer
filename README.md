web-page-summarizer
===================

Web page text summarizer with nltk and goose

adopted from the original tokenizer code - https://gist.github.com/shlomibabluki/5473521 to include nltk functions and goose integration to pull content from a url

The idea behind the class is as following

1. split the text into sentences

2. create a clean version of the text - remove stop words, and stem the words so when we compare the words we compear between similar words even if originally they were written in different forms

3. create sentence dictionary where each word in each sentence get a rank based on the number of times it appear in the whole text, the idea is if a word appear many times in the text it must be an important word (thats why we  remove the stop words at step 2 so words like 'The', 'a', 'and', 'or' would not affect the result

4. run a loop on each paragraph and see if it has sentences with high rank, if so - consider them apart of the summarized text
