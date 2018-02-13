#-*- coding: UTF-8 -*-
import csv
import os
import cPickle
import re
from custom_setting import *
from difflib import SequenceMatcher
from name import *
from scipy.sparse import lil_matrix

duplicate_author_dict = {}

class Metapaths(object):
    """Keeping metapaths features for computing similarity between author id pairs."""

    # def __init__(self, AP, APV, APW, AO, AY, APA, APVPA, APAPA, APAPV):
    #     #AP: author-paper
    #     #APV: author-venue
    #     #APW: author-paper-titleword
    #     #AO: author-orgnization
    #     #AY: author-year
    #     #APA: author-paper-author
    #     #APVPA: author-venue-author
    #     #APAPA: author-paper-author-paper-author
    #     #APAPV: author-paper-author-paper-venue
    #     self.AP = AP
    #     self.APV = APV
    #     self.APW = APW
    #     self.AO = AO
    #     self.AY = AY
    #     self.APA = APA
    #     self.APVPA = APVPA
    #     self.APAPA = APAPA
    #     self.APAPV = APAPV


    def __init__(self, AP, APA, APAPA):
        #AP: author-paper
        #APV: author-venue
        #APW: author-paper-titleword
        #AO: author-orgnization
        #AY: author-year
        #APA: author-paper-author
        #APVPA: author-paper-venue-paper-author
        #APAPA: author-paper-author-paper-author
        #APAPV: author-paper-author-paper-venue
        self.AP = AP
        self.APA = APA
        self.APAPA = APAPA


def load_files():
    """
    Read in files from the folder "data" if no serialization files exist in folder serialization_dir.
    """
    # (name_statistics, raw_name_statistics, name_statistics_super, author_paper_stat) = \
    #     load_name_statistic()
    # (name_instance_dict, id_name_dict, name_statistics) = \
    #     load_author_files(name_statistics, raw_name_statistics, name_statistics_super, author_paper_stat)
    # (author_paper_matrix, all_author_paper_matrix, coauthor_matrix, coauthor_2hop_matrix, name_instance_dict, id_name_dict) = \
    #     load_coauthor_files(name_instance_dict, id_name_dict, author_paper_stat)
    # (covenue_matrix, author_venue_matrix) = load_covenue_files(id_name_dict, author_paper_matrix, all_author_paper_matrix)
    # author_word_matrix = load_author_word_files(id_name_dict, author_paper_matrix)
    # author_org_matrix = load_author_affili_matrix_files()
    # author_year_matrix = load_author_year_matrix_files()
    # APAPC = coauthor_matrix * author_venue_matrix
    # metapaths = Metapaths(author_paper_matrix, author_venue_matrix, author_word_matrix, author_org_matrix, author_year_matrix, coauthor_matrix, covenue_matrix, coauthor_2hop_matrix, APAPC)
    # return (name_instance_dict, id_name_dict, name_statistics, author_paper_stat, metapaths)

    (name_statistics, raw_name_statistics, name_statistics_super, author_paper_stat) = \
        load_name_statistic()
    (name_instance_dict, id_name_dict, name_statistics) = \
        load_author_files(name_statistics, raw_name_statistics, name_statistics_super, author_paper_stat)
    (author_paper_matrix, all_author_paper_matrix, coauthor_matrix, coauthor_2hop_matrix, name_instance_dict, id_name_dict) = \
        load_coauthor_files(name_instance_dict, id_name_dict, author_paper_stat)
    metapaths = Metapaths(author_paper_matrix, coauthor_matrix, coauthor_2hop_matrix)
    return (name_instance_dict, id_name_dict, name_statistics, author_paper_stat, metapaths)


def load_name_statistic():
    """
    Generate the statistics of name unit (pair) and author-paper.
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
        print "\tReading in the serialization files."
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
                    print "\tFinish analysing " + str(count) + " lines of the file."
                # Pub: author_id,surname,given_name,email,affiliation,AffliationId
                author_name = row[2] + ' ' + row[1]
                author_name = author_name.lower().strip()
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
                            name_statistics[element1 + ' ' + element2] = \
                                name_statistics.setdefault(element1 + ' ' + element2, 0) + 1
                            name_statistics_super[element1 + ' ' + element2] = \
                                name_statistics_super.setdefault(element1 + ' ' + element2, 0) + 1
        print "\tReading in the paperauthor.csv file."
        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            # Skip first line
            next(paper_author_reader)
            count = 0
            for row in paper_author_reader:
                count += 1
                if count % 500000 == 0:
                    print "\tFinish analysing " + str(count) + " lines of the file."
                # Pub: pmid,author_id,surname,given_name
                author_name = row[3] + ' ' + row[2]
                author_name = author_name.lower().strip()
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
                            name_statistics_super[element1 + ' ' + element2] = \
                                name_statistics_super.setdefault(element1 + ' ' + element2, 0) + 1
        print "\tWriting into serialization files related to name_statistics."
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


def load_author_files(name_statistics, raw_name_statistics, name_statistics_super, author_paper_stat):
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
                    print "\tFinish analysing " + str(count) + " lines of the file."
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
                                elif element.lower() not in asian_units \
                                        and element.lower() not in asian_last_names \
                                        and raw_name_statistics[element.lower()] <= 10:
                                    new_elements.append(re.sub(r"(?<=\w)([A-Z])", r" \1", element))
                                else:
                                    new_elements.append(element)
                            elif len(element) > 3 and raw_name_statistics[element.lower()] <= 1:
                                if element.lower()[:-1] not in raw_name_statistics \
                                        or raw_name_statistics[element.lower()[:-1]] <= 1:
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
        # Similar to the code at the beginning of this function
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
                author_name = author_name.strip()
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


def load_coauthor_files(name_instance_dict, id_name_dict, author_paper_stat):
    """Load coauthor relationship."""
    if os.path.isfile(serialization_dir + coauthor_matrix_file) and \
            os.path.isfile(serialization_dir + '2hop_' + coauthor_matrix_file) and \
            os.path.isfile(serialization_dir + author_paper_matrix_file) and \
            os.path.isfile(serialization_dir + 'all_' + author_paper_matrix_file) and \
            os.path.isfile(serialization_dir + 'complete_' + name_instance_file) and \
            os.path.isfile(serialization_dir + 'complete_' + id_name_file):
        print "\tSerialization files related to coauthors exist."
        print "\tReading in the serialization files.\n"
        coauthor_matrix = cPickle.load(
            open(serialization_dir + coauthor_matrix_file, "rb"))
        coauthor_2hop_matrix = cPickle.load(
            open(serialization_dir + '2hop_' + coauthor_matrix_file, "rb"))
        author_paper_matrix = cPickle.load(
            open(serialization_dir + author_paper_matrix_file, "rb"))
        all_author_paper_matrix = cPickle.load(
            open(serialization_dir + 'all_' + author_paper_matrix_file, "rb"))
        name_instance_dict = cPickle.load(
            open(serialization_dir + 'complete_' + name_instance_file, "rb"))
        id_name_dict = cPickle.load(
            open(serialization_dir + 'complete_' + id_name_file, "rb"))
    else:
        #Load confident author duplicates generated by model0.
        if os.path.isfile(duplicate_authors_file):
            print "\tReading from confident duplicate_author file."
            #with open(confident_duplicate_authors_file, 'rb') as csv_file:
            with open(duplicate_authors_file, 'rb') as csv_file:
                duplicate_author_reader = csv.reader(
                    csv_file, delimiter=',', quotechar='"')
                next(duplicate_author_reader)
                count = 0
                for row in duplicate_author_reader:
                    count += 1
                    if count % 10000 == 0:
                        print "\tFinish reading in  "  \
                            + str(count) + " lines of the file."
                    author_list = row[1].split()
                    for author_id in author_list:
                        duplicate_author_dict.setdefault(int(row[0]), set()).add(int(author_id))
        print "\tSerialization files related to coauthors do not exist."
        # The maximum id for author is 2293837 and for paper is 2259021
        all_author_paper_matrix = lil_matrix((max_author + 1, max_paper + 1))
        author_paper_matrix = lil_matrix((max_author + 1, max_paper + 1))
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
                paper_id = int(row[0])
                author_id = int(row[1])
                all_author_paper_matrix[author_id, paper_id] = 1
                if author_id in duplicate_author_dict:
                    for id in duplicate_author_dict[author_id]:
                        all_author_paper_matrix[id, paper_id] = 1
                if author_id in id_name_dict:
                    author = Name(row[3] + ' ' + row[2], True)
                    author_paper_matrix[author_id, paper_id] = 1
                    # Add names appeared in paperauthor.csv
                    if author.last_name == name_instance_dict[id_name_dict[author_id][0]].last_name:
                        name_instance_dict[id_name_dict[author_id][0]].add_alternative(author.name)
                        id_name_dict[author_id].append(author.name)
                    elif SequenceMatcher(None, author.name, id_name_dict[author_id][0]).ratio() >= 0.6:
                        name_instance_dict[id_name_dict[author_id][0]].add_alternative(author.name)
                        id_name_dict[author_id].append(author.name)
        print "\tComputing the coauthor graph."
        coauthor_matrix = author_paper_matrix * all_author_paper_matrix.transpose()
        coauthor_2hop_matrix = coauthor_matrix * coauthor_matrix.transpose()

        # Time consuming.
        # print "\tRemoving diagonal elements in coauthor_matrix."
        # coauthor_matrix = coauthor_matrix - spdiags(coauthor_matrix.diagonal(), 0, max_author + 1, max_author + 1, 'csr')
        # coauthor_2hop_matrix = coauthor_2hop_matrix - spdiags(coauthor_2hop_matrix.diagonal(), 0, max_author + 1, max_author + 1, 'csr')

        print "\tWriting into serialization files related to coauthors.\n"
        cPickle.dump(
            coauthor_matrix,
            open(serialization_dir + coauthor_matrix_file, "wb"), 2)
        cPickle.dump(
            coauthor_2hop_matrix,
            open(serialization_dir + '2hop_' + coauthor_matrix_file, "wb"), 2)
        cPickle.dump(
            author_paper_matrix,
            open(serialization_dir + author_paper_matrix_file, "wb"), 2)
        cPickle.dump(
            all_author_paper_matrix,
            open(serialization_dir + "all_" + author_paper_matrix_file, "wb"), 2)
        cPickle.dump(
            name_instance_dict,
            open(serialization_dir + 'complete_' + name_instance_file, "wb"), 2)
        cPickle.dump(
            id_name_dict,
            open(serialization_dir + 'complete_' + id_name_file, "wb"), 2)

    # Both time and space consuming.
    # coauthor_3hop_matrix = coauthor_2hop_matrix * coauthor_matrix.transpose()

    return (author_paper_matrix, all_author_paper_matrix, coauthor_matrix, coauthor_2hop_matrix, name_instance_dict, id_name_dict)


def load_covenue_files(id_name_dict, author_paper_matrix, all_author_paper_matrix):
    """Load covenue relationship."""
    if os.path.isfile(serialization_dir + author_venue_matrix_file) and \
            os.path.isfile(serialization_dir + covenue_matrix_file) and \
            os.path.isfile(serialization_dir + 'all_' + author_venue_matrix_file):
        print "\tSerialization files related to author_venue exist."
        print "\tReading in the serialization files.\n"
        covenue_matrix = cPickle.load(open(
            serialization_dir + covenue_matrix_file, "rb"))
        author_venue_matrix = cPickle.load(open(
            serialization_dir + author_venue_matrix_file, "rb"))
        all_author_venue_matrix = cPickle.load(open(
            serialization_dir + 'all_' + author_venue_matrix_file, "rb"))
    else:
        print "\tSerialization files related to author_venue do not exist."
        # The maximum id for conference is 22228
        all_author_venue_matrix = lil_matrix((max_author + 1, max_conference + 1))
        paper_venue_matrix = lil_matrix((max_paper + 1, max_conference+ 1))
        print "\tReading in the sanitizedPaper.csv file."
        with open(paper_file, 'rb') as csv_file:
            paper_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            # Skip first line
            next(paper_reader)
            for row in paper_reader:
                paper_id = int(row[0])
                conference = int(row[3])
                if conference > 0:
                    paper_venue_matrix[paper_id, conference] = 1

        print "\tComputing the author_venue matrix."
        author_venue_matrix = author_paper_matrix * paper_venue_matrix
        all_author_venue_matrix = all_author_paper_matrix * paper_venue_matrix
        print "\tComputing the covenue matrix."
        covenue_matrix = author_venue_matrix * author_venue_matrix.transpose()

        print "\tWriting into serialization files related to author_venue.\n"
        cPickle.dump(
            author_venue_matrix,
            open(serialization_dir + author_venue_matrix_file, "wb"), 2)
        cPickle.dump(
            all_author_venue_matrix,
            open(serialization_dir + 'all_' + author_venue_matrix_file, "wb"), 2)
        cPickle.dump(
            covenue_matrix,
            open(serialization_dir + covenue_matrix_file, "wb"), 2)

    # Time consuming
    # print "\tRemoving diagonal elements in covenue_matrix.\n"
    # covenue_matrix = covenue_matrix - spdiags(covenue_matrix.diagonal(), 0, max_author + 1, max_author + 1, 'csr')

    return (covenue_matrix, author_venue_matrix)


def load_author_word_files(id_name_dict, author_paper_matrix):
    """Load author-paper-titleword relationship."""
    if os.path.isfile(serialization_dir + author_word_matrix_file):
        print "\tSerialization files related to author_word exist."
        print "\tReading in the serialization files.\n"
        author_word_matrix = cPickle.load(open(
            serialization_dir + author_word_matrix_file, "rb"))
    else:
        print "\tSerialization files related to author_word do not exist."

        # stopwords = set()
        # print "\tReading in stopword file."
        # with open(stopword_file, 'rb') as csv_file:
        #     stopword_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        #     # skip first line
        #     next(stopword_reader)
        #     for row in stopword_reader:
        #         if row:
        #             stopwords.add(row[0].strip())

        print "\tReading in the sanitizedPaper.csv file and roughly filter words."
        word_statistic_dict = {}
        with open(paper_file, 'rb') as csv_file:
            paper_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            # skip first line
            next(paper_reader)
            index = 0
            for row in paper_reader:
                paper_id = int(row[0])
                title = row[1]
                words = title.split(' ')
                for word in words:
                    word = word.strip().lower()
                    if word != "":
                        word_statistic_dict.setdefault(word, 0)
                        word_statistic_dict[word] += 1
        stopwords = set()
        max_word = 0
        for (word, count) in word_statistic_dict.iteritems():
            if count <= 1 or count > 500000:
                stopwords.add(word)
            else:
                max_word += 1
        print "\tThere are in totoal " + str(max_word) + " words."
        max_word -= 1
        print "\tComputing the paper_word matrix."
        paper_word_matrix = lil_matrix((max_paper + 1, max_word + 1))

        word_id_dict = {}
        id_word_dict = {}
        with open(paper_file, 'rb') as csv_file:
            paper_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            # Skip first line
            next(paper_reader)
            index = 0
            for row in paper_reader:
                paper_id = int(row[0])
                title = row[1]
                words = title.split(' ')
                for word in words:
                    word = word.strip().lower()
                    if word not in stopwords and word != "":
                        if word not in word_id_dict:
                            word_id_dict[word] = index
                            id_word_dict[index] = word
                            paper_word_matrix[paper_id, index] = 1
                            index += 1
                        else:
                            paper_word_matrix[paper_id, word_id_dict[word]] = 1

        print "\tComputing the author_word matrix."
        author_word_matrix = author_paper_matrix * paper_word_matrix

        author_word_count = author_word_matrix.sum(0)
        count = 0
        # View high frequent words as stopwords
        for word_index in xrange(max_word + 1):
            if author_word_count[0, word_index] <= 1 or author_word_count[0, word_index] > word_title_count_threshold:
                stopwords.add(id_word_dict[word_index])
                count += 1

        print "\tRemoving " + str(count) + " words."
        print "\tRecomputing the paper_word matrix."
        paper_word_matrix = lil_matrix((max_paper + 1, max_word - count + 1))

        word_id_dict = {}
        with open(paper_file, 'rb') as csv_file:
            paper_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            # skip first line
            next(paper_reader)
            index = 0
            for row in paper_reader:
                paper_id = int(row[0])
                title = row[1]
                words = title.split(' ')
                for word in words:
                    word = word.strip().lower()
                    if word not in stopwords and word != "":
                        if word not in word_id_dict:
                            word_id_dict[word] = index
                            paper_word_matrix[paper_id, index] = 1
                            index += 1
                        else:
                            paper_word_matrix[paper_id, word_id_dict[word]] = 1

        print "\tRecomputing the author_word matrix."
        author_word_matrix = author_paper_matrix * paper_word_matrix

        print "\tWriting into serialization files related to author_word.\n"
        cPickle.dump(
            author_word_matrix,
            open(serialization_dir + author_word_matrix_file, "wb"), 2)
    return author_word_matrix


def load_author_affili_matrix_files():
    """Load author-affiliation(organization) relationship."""
    if os.path.isfile(serialization_dir + author_affli_matrix_file):
        print "\tSerialization files related to author_affiliation exist."
        print "\tReading in the serialization files.\n"
        author_affi_matrix = cPickle.load(open(
            serialization_dir + author_affli_matrix_file, "rb"))
    else:
        print "\tSerialization files related to author_affiliation do not exist."
        dict_author_affi = dict()
        dict_affi = dict()
        cnt_affi = 1
        cnt_line = 0
        word_count = {}
        with open(author_file, 'rb') as csv_file:
            author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            next(author_reader)
            for row in author_reader:
                author_affili = row[2].strip().lower()
                author_affilis = re.sub('[^a-zA-Z ]', ' ', author_affili)
                words = author_affilis.split()
                for word in words:
                    if word != '':
                        word_count[word] = word_count.setdefault(word, 0) + 1
        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            next(paper_author_reader)
            for row in paper_author_reader:
                cnt_line += 1
                if cnt_line % 2000000 == 0:
                    print "\tFinish analysing " + str(cnt_line) + " lines of the file."
                author_id = int(row[1])
                author_affili = row[3].strip().lower()
                author_affilis = re.sub('[^a-zA-Z ]', ' ', author_affili)
                words = author_affilis.split()
                for word in words:
                    if word != '':
                        word_count[word] = word_count.setdefault(word, 0) + 1

        word_list = list(word_count.iterkeys())
        # View high frequent words as stopwords
        for word in word_list:
            if word_count[word] > organization_count_threshold:
                del word_count[word]
        sorted_ = sorted(word_count.items(), key=lambda x: -x[1])
        print sorted_[0:20]
        with open(author_file, 'rb') as csv_file:
            author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            next(author_reader)
            for row in author_reader:
                cnt_line += 1
                if cnt_line % 40000 == 0:
                    print "\tFinish analysing " + str(cnt_line) + " lines of the file."
                author_id = int(row[0])
                if author_id in duplicate_author_dict:
                    duplicate_authors = duplicate_author_dict[author_id]
                else:
                    duplicate_authors = list()
                author_affili = row[2].strip().lower()
                if author_affili != '':
                    author_affilis = re.sub('[^a-zA-Z ]', ' ', author_affili)
                    words = author_affilis.split()
                    for word in words:
                        if word == '':
                            continue
                        if word in word_count:
                            if word not in dict_affi:
                                dict_affi[word] = cnt_affi
                                cnt_affi += 1
                            dict_author_affi.setdefault(author_id, list()).append(word)
                            for id in duplicate_authors:
                                dict_author_affi.setdefault(id, list()).append(word)
        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            next(paper_author_reader)
            for row in paper_author_reader:
                cnt_line += 1
                if cnt_line % 2000000 == 0:
                    print "\tFinish analysing " + str(cnt_line) + " lines of the file."
                author_id = int(row[1])
                if author_id in duplicate_author_dict:
                    duplicate_authors = duplicate_author_dict[author_id]
                else:
                    duplicate_authors = list()
                author_affili = row[3].strip().lower()
                if author_affili != '':
                    author_affilis = re.sub('[^a-zA-Z ]', ' ', author_affili)
                    words = author_affilis.split()
                    for word in words:
                        if word == '':
                            continue
                        if word in word_count:
                            if word not in dict_affi:
                                dict_affi[word] = cnt_affi
                                cnt_affi += 1
                            dict_author_affi.setdefault(author_id, list()).append(word)
                            for id in duplicate_authors:
                                dict_author_affi.setdefault(id, list()).append(word)
        #nUniqueAffi is the number of unique affliations
        nUniqueAffi = cnt_affi

        #Create author-affiliation matrix
        print "\tCreating author-affiliation matrix."
        author_affi_matrix = lil_matrix((max_author + 1, nUniqueAffi + 1))
        for author_id in dict_author_affi.iterkeys():
            author_affi = dict_author_affi[author_id]
            for affi in author_affi:
                author_affi_matrix[author_id, dict_affi[affi]] += 1

        author_affi_matrix = author_affi_matrix.tocsr()
        print "\tWriting into serialization files related to author_affi.\n"
        cPickle.dump(author_affi_matrix,
                     open(serialization_dir + author_affli_matrix_file, "wb"), 2)

        ## Summary: sorted_affi_freq and sorted_affiName
        #sort the frequency of each affiliation from high to low.
        #sorted_affiName (a list) stores the corresponding affiliation names

        # sorted_affiName = sorted(dict_affi_frequency, key=dict_affi_frequency.get, reverse=True)
        # sorted_affi_freq = range(0, len(sorted_affiName))
        # for i in range(0, len(sorted_affiName)):
        #     sorted_affi_freq[i] = dict_affi_frequency[sorted_affiName[i]]

        #you can see the frequency of a certain affiliation.
        #Most common one is '' (none)
        #return (author_affi_matrix, sorted_affiName, sorted_affi_freq)

    return author_affi_matrix


def load_author_year_matrix_files():
    """Load author-paper-year relationship."""
    if os.path.isfile(serialization_dir + author_year_matrix_file):
        print "\tSerialization files related to author_year exist."
        print "\tReading in the serialization files."
        author_year_matrix = cPickle.load(open(serialization_dir + author_year_matrix_file, "rb"))

    else:
        MinValidYear = 1900
        MaxValidYear = 2013
        nValidYearSpan = MaxValidYear - MinValidYear + 1

        dict_paper_year = dict()
        dict_author_year = dict()

        print "\tConstruct paperID-year dict"
        with open(paper_file, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                paper_id = int(row[0])
                year = int(row[2])
                if year >= MinValidYear and year <= MaxValidYear:
                    dict_paper_year[paper_id] = year

        print "\tConstruct author-year dict"
        cnt_line = 0
        with open(paper_author_file, 'rb') as csv_file:
            paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            next(paper_author_reader)
            for row in paper_author_reader:
                cnt_line += 1
                if cnt_line % 2000000 == 0:
                    print "\tFinish analysing " + str(cnt_line) + " lines of the file."
                paper_id = int(row[0])
                author_id = int(row[1])
                if paper_id in dict_paper_year:
                    year = dict_paper_year[paper_id]
                    if author_id not in dict_author_year:
                        dict_author_year[author_id] = [year]
                    else:
                        dict_author_year[author_id] += [year]

        #Create author-year matrix
        print "\tCreating author-year matrix."
        author_year_matrix = lil_matrix((max_author + 1, nValidYearSpan))
        for author_id in dict_author_year.iterkeys():
            allYears = dict_author_year[author_id]
            for year in allYears:
                author_year_matrix[author_id, year - MinValidYear] += 1

        print "\tWriting into serialization files related to author_year."
        cPickle.dump(author_year_matrix,
                     open(serialization_dir + author_year_matrix_file, "wb"), 2)

    return author_year_matrix