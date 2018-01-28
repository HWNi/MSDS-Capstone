#-*- coding: UTF-8 -*-
import cPickle
import os
import difflib
import re
import string
import unicodedata
import csv


def remove_noise(src):
    src = src.decode('utf-8')

    pattern = re.compile(u'è\·ˉ |È\·ˉ |è\·ˉ|È\·ˉ', re.MULTILINE)
    s = pattern.sub('', src)

    pattern = re.compile(u'@.*|[? ]author.email:.*', re.MULTILINE)
    s = pattern.sub('', s)

    s = s.replace(r'\xi', '')
    s = s.replace(r'\phi', '')
    s = s.replace(r'\delta', '')
    s = s.replace(u'é', 'e')
    s = s.replace(u'ó', 'o')

    pattern = re.compile(u'[àáâãäåæ]|(¨¢)+', re.MULTILINE)
    s = pattern.sub('a', s)

    pattern = re.compile(u'[ÀÁÂÃÄÅÆ]', re.MULTILINE)
    s = pattern.sub('A', s)

    pattern = re.compile(u'[èéêëȩ]|¨\||¨¨|¨e|¨¦', re.MULTILINE)
    s = pattern.sub('e', s)

    pattern = re.compile(u'[ÈÉÊË]', re.MULTILINE)
    s = pattern.sub('E', s)

    pattern = re.compile(u' ı', re.MULTILINE)
    s = pattern.sub('i', s)

    pattern = re.compile(u'[ìíîïı]|¨a|¨ª', re.MULTILINE)
    s = pattern.sub('i', s)

    pattern = re.compile(u'[ÌÍÎÏ]', re.MULTILINE)
    s = pattern.sub('I', s)

    pattern = re.compile(u'[ðđ]', re.MULTILINE)
    s = pattern.sub('d', s)

    pattern = re.compile(u'[ÐĐ]', re.MULTILINE)
    s = pattern.sub('D', s)

    pattern = re.compile(u'[ñ]', re.MULTILINE)
    s = pattern.sub('n', s)

    pattern = re.compile(u'[Ñ]', re.MULTILINE)
    s = pattern.sub('N', s)

    pattern = re.compile(u'[òóôõöø]|¨°|¨®|¨o', re.MULTILINE)
    s = pattern.sub('o', s)

    pattern = re.compile(u'[ÒÓÔÕÖØ]', re.MULTILINE)
    s = pattern.sub('O', s)

    pattern = re.compile(u'[ùúûü]|¨²|¨¹|¨u', re.MULTILINE)
    s = pattern.sub('u', s)

    pattern = re.compile(u'[ÙÚÛÜ]', re.MULTILINE)
    s = pattern.sub('U', s)

    pattern = re.compile(u'[Ýýÿ]', re.MULTILINE)
    s = pattern.sub('y', s)

    pattern = re.compile(u'[Ý]', re.MULTILINE)
    s = pattern.sub('Y', s)

    pattern = re.compile(u'[Þþ]', re.MULTILINE)
    s = pattern.sub('p', s)

    pattern = re.compile(u'[çčć]', re.MULTILINE)
    s = pattern.sub('c', s)

    pattern = re.compile(u'[Ç]', re.MULTILINE)
    s = pattern.sub('C', s)

    pattern = re.compile(u'¨f', re.MULTILINE)
    s = pattern.sub('ef', s)

    pattern = re.compile(u'[łŁ]|¨l', re.MULTILINE)
    s = pattern.sub('l', s)

    pattern = re.compile(u'Ł', re.MULTILINE)
    s = pattern.sub('L', s)

    pattern = re.compile(u'ž', re.MULTILINE)
    s = pattern.sub('z', s)

    pattern = re.compile(u'Ž', re.MULTILINE)
    s = pattern.sub('Z', s)

    pattern = re.compile(u'š', re.MULTILINE)
    s = pattern.sub('s', s)

    pattern = re.compile(u'ß', re.MULTILINE)
    s = pattern.sub('b', s)

    pattern = re.compile(u' ¨\.', re.MULTILINE)
    s = pattern.sub('.', s)

    pattern = re.compile(u' º | ¨ |¨ |° |° | ¨ |¨ | ¨| \?ˉ\? |\?ˉ\? |\?ˉ\?|ˉ\? |ˉ\?| ´ |´ | ´| ˝ |˝ | ˘ | ˜ | ˆ | ‰ |‰ | » |» ', re.MULTILINE)
    s = pattern.sub('', s)

    s = s.replace(u' ³ ', ' ')

    pattern = re.compile(u"[¯´ˉ’‘ˆ°¨¸³·»~«˘'""\\\\]", re.MULTILINE)
    s = pattern.sub('', s)

    pattern = re.compile(u"[  ]", re.MULTILINE)
    s = pattern.sub(' ', s)

    return unicodedata.normalize('NFKD', s).encode('ascii','ignore')

def generate_new_author_names():
    author_fn = 'data/Author_refined_simple.csv'

    if not os.path.isfile(author_fn):
        print "Start preprocessing author names"
        with open("data/author_paper.csv") as author_file:
            f = open(author_fn, 'w')
            for row in csv.reader(author_file, delimiter=","):              
                if len(row) < 5:
                    # the row does not have PMID, AuthorID, LastName, ForeName, and Initials 
                    pass
                else:
                    lastName_cleaned = remove_noise(row[2])
                    row[2] = lastName_cleaned
                    if len(row) > 5:
                        # the row has AffiliationInfo
                        affliation_cleaned = remove_noise(row[5])
                        row[5] = affliation_cleaned
                    f.write(','.join(row) + '\n')

generate_new_author_names()
