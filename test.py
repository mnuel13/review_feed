import json

with open('reviews_sk.json', 'r') as reviews:
    a = json.load(reviews)
    print(a[list(a.keys())[9]][0])
    reviews.close()


from time import sleep
from tqdm import tqdm
import random

# Default smoothing of 0.3 - irregular updates and medium-useful ETA
for i in tqdm(range(100)):
    sleep(random.randint(0,5)/10)

# Immediate updates - not useful for irregular updates
for i in tqdm(range(100), smoothing=1):
    sleep(random.randint(0,5)/10)

# Global smoothing - most useful ETA in this scenario
for i in tqdm(range(100), smoothing=0):
    sleep(random.randint(0,5)/10)