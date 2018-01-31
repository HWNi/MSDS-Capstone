import csv
import os
import cPickle
import re
#from custom_setting import *
from difflib import SequenceMatcher
from name import *
from scipy.sparse import lil_matrix

csv.field_size_limit(500 * 1024 * 1024)

# Global
"""
author_file = 'C:\\Users\\nhw10\\Desktop\\Author.csv'
paper_author_file = 'C:\\Users\\nhw10\\Desktop\\PaperAuthor.csv'
serialization_dir = 'C:\\Users\\nhw10\\Desktop\\Serialization\\'
"""
author_file = '/Users/zicong/Desktop/DataScience/Capstone/pubmed_data/Author.csv'
paper_author_file = '/Users/zicong/Desktop/DataScience/Capstone/pubmed_data/PaperAuthor.csv'
serialization_dir = '/Users/zicong/Desktop/DataScience/Capstone/pubmed_data/'
name_statistics_file = 'name_statistics_seal'
author_paper_stat_file = 'author_paper_stat_seal'
name_instance_file = 'name_instance_seal'
id_name_file = 'id_name_seal'


duplicate_author_dict = {}
def load_name_statistic():
    """Generate the statistics of name unit (pair) and author-paper.
       raw_name_statistics keeps statistics of noisy single name unit appeared in author.csv
       name_statistics keeps statistics of single and pairwise name unit appeared in author.csv
       name_statistics_super keeps statistics of single and pairwise name unit appeared in both author.csv and paperauthor.csv
    """

    directory = os.path.dirname(serialization_dir)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if os.path.isfile(serialization_dir + name_statistics_file) and \
            os.path.isfile(serialization_dir + 'super_' + name_statistics_file) and \
            os.path.isfile(serialization_dir + 'raw_' + name_statistics_file) and \
            os.path.isfile(serialization_dir + author_paper_stat_file):
        print "\tSerialization files related to name_statistics exist."
        print "\tReading in the serialization files.\n"
        name_statistics = cPickle.load(
            open(serialization_dir + name_statistics_file, "rb"))
        name_statistics_super = cPickle.load(
            open(serialization_dir + 'super_' + name_statistics_file, "rb"))
        raw_name_statistics = cPickle.load(
            open(serialization_dir + 'raw_' + name_statistics_file, "rb"))
        author_paper_stat = cPickle.load(
            open(serialization_dir + author_paper_stat_file, "rb"))
    else:
        print "\tSerialization files related to name_statistics do not exist."
        name_statistics = dict()
        raw_name_statistics = dict()
        name_statistics_super = dict()
        author_paper_stat = dict()
        print "\tReading in the author.csv file."
        with open(author_file, 'rb') as csv_file:
            author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            # Skip first line
            next(author_reader)
            count = 0
            for row in author_reader:
                count += 1
                if count % 20000 == 0:
                    print "\\tFinish analysing " \
                        + str(count) + " lines of the file."
                author_name = (row[2] + ' ' + row[1]).lower().strip()
                elements = author_name.split()
                for element in elements:
                    if element != '':
                        raw_name_statistics[element] = raw_name_statistics.setdefault(element, 0) + 1
                # Remove noisy characters
                author_name = re.sub('[^a-zA-Z ]', '', author_name)
                elements = author_name.split()
                for element in elements:
                    if element != '':
                        name_statistics[element] = name_statistics.setdefault(element, 0) + 1
                        name_statistics_super[element] = name_statistics.setdefault(element, 0) + 1
                for element1 in elements:
                    for element2 in elements:
                        if element1 != element2:
                            # Keep statistics of name unit pairs:
                            # name_statistics if only for names in author.csv
                            # name_statistics_super is for names in both author.csv and paperauthor.csv
                            name_statistics[element1 + ' ' + element2] = name_statistics.setdefault(element1 + ' ' + element2, 0) + 1
                            name_statistics_super[element1 + ' ' + element2] = name_statistics_super.setdefault(element1 + ' ' + element2, 0) + 1
        print "\tReading in the paperauthor.csv file."
        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(
                csv_file, delimiter=',', quotechar='"')
            # Skip first line
            next(paper_author_reader)
            count = 0
            for row in paper_author_reader:
                count += 1
                if count % 500000 == 0:
                    print "\tFinish analysing " \
                        + str(count) + " lines of the file."
                author_name = (row[3] + ' ' + row[2]).lower().strip()
                author_name = re.sub('[^a-zA-Z ]', '', author_name)
                author_id = int(row[1])
                # Keep the publication size of each author id
                author_paper_stat[author_id] = author_paper_stat.setdefault(author_id, 0) + 1
                elements = author_name.split()
                for element in elements:
                    if element != '':
                        name_statistics_super[element] = name_statistics.setdefault(element, 0) + 1
                for element1 in elements:
                    for element2 in elements:
                        if element1 != element2:
                            name_statistics_super[element1 + ' ' + element2] = name_statistics_super.setdefault(element1 + ' ' + element2, 0) + 1
        print "\tWriting into serialization files related to name_statistics.\n"
        cPickle.dump(
            name_statistics,
            open(serialization_dir + name_statistics_file, "wb"), 2)
        cPickle.dump(
            raw_name_statistics,
            open(serialization_dir + 'raw_' + name_statistics_file, "wb"), 2)
        cPickle.dump(
            name_statistics_super,
            open(serialization_dir + 'super_' + name_statistics_file, "wb"), 2)
        cPickle.dump(
            author_paper_stat,
            open(serialization_dir + author_paper_stat_file, "wb"), 2)
        return (name_statistics, raw_name_statistics, name_statistics_super, author_paper_stat)

def load_author_files(name_statistics,  raw_name_statistics, name_statistics_super, author_paper_stat):
    """Load author info into class: Name and do some initial clearning."""
    directory = os.path.dirname(serialization_dir)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if os.path.isfile(serialization_dir + name_instance_file) and \
            os.path.isfile(serialization_dir + id_name_file):
        print "\tSerialization files related to authors exist."
        print "\tReading in the serialization files.\n"
        name_instance_dict = cPickle.load(
            open(serialization_dir + name_instance_file, "rb"))
        id_name_dict = cPickle.load(
            open(serialization_dir + id_name_file, "rb"))
        name_statistics = cPickle.load(
            open(serialization_dir + name_statistics_file, "rb"))
    else:
        print "\tSerialization files related to authors do not exist."
        name_instance_dict = dict()
        id_name_dict = dict()
        print "\tReading in the author.csv file."
        with open(author_file, 'rb') as csv_file:
            author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            # Skip first line
            next(author_reader)
            count = 0
            for row in author_reader:
                count += 1
                if count % 20000 == 0:
                    print "\tFinish analysing " \
                        + str(count) + " lines of the file."
                author_id = int(row[0])
                author_name = row[2] + ' ' + row[1]

                elements = author_name.split()
                if author_name.upper()[:-1] == author_name[:-1]:
                    new_elements = elements
                else:
                    new_elements = list()
                    for element in elements:
                        if element.lower() in raw_name_statistics:
                            # Split consective initials into different name units if necessary. E.g., ABC Michael -> A B C Michael
                            if len(element) <= 3 and element != elements[-1]:
                                if raw_name_statistics[element.lower()] <= 3:
                                    new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                                elif element.lower() not in asian_units and element.lower() not in asian_last_names and raw_name_statistics[element.lower()] <= 10:
                                    new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                                else:
                                    new_elements.append(element)
                            elif len(element) > 3 and raw_name_statistics[element.lower()] <= 1:
                                if element.lower()[:-1] not in raw_name_statistics or raw_name_statistics[element.lower()[:-1]] <= 1:
                                    new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                                else:
                                    new_elements.append(element)
                            else:
                                new_elements.append(element)
                        else:
                            new_elements.append(element)
                # Additional operation on names with last element 'j' (jr)
                if len(new_elements) >= 3 and new_elements[-1].lower() == 'j':
                    # print new_elements
                    new_elements = new_elements[:-1]
                author = Name(' '.join(new_elements))
                id_name_dict[author_id] = [author.name, row[1]]
                if author.name in name_instance_dict:
                    name_instance_dict[author.name].add_author_id(int(row[0]))
                else:
                    author.add_author_id(int(row[0]))
                    name_instance_dict[author.name] = author

        print '\tStart recovering names'
        # Try breaking name units to see if it exists in the name_instance_dict
        # Similar to the code at the bigining of this function
        with open(author_file, 'rb') as csv_file:
            author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            # Skip first line
            next(author_reader)
            count = 0
            for row in author_reader:
                count += 1
                if count % 20000 == 0:
                    print "\tFinish analysing " \
                        + str(count) + " lines of the file."
                author_id = int(row[0])
                author_name = (row[2] + ' ' + row[1]).strip()
                if author_name == '':
                    continue
                elements = author_name.split()
                new_elements = list()
                if len(elements[0]) > 1 and len(elements[0]) <= 5 and raw_name_statistics[elements[0].lower()] <= 20:
                    new_elements.append(re.sub(r"(?<=\w)([a-zA-Z])", r" \1", elements[0]))
                    for element in elements[1:]:
                        new_elements.append(element)
                    author = Name(' '.join(new_elements))
                    if author.name in name_instance_dict:
                        # print author_name + ' --> ' + author.name
                        name_instance_dict[id_name_dict[author_id][0]].del_author_id(int(row[0]))
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
            count += 1
            if count % 20000 == 0:
                    print "\tFinish analysing " \
                        + str(count) + " lines of the file for removing noisy last names."
            if len(name_instance.author_ids) == 1 and not name_instance.is_asian and not name_instance.has_dash:
                elements = name_instance.name.split()
                if len(elements) >= 2:
                    if (elements[-2] + ' ' + elements[-1]) in name_statistics_super and name_statistics_super[(elements[-2] + ' ' + elements[-1])] >= 2:
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
            count += 1
            if count % 20000 == 0:
                    print "\tFinish analysing " \
                        + str(count) + " lines of the file."
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
                            if element not in name_statistics or min(name_statistics[element[i:]], name_statistics[element[:i]]) > name_statistics[element] and\
                                    element[:i] not in asian_units and element[i:] not in asian_units and\
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

        name_statistics = dict()
        for name_instance in list(name_instance_dict.itervalues()):
            elements = name_instance.name.split()
            for element in elements:
                name_statistics[element] = name_statistics.setdefault(element, 0) + len(name_instance.author_ids)
            for element1 in elements:
                    for element2 in elements:
                        if element1 != element2:
                            name_statistics[element1 + ' ' + element2] = name_statistics.setdefault(element1 + ' ' + element2, 0) + len(name_instance.author_ids)
                            # name_statistics[element2 + ' ' + element1] = name_statistics.setdefault(element2 + ' ' + element1, 0) + len(name_instance.author_ids)

        print "\tWriting into serialization files related to name_statistics.\n"
        cPickle.dump(
            name_statistics,
            open(serialization_dir + name_statistics_file, "wb"), 2)
        print "\tWriting into serialization files related to authors.\n"
        cPickle.dump(
            name_instance_dict,
            open(serialization_dir + name_instance_file, "wb"), 2)
        cPickle.dump(
            id_name_dict,
            open(serialization_dir + id_name_file, "wb"), 2)

    return (name_instance_dict, id_name_dict, name_statistics)


def add_similar_ids_under_name(name_instance_dict, id_name_dict):
    """Find similar id for each name in name_instance_dict."""
    print "\tBuilding virtual names."
    virtual_name_set = set()
    for (author_name, name_instance) in name_instance_dict.iteritems():
        alternatives = name_instance.get_alternatives()
        for alternative in alternatives:
            if alternative not in name_instance_dict:
                virtual_name_set.add(alternative)

    for virtual_author_name in virtual_name_set:
        new_name_instance = Name(virtual_author_name)
        name_instance_dict[virtual_author_name] = new_name_instance

    print "\tAdding similar author ids into each name instance."
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            alternatives = name_instance.alternatives
            for alternative in alternatives:
                # Add author_ids into the similar_author_ids
                # of the name's alternative.
                for id in name_instance.author_ids:
                    name_instance_dict[alternative].add_similar_author_id(id)
                # Add alternative's author_ids into the similar_author_ids
                # of the current name.
                for id in name_instance_dict[alternative].author_ids:
                    name_instance_dict[author_name].add_similar_author_id(id)

    reduced_name_pool = {}
    length = len(name_instance_dict) - len(virtual_name_set)
    print "\tBuilding reduced_name dict."
    count = 0
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish computing " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names' hash value."
            elements = sorted(author_name.split())
            reduced_name = ''.join(elements)
            reduced_name_pool.setdefault(reduced_name, set()).add(author_name)

    print "\tAdding similar ids for the same reduced_names."
    count = 0
    for (author_name1, name_instance1) in name_instance_dict.iteritems():
        if author_name1 not in virtual_name_set:
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish comparing " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names."

            # name = "b a" -> split -> ['b', 'a'] -> sorted -> ['a', 'b']
            elements = sorted(author_name1.split())
            reduced_name = ''.join(elements)
            pool = reduced_name_pool[reduced_name]
            for author_name2 in pool:
                name_instance2 = name_instance_dict[author_name2]
                for id in name_instance1.author_ids:
                    name_instance2.add_similar_author_id(id)
                for id in name_instance2.author_ids:
                    name_instance1.add_similar_author_id(id)

    sorted_name_pool = {}
    length = len(name_instance_dict) - len(virtual_name_set)
    print "\tBuilding sorted name dict."
    count = 0
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish computing " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names' hash value."
            elements = author_name.split()
            sorted_name = ''.join(elements)
            sorted_name_pool.setdefault(sorted_name, set()).add(author_name)

    print "\tAdding similar ids for the same sorted_names."
    count = 0
    for (author_name1, name_instance1) in name_instance_dict.iteritems():
        if author_name1 not in virtual_name_set:
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish comparing " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names."
            elements = author_name1.split()
            sorted_name = ''.join(elements)
            pool = sorted_name_pool[sorted_name]
            for author_name2 in pool:
                if author_name1 < author_name2:
                    name_instance2 = name_instance_dict[author_name2]
                    for id in name_instance1.author_ids:
                        name_instance2.add_similar_author_id(id)
                    for id in name_instance2.author_ids:
                        name_instance1.add_similar_author_id(id)

    name_unit_pool = {}
    length = len(name_instance_dict) - len(virtual_name_set)
    print "\tBuilding name unit dict."
    count = 0
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            if len(author_name) < 10:
                continue
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish computing " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names' hash value."
            elements = name_instance.name.split()
            for element in elements:
                name_unit_pool.setdefault(element, set()).add(author_name)

    name_finger_dict = {}
    for (author_name, name_instance) in name_instance_dict.iteritems():
        name_finger_dict[author_name] = ''.join(sorted(author_name.split()))

    print "\tAdding similar ids for the same name units."
    count = 0
    for (author_name1, name_instance1) in name_instance_dict.iteritems():
        if author_name1 not in virtual_name_set:
            if len(author_name1) < 10:
                continue
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish comparing " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names."
            elements = name_instance1.name.split()
            for element in elements:
                pool = name_unit_pool[element]
                for author_name2 in pool:
                    if author_name1 < author_name2:
                        if author_name1.find(author_name2) >= 0 or author_name2.find(author_name1) >= 0:
                            if abs(len(author_name1) - len(author_name2)) <= 3 and len(author_name1) >= 8 and len(author_name2) >= 8 or\
                                    len(author_name1) > 15 and len(author_name2) > 15:
                                name_instance2 = name_instance_dict[author_name2]
                                for id in name_instance1.author_ids:
                                    name_instance2.add_similar_author_id(id)
                                for id in name_instance2.author_ids:
                                    name_instance1.add_similar_author_id(id)
                        # print author_name2 + ' ' + author_name1

    # hash_dict = {}
    # hash_pool = {}
    # length = len(name_instance_dict) - len(virtual_name_set)
    # print "\tBuilding hashes."
    # count = 0
    # for (author_name, name_instance) in name_instance_dict.iteritems():
    #     if author_name not in virtual_name_set:
    #         count += 1
    #         if count % 30000 == 0:
    #             print "\t\tFinish computing " + str(float(count)/length*100)\
    #                 + "% (" + str(count) + "/" + str(length) + ") names' hash value."
    #         tokens = list()
    #         reduced_name = author_name.replace(' ', '')
    #         for i in xrange(len(reduced_name) - 2):
    #             tokens.append(reduced_name[i:i+3])
    #         hash_dict[author_name] = Simhash(tokens, 20)
    #         hash_pool.setdefault(hash_dict[author_name].hash, set()).add(author_name)

    # print "\tComparing hashes."
    # count = 0
    # for (author_name1, name_instance1) in name_instance_dict.iteritems():
    #     if author_name1 not in virtual_name_set:
    #         count += 1
    #         if count % 30000 == 0:
    #             print "\t\tFinish comparing " + str(float(count)/length*100)\
    #                 + "% (" + str(count) + "/" + str(length) + ") names."
    #         pool = hash_pool[hash_dict[author_name1].hash]
    #         for author_name2 in pool:
    #             if author_name1 <= author_name2:
    #                 name_instance2 = name_instance_dict[author_name2]
    #                 for id in name_instance1.author_ids:
    #                     name_instance2.add_similar_author_id(id)
    #                 for id in name_instance2.author_ids:
    #                     name_instance1.add_similar_author_id(id)

    length = len(name_instance_dict) - len(virtual_name_set)
    init_full_dict = {}
    full_init_dict = {}
    initlen_full_dict = {}
    count = 0
    print "\tBuilding name initials mapping."
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            initials = ''
            # elements = author_name.split(' ')
            # for element in elements:
            #     if len(element) > 1:
            #         initials += element[0]
            if name_instance.first_name != '':
                initials += name_instance.first_name[0]
            if name_instance.middle_name != '':
                initials += name_instance.middle_name[0]
            if name_instance.last_name != '':
                initials += name_instance.last_name[0]
            init_full_dict.setdefault(initials, set()).add(author_name)
            full_init_dict[author_name] = initials
            initlen_full_dict.setdefault((initials, len(author_name)), set()).add(author_name)

    print "\tStart noisy last name comparison:"
    count = 0
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            pool = init_full_dict[full_init_dict[author_name]]
            for candidate in pool:
                if author_name[:-1] == candidate:
                # if SequenceMatcher(None, author_name, candidate).ratio() >= 0.9:
                    name_instance_candidate = name_instance_dict[candidate]
                    for id in name_instance.author_ids:
                        name_instance_candidate.add_similar_author_id(id)
                    for id in name_instance_candidate.author_ids:
                        name_instance.add_similar_author_id(id)
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish matching " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names containing noisy last character with the whole database."
    print "\tStart question marks or non askii name comparison:"
    count = 0
    for (author_id, author_name_list) in id_name_dict.iteritems():
        if not all(ord(char) < 128 for char in author_name_list[1]) or author_name_list[1].find('?') >= 0:
            name_instance_dict[author_name_list[0]].bad_name_flag = True
            pool = init_full_dict[full_init_dict[author_name_list[0]]]
            for candidate in pool:
                if SequenceMatcher(None, author_name_list[0], candidate).ratio() >= 0.9 or SequenceMatcher(None, author_name_list[1], candidate).ratio() >= 0.9:
                    name_instance_candidate = name_instance_dict[candidate]
                    for id in name_instance_dict[author_name_list[0]].author_ids:
                        name_instance_candidate.add_similar_author_id(id)
                    for id in name_instance_candidate.author_ids:
                        name_instance_dict[author_name_list[0]].add_similar_author_id(id)
            count += 1
            if count % 300 == 0:
                print "\t\tFinish matching " + str(count)\
                    + " names containing question mark or non askii characters with the whole database."
    print "\t\tIn total there exist " + str(count) + " names containing question marks or non askii characters."

    print "\tStart arbitrary name comparison:"
    count = 0
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            name_length = len(author_name)
            for area in range(-3, 4):
                if name_length + area > 0 and (full_init_dict[author_name], name_length + area) in initlen_full_dict:
                    pool = initlen_full_dict[(full_init_dict[author_name], name_length + area)]
                    for candidate in pool:
                        if SequenceMatcher(None, author_name, candidate).ratio() >= 0.94:
                            name_instance_candidate = name_instance_dict[candidate]
                            for id in name_instance_dict[author_name].author_ids:
                                name_instance_candidate.add_similar_author_id(id)
                            for id in name_instance_candidate.author_ids:
                                name_instance_dict[author_name].add_similar_author_id(id)
            count += 1
            if count % 30000 == 0:
                print "\t\tFinish matching " + str(float(count)/length*100)\
                    + "% (" + str(count) + "/" + str(length) + ") names containing noisy last character with the whole database."
    print

    print "\tStart nicknames comparison:"
    count = 0
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if name_instance.first_name in nickname_dict:
            for nickname in nickname_dict[name_instance.first_name]:
                s = ' '.join([nickname, name_instance.middle_name, name_instance.last_name]).strip()
                new_name = ' '.join(s.split())
                if new_name in name_instance_dict:
                    for id in name_instance_dict[new_name].author_ids:
                        name_instance.add_similar_author_id(id)
                    for id in name_instance.author_ids:
                        name_instance_dict[new_name].add_similar_author_id(id)
                    count += 1
                    if count % 2000 == 0:
                        print "\t\tFinish matching " + str(count)\
                            + " pairs of nicknames."


def create_potential_duplicate_groups(name_instance_dict, author_paper_stat):
    """Create potential duplicate groups for local clustering algorithm to analyse.

    Parameters:
        name_instance_dict:
            A dictionary with key: author's name string and value:
            name instance. Note that the author's name is clean after
            initialization of the Name class.

    Returns:
        A set containing lots of tuples describing the potential duplicate group.
    """
    # groups = set()
    # for (author_name, name_instance) in name_instance_dict.iteritems():
    #     groups.add(tuple(sorted(name_instance.author_ids.union(name_instance.similar_author_ids))))
    # return groups

    groups = set()
    for (author_name, name_instance) in name_instance_dict.iteritems():
        group = name_instance.author_ids.union(name_instance.similar_author_ids)
        for id1 in group:
            if id1 in author_paper_stat:
                for id2 in group:
                    if id2 in author_paper_stat:
                        if id1 < id2:
                            groups.add(tuple([id1, id2]))
    return groups