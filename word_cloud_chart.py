import json
import numpy as np
from collections import Counter
from PIL import Image
from os import path
import os
import random
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud, STOPWORDS,  get_single_color_func
import matplotlib.pyplot as plt

class SimpleGroupedColorFunc(object):
    def __init__(self, color_to_words, default_color):
        self.word_to_color = {word: color
                              for (color, words) in color_to_words.items()
                              for word in words}

        self.default_color = default_color

    def __call__(self, word, **kwargs):
        return self.word_to_color.get(word, self.default_color)


class GroupedColorFunc(object):
    def __init__(self, color_to_words, default_color):
        self.color_func_to_words = [
            (get_single_color_func(color), set(words))
            for (color, words) in color_to_words.items()]

        self.default_color_func = get_single_color_func(default_color)

    def get_color_func(self, word):
        try:
            color_func = next(
                color_func for (color_func, words) in self.color_func_to_words
                if word in words)
        except StopIteration:
            color_func = self.default_color_func

        return color_func

    def __call__(self, word, **kwargs):
        return self.get_color_func(word)(word, **kwargs)


num_reviews_to_display = 50
max_words = 150
d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

with open(path.join(d, 'reviews_south_ken.json'), 'r') as reviews:
    data = json.load(reviews)
    review_string = ''
    for x in list(data.keys()):
        if int(x) <= num_reviews_to_display:
            review_string += data[x][5].strip('Review: ').lower()
            review_string += '\n'
reviews.close()

review_string_split = review_string.split(" ")

tokens = nltk.word_tokenize(review_string)
tags = nltk.pos_tag(tokens)
words = [word for word, pos in tags if (pos == 'JJ' or pos == 'JJR' or pos == 'JJS')]
# words = [w for w in review_string_split if w.isalpha()]

stopwords = nltk.corpus.stopwords.words(["english", "italian"])
new_stopwords = ['\'', 'us', 'one', 'de', 'would', 'also', 'go', 'bit', 'south', 'went', 'et', 'get', 'two',
                 'could', 'stato', 'stati', 'got', 'Kensington', 'ben', 'qui', 'stata', 'every', 'à',
                 'po', 'prima', 'und', 'que', 'due', '.', '..', '...', '....', '!', '(', ')', '-']
stopwords.extend(new_stopwords)
words = [w for w in words if w.lower() not in stopwords]

fd = nltk.FreqDist(words)
# print(fd.most_common(max_words))

pos_words = []
neg_words = []
neu_words = []

sia = SentimentIntensityAnalyzer()

for x in words:
    if sia.polarity_scores(x)['compound'] > 0:
        pos_words.append(x)
    elif sia.polarity_scores(x)['compound'] < 0:
        neg_words.append(x)
    else:
        neu_words.append(x)


with open(path.join(d,'word_cloud_words.txt'), 'w') as fp:
    for item in words:
        # write each item on a new line
        fp.write('%s\n' % item)
fp.close()

# Read the whole text.
text = open(path.join(d, 'word_cloud_words.txt')).read()
mask = np.array(Image.open(path.join(d, "img/sk.png")))


# Generate a word cloud image
wc = WordCloud(max_words=max_words,
               background_color='black',
               mask=mask,
               width=900,
               relative_scaling=0.1,
               random_state=1,
               height=900).generate(text)

color_to_words = {
    # words below will be colored with a green single color function
    '#00ff00': pos_words,
    # will be colored with a red single color function
    'red': neg_words
}

# Words that are not in any of the color_to_words values
# will be colored with a grey single color function
default_color = 'black'

# Create a color function with single tone
# grouped_color_func = SimpleGroupedColorFunc(color_to_words, default_color)

# Create a color function with multiple tones
grouped_color_func = GroupedColorFunc(color_to_words, default_color)

# Apply our color function
wc.recolor(color_func=grouped_color_func)

# Plot
plt.imshow(wc, interpolation="bilinear")
plt.axis('off')


plt.show()
