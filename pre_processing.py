#-*- coding: UTF-8 -*-
import csv
import cPickle
import os
import re
import unicodedata

from custom_setting import *
from name import *


def remove_noise_simple(src_name):
    """Solve encoding problem in the raw data."""
    name = src_name.decode('utf-8')
    return unicodedata.normalize('NFKD', name).encode('ascii','ignore')


def remove_noise(src):
    """Substitue non-English characters with English characters."""
    src = src.decode('utf-8')

    pattern = re.compile(u'è\·ˉ |È\·ˉ |è\·ˉ|È\·ˉ', re.MULTILINE)
    s = pattern.sub('', src)

    pattern = re.compile(u'@.*|[? ]author.email:.*', re.MULTILINE)
    s = pattern.sub('', s)

    s = s.replace(r'\xi', '')
    s = s.replace(r'\phi', '')
    s = s.replace(r'\delta', '')
    s = s.replace(u'é', 'e')
    s = s.replace(u'ó', 'o')

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
    """Load and extract author names."""
    author_fn = 'data/Author_refined_simple.csv'
    paper_author_fn = 'data/PaperAuthor_refined_simple.csv'
    if not os.path.isfile(author_fn):
        done = {}
        print "Generating Author_refined, simple non-ascii to ascii"
        with open("data/Author.csv") as author_file:
            f = open(author_fn, 'w')
            for line in author_file:
                tokens = line.split(',')
                if len(tokens) > 1:
                    if tokens[1] in done:
                        tokens[1] = done[tokens[1]]
                    else:
                        clean = remove_noise(tokens[1])
                        done[tokens[1]] = clean
                        tokens[1] = clean
                    f.write(','.join(tokens))
                else:
                    f.write(line)
    if not os.path.isfile(paper_author_fn):
        done = {}
        print "Generating PaperAuthor_refined, simple non-ascii to ascii"
        with open("data/PaperAuthor.csv") as pa_file:
            f = open(paper_author_fn, 'w')
            for line in pa_file:
                tokens = line.split(',')
                if len(tokens) > 2:
                    if tokens[2] in done:
                        tokens[2] = done[tokens[2]]
                    else:
                        clean = remove_noise(tokens[2])
                        done[tokens[2]] = clean
                        tokens[2] = clean
                    f.write(','.join(tokens))
                else:
                    f.write(line)


def cal_name_statistics(name_statistics, input_file, name_index):
    """Load author name statistics."""
    with open(input_file, 'r') as csv_file:
        author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        next(author_reader)
        for row in author_reader:
            # author.csv: 1, paper_author.csv: 2
            author_name = row[name_index]
            author_name = author_name.lower().strip()
            author_name = re.sub('[^a-zA-Z ]', '', author_name)
            elements = author_name.split()
            for element in elements:
                if element != '':
                    name_statistics[element] = name_statistics.setdefault(element, 0) + 1
            for element1 in elements:
                for element2 in elements:
                    if element1 != element2:
                        name_statistics[element1 + ' ' + element2] = \
                            name_statistics.setdefault(element1 + ' ' + element2, 0) + 1
    return name_statistics


def generate_name_instance(input_file, id_index, name_index, name_statistics):
    """Calculate a dictionary to store all related name instances."""
    name_instance_dict = dict()
    id_name_dict = dict()
    with open(input_file, 'rb') as csv_file:
        author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        next(author_reader)
        for row in author_reader:
            author_id = int(row[id_index])
            author_name = row[name_index]
            elements = author_name.split()

            if author_name.upper()[:-1] == author_name[:-1]:
                new_elements = elements
            else:
                new_elements = list()
                for element in elements:
                    if element.lower() in name_statistics:
                        # Split consective initials into different name units if necessary. E.g., ABC Michael -> A B C Michael
                        if len(element) <= 3 and element != elements[-1]:
                            if name_statistics[element.lower()] <= 3:
                                new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                            elif element.lower() not in asian_units \
                                    and element.lower() not in asian_last_names \
                                    and name_statistics[element.lower()] <= 10:
                                new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                            else:
                                new_elements.append(element)
                        elif len(element) > 3 and name_statistics[element.lower()] <= 1:
                            if element.lower()[:-1] not in name_statistics \
                                    or name_statistics[element.lower()[:-1]] <= 1:
                                new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                            else:
                                new_elements.append(element)
                        else:
                            new_elements.append(element)
                    else:
                        new_elements.append(element)

            # Additional operation on names with last element 'j' (jr)
            if len(new_elements) >= 3 and new_elements[-1].lower() == 'j':
                new_elements = new_elements[:-1]
            author = Name(' '.join(new_elements))
            id_name_dict[author_id] = [author.name, row[1]]
            if author.name in name_instance_dict:
                name_instance_dict[author.name].add_author_id(int(row[0]))
            else:
                author.add_author_id(int(row[0]))
                name_instance_dict[author.name] = author

    # Try removing last name noises like Lin Zhangt -> Lin Zhang
    for name in list(name_instance_dict.iterkeys()):
        if name not in name_instance_dict:
            continue
        name_instance = name_instance_dict[name]
        if len(name_instance.author_ids) == 1 and not name_instance.is_asian and not name_instance.has_dash:
            elements = name_instance.name.split()
            if len(elements) >= 2:
                if (elements[-2] + ' ' + elements[-1]) in name_statistics and name_statistics[(elements[-2] + ' ' + elements[-1])] >= 2:
                    continue
            i = len(name) / 3
            flag = False
            for j in range(1, i):
                elements = name[:-j].split()
                if len(elements) < 2:
                    break
                if len(elements) <= 4:
                    pool = itertools.permutations(elements)
                else:
                    pool = [elements]
                for permutation in pool:
                    candi = ' '.join(permutation)
                    if candi in name_instance_dict:
                        if len(candi) <= 10 or len(name[:-j].split()[-1]) == 1:
                            continue
                        if len(name_instance_dict[candi].author_ids) > len(name_instance.author_ids):
                            for id in name_instance.author_ids:
                                name_instance_dict[candi].add_author_id(id)
                                id_name_dict[id][0] = candi
                            alternatives = name_instance_dict[name].get_alternatives()
                            for alternative in alternatives:
                                name_instance_dict[candi].add_alternative(alternative)
                            del name_instance_dict[name]
                        elif len(name_instance_dict[candi].author_ids) < len(name_instance.author_ids):
                            for id in set(name_instance_dict[candi].author_ids):
                                name_instance.add_author_id(id)
                                id_name_dict[id][0] = name_instance.name
                            alternatives = name_instance_dict[candi].get_alternatives()
                            for alternative in alternatives:
                                name_instance_dict[name].add_alternative(alternative)
                            del name_instance_dict[candi]
                        else:
                            score_A = 0
                            elements = name.split()
                            for k in xrange(len(elements) - 1):
                                if (elements[k] + ' ' + elements[k + 1]) in name_statistics:
                                    score_A += name_statistics[elements[k] + ' ' + elements[k + 1]]
                            if len(elements) == 1:
                                score_A = 0
                            else:
                                score_A /= len(elements) - 1.0
                            score_B = 0
                            elements = candi.split()
                            for k in xrange(len(elements) - 1):
                                if (elements[k] + ' ' + elements[k + 1]) in name_statistics:
                                    score_B += name_statistics[elements[k] + ' ' + elements[k + 1]]
                            if len(elements) == 1:
                                score_B = 0
                            else:
                                score_B /= len(elements) - 1.0
                            if score_A == score_B:
                                score_A = 0
                                score_B = 0
                                if name_instance.last_name in name_statistics:
                                    score_A = name_statistics[name_instance.last_name]
                                if name_instance_dict[candi].last_name in name_statistics:
                                    score_B = name_statistics[name_instance_dict[candi].last_name]
                            if score_A <= score_B:
                                for id in name_instance.author_ids:
                                    name_instance_dict[candi].add_author_id(id)
                                    id_name_dict[id][0] = candi
                                alternatives = name_instance_dict[name].get_alternatives()
                                for alternative in alternatives:
                                    name_instance_dict[candi].add_alternative(alternative)
                                del name_instance_dict[name]
                            else:
                                for id in name_instance_dict[candi].author_ids:
                                    name_instance.add_author_id(id)
                                    id_name_dict[id][0] = name_instance.name
                                alternatives = name_instance_dict[candi].get_alternatives()
                                for alternative in alternatives:
                                    name_instance_dict[name].add_alternative(alternative)
                                del name_instance_dict[candi]
                        flag = True
                        break
                if flag is True:
                    break

    # Split long name unit to two consective short name units. E.g., michaeljordan -> michael jordan
    for name_instance in list(name_instance_dict.itervalues()):
        if len(name_instance.name) < 10:
            continue
        new_elements = list()
        change_flag = False
        elements = name_instance.name.split()
        for element in elements:
            if len(element) > 10:
                new_elements.append(element)
                if element in name_statistics:
                    if name_statistics[element] >= 2:
                        continue
                for i in range(4, len(element) - 4):
                    if element[:i] in name_statistics and element[i:] in name_statistics:
                        if element not in name_statistics or min(name_statistics[element[i:]],
                                                                 name_statistics[element[:i]]) > \
                                name_statistics[element] and \
                                element[:i] not in asian_units and element[i:] not in asian_units and \
                                (element[:i] + ' ' + element[i:]) in name_statistics:
                            new_elements.pop()
                            new_elements.append(element[:i])
                            new_elements.append(element[i:])
                            change_flag = True
                            break
            else:
                new_elements.append(element)
        if change_flag is True:
            author = Name(' '.join(new_elements))
            if author.name != name_instance.name:
                print '\t\tSplit ' + name_instance.name + ' --> ' + author.name
            for id in name_instance.author_ids:
                author.add_author_id(id)
                id_name_dict[id][0] = author.name
            name_instance_dict[author.name] = author

    return (name_instance_dict, id_name_dict)