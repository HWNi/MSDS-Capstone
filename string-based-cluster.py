import csv
import os
import cPickle
import re
#from custom_setting import *
from difflib import SequenceMatcher
from name import *
from scipy.sparse import lil_matrix


# Global
author_file = 'C:\\Users\\nhw10\\Desktop\\Author.csv'
paper_author_file = 'C:\\Users\\nhw10\\Desktop\\PaperAuthor.csv'
serialization_dir = 'C:\\Users\\nhw10\\Desktop\\Serialization\\'
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



