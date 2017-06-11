"""
100 ids, urls of shape 'https://geopulse-events.s3-us-west-1.amazonaws.com/<ID>/article_text.txt'

1.
take all the words and add to 'words' tables with schema:
 string:word
 string:word_type (word, entity, number, stop_word)
 integer:event_id (article)
 integer:word_position (word count in article)

word - general word,
entity - starts with capital
number - number
stop word - from list below

 2.
 2 queries -
 A. most common non-stop words
 B. Most common entity across articles - which entity was in the most articles


"""

import os
import time
import urllib
import urlparse
from pandas import DataFrame
from task import DataBase

# "Constants"
main_url = r'https://geopulse-events.s3-us-west-1.amazonaws.com'
suffix = r'article_text.txt'
local_dir = r'D:\Various\Geopulse\articles'

STOP_WORDS = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]

# Connect to DB
db = DataBase(dbname='temp', user='postgres', password='blahblah15')
# db.cursor.execute("CREATE TYPE word_type AS ENUM ('word', 'entity', 'number', 'stop_word');")  # TODO: add a validation here that 'word_type' exists, like in table below
if 'word_type' not in db.AVAILABLE_COLUMN_TYPES:
    db.AVAILABLE_COLUMN_TYPES.append('word_type')
if 'word_type' not in db.COLUMN_TYPE_INSTANCE_MAPPING:
    db.COLUMN_TYPE_INSTANCE_MAPPING.update({'word_type': str})
if 'USER-DEFINED' not in db.COLUMN_TYPE_INSTANCE_MAPPING:
    db.COLUMN_TYPE_INSTANCE_MAPPING.update({'USER-DEFINED': str})


# Query existing tables
db.cursor.execute("SELECT table_name from INFORMATION_SCHEMA.Tables WHERE table_schema = 'public'")
table_names = db.cursor.fetchall()
table_names = [tn[0] for tn in table_names]

# create new table if needed
if 'words' not in table_names:
    db.create_table('words', word='text', word_type='word_type', event_id='integer', word_position='integer')  # TODO: make 'word' primary key?

# get article ids
ids_path = 'ids.txt'
f = open(ids_path)
ids_txt = f.read()
f.close()

# cleanup article ids - remove spaces, commas, etc
ids = [i.strip(', ') for i in ids_txt.split('\n')]

# download all articles locally
dirlist = os.listdir(local_dir)
if len(dirlist) < len(ids):
    for ix, i in enumerate(ids):
        print "downloading {} {}/{}".format(i, ix, len(ids))
        if i + '.txt' in dirlist:
            print "skipping {} {}/{} - already exists".format(i, ix, len(ids))
            continue
        link = urlparse.urljoin(main_url, i + "/" + suffix)
        fr = urllib.urlopen(link)
        myfile = fr.read()
        new_fname = os.path.join(local_dir, i + '.txt')
        fw = open(new_fname, 'w')
        fw.write(myfile)
        fw.close()
        fr.close()
        print "saved {} {}/{}".format(i, ix, len(ids))


# define helper functions
def get_word_type(word):
    if word in STOP_WORDS:
        return 'stop_word'
    if word.isdigit():
        return 'number'
    if word[0].isupper():
        return 'entity'
    return 'word'


def get_words_from_file(fname):
    """
    Reads fname, returns a list of tuples - word, its type, position and article id
    :param fname: should be the local dir \ id.txt
    :return:
    """
    # get event id
    event_id = os.path.split(fname)[-1][:-4]

    # get all words
    f = open(fname, 'r')
    txt = f.read()  # TODO: do not read headers?
    f.close()

    # split and strip words
    word_list = txt.split()
    word_list_clean = [word for word in word_list if word not in ['|', '.', '-']]  # ignore single special characters
    word_type_list = []
    word_list_stripped = []
    for word in word_list_clean:
        word_stripped = word.strip('.|,-:')  # remove non-alphabetic characters
        if not len(word_stripped):
            continue
        word_list_stripped.append(word_stripped)
        word_type_list.append(get_word_type(word_stripped))

    return zip(word_list_stripped, word_type_list, range(len(word_list_stripped)), [int(event_id)] * len(word_list_stripped))

# minor test
assert get_word_type('Apple') == 'entity', "problem with 'entity'"
assert get_word_type('12') == 'number', "problem with 'number'"
assert get_word_type('at') == 'stop_word', "problem with 'stop_word'"
assert get_word_type('blah') == 'word', "problem with 'word'"

# fname = r'D:\Various\Geopulse\articles\26951.txt'
# res = get_words_from_file(fname)

# Go over all local articles and analyze
fill_table = False
if fill_table:
    for ix, article in enumerate(dirlist):
        print "Started working on article {}, {}/{}".format(article, ix, len(dirlist))
        t_start_article = time.time()
        word_details = get_words_from_file(os.path.join(local_dir, article))
        for wd in word_details:
            word, word_type, word_position, event_id = wd
            db.add_row('words', word=word, word_type=word_type, event_id=event_id, word_position=word_position)
        print 'finished going over article {}, {}/{}. took {} secs'.format(article, ix, len(dirlist), time.time() - t_start_article)


"""
Noted issues in DB:
time is identified as a word - 1:04pm
words with slashed, hyphens are not treated correctly - Brief-peach \ 2005/2010
"""

# ========================== QUERIES ==============================================

# 1. most common non-stop words
non_stop_words = db.query_table('words', "word_type <> 'stop_word'")
count1 = DataFrame(non_stop_words.groupby('word').size().rename('counts')).sort_values('counts', ascending=False)
top_10 = count1.iloc[:10]

# TODO: query_table does not support distinct, count, etc.

# which entity was in the most articles
command_string = "SELECT DISTINCT word, event_id FROM words WHERE word_type = \'entity\';"
db.cursor.execute(command_string)
count2 = db.cursor.fetchall()

count_dict = {}
for entity, article in count2:
    if entity in count_dict:
        count_dict[entity] |= set([article])
    else:
        count_dict[entity] = set([article])

# count
count_result = [(len(a), e) for e, a in count_dict.items()]
count_result.sort(reverse=True)
top_10_2 = count_result[:10]

a=5


