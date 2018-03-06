import csv
import cPickle
import os
import re

from difflib import SequenceMatcher
from scipy.sparse import lil_matrix
from sklearn.preprocessing import normalize

from custom_setting import *
from string_based import *
from name import *

duplicate_author_dict = {}
normalized_feature_dict = {}


class Metapaths(object):
    """Keeping metapaths features for computing similarity between author id pairs."""

    def __init__(self, AP, APV, APW, AO, AY, APA, APVPA, APAPA, APAPV):
        #AP: author-paper
        #APV: author-venue
        #APW: author-paper-titleword
        #AO: author-orgnization
        #AY: author-year
        #APA: author-paper-author
        #APVPA: author-venue-author
        #APAPA: author-paper-author-paper-author
        #APAPV: author-paper-author-paper-venue
        self.AP = AP
        self.APV = APV
        self.APW = APW
        self.AO = AO
        self.AY = AY
        self.APA = APA
        self.APVPA = APVPA
        self.APAPA = APAPA
        self.APAPV = APAPV


def load_coauthor_files(name_instance_dict, id_name_dict):
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
        if os.path.isfile(duplicate_authors_file):
            print "\tReading from confident duplicate_author file."
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
                    author = Name(row[2], True)
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


def compute_similarity_score(author_A, author_B, metapaths):
    """Compute similarity of two author ids based on metapaths"""
    if author_A not in normalized_feature_dict:
        feature_A = (metapaths.AP.getrow(author_A),
                     metapaths.APA.getrow(author_A),
                     metapaths.APV.getrow(author_A),
                     metapaths.APVPA.getrow(author_A),
                     #metapaths.APK.getrow(author_A),
                     metapaths.AO.getrow(author_A),
                     metapaths.APAPA.getrow(author_A),
                     metapaths.APAPV.getrow(author_A),
                     metapaths.AY.getrow(author_A),
                     metapaths.APW.getrow(author_A))
        normalized_feature_A = (
            normalize(feature_A[0], norm='l2', axis=1),
            normalize(feature_A[1], norm='l2', axis=1),
            normalize(feature_A[2], norm='l2', axis=1),
            normalize(feature_A[3], norm='l2', axis=1),
            normalize(feature_A[4], norm='l2', axis=1),
            normalize(feature_A[5], norm='l2', axis=1))
            # normalize(feature_A[6], norm='l2', axis=1))
        # normalize(feature_A[7], norm='l2', axis=1),
        # normalize(feature_A[8], norm='l2', axis=1),
        # normalize(feature_A[9], norm='l2', axis=1),
        # normalize(feature_A[10], norm='l2', axis=1)
        normalized_feature_dict[author_A] = normalized_feature_A
    else:
        normalized_feature_A = normalized_feature_dict[author_A]

    if author_B not in normalized_feature_dict:
        feature_B = (metapaths.AP.getrow(author_B),
                     metapaths.APA.getrow(author_B),
                     metapaths.APV.getrow(author_B),
                     metapaths.APVPA.getrow(author_B),
                     # metapaths.APK.getrow(author_B),
                     metapaths.AO.getrow(author_B),
                     metapaths.APAPA.getrow(author_B),
                     metapaths.APAPV.getrow(author_B),
                     metapaths.AY.getrow(author_B),
                     metapaths.APW.getrow(author_A))
        normalized_feature_B = (
            normalize(feature_B[0], norm='l2', axis=1),
            normalize(feature_B[1], norm='l2', axis=1),
            normalize(feature_B[2], norm='l2', axis=1),
            normalize(feature_B[3], norm='l2', axis=1),
            normalize(feature_B[4], norm='l2', axis=1),
            normalize(feature_B[5], norm='l2', axis=1))
        # normalize(feature_B[6], norm='l2', axis=1))
        # normalize(feature_B[7], norm='l2', axis=1),
        # normalize(feature_B[8], norm='l2', axis=1),
        # normalize(feature_B[9], norm='l2', axis=1),
        # normalize(feature_B[10], norm='l2', axis=1)
        normalized_feature_dict[author_B] = normalized_feature_B
    else:
        normalized_feature_B = normalized_feature_dict[author_B]

    similarity = (
        normalized_feature_A[0].multiply(normalized_feature_B[0]).sum(),  # same paper
        normalized_feature_A[1].multiply(normalized_feature_B[1]).sum(),  # APA
        normalized_feature_A[2].multiply(normalized_feature_B[2]).sum(),  # AV
        normalized_feature_A[3].multiply(normalized_feature_B[3]).sum(),  # AVA
        # 1000 * normalized_feature_A[3].multiply(normalized_feature_B[6]).sum(),
        # 1000 * normalized_feature_A[6].multiply(normalized_feature_B[3]).sum(),
        # 100000 * normalized_feature_A[4].multiply(normalized_feature_B[4]).sum(),  # APK
        normalized_feature_A[4].multiply(normalized_feature_B[4]).sum(),  # AO
        normalized_feature_A[5].multiply(normalized_feature_B[5]).sum(),  # APAPA
        # 1000 * normalized_feature_A[7].multiply(normalized_feature_B[7]).sum(),  # APKPA
        # 1000 * normalized_feature_A[8].multiply(normalized_feature_B[8]).sum(),  # APAPV
        # 1 * normalized_feature_A[9].multiply(normalized_feature_B[9]).sum(),  # AY
        # 1000 * normalized_feature_A[10].multiply(normalized_feature_B[10]).sum(),  # APW
        merge_threshold)

    return similarity


def merge_name_instances(name_instance_dict, id_name_dict, author_A, author_B):
    """Merge author_B's name instance into author_A's"""
    if id_name_dict[author_A][0] == id_name_dict[author_B][0]:
        return
    to_del = id_name_dict[author_B][0]
    for id in set(name_instance_dict[id_name_dict[author_B][0]].author_ids):
        name_instance_dict[id_name_dict[author_A][0]].add_author_id(id)
        id_name_dict[id][0] = id_name_dict[author_A][0]
    del name_instance_dict[to_del]


def local_clustering(similarity_dict, potential_duplicate_groups, name_instance_dict, id_name_dict, name_statistics, metapaths):
    """Detect duplicate pairs based on coauthor relationship between authors."""
    count = 0
    statistic = [0] * 14
    real_duplicate_groups = set()

    # Compute similarity between two name ids based on metapaths if their name are comparable
    for potential_duplicate_group in potential_duplicate_groups:
        if count % 10000 == 0:
            print "\tFinish computing similarities for " \
                + str(float(count)/len(potential_duplicate_groups)*100) \
                + "% (" + str(count) + "/" + str(len(potential_duplicate_groups)) \
                + ") possible duplicate groups."
            print "\tStatistic about merges based on different features: " + str(statistic)
        count += 1

        author_A = potential_duplicate_group[0]
        author_B = potential_duplicate_group[1]
        name_A = id_name_dict[author_A][0]
        name_B = id_name_dict[author_B][0]
        if not name_comparable(name_instance_dict[name_A], name_instance_dict[name_B], name_statistics):
            continue

        if potential_duplicate_group not in similarity_dict:
            similarity = compute_similarity_score(author_A, author_B, metapaths)
            if max(similarity) == merge_threshold:
                print("Removing:", potential_duplicate_group)
                potential_duplicate_groups.remove(potential_duplicate_group)
                continue
            similarity_dict[potential_duplicate_group] = max(similarity)
            statistic[similarity.index(max(similarity))] += 1

    # Sort author pairs based on their similarity, then merge their name instances if necessary
    sorted_potential_duplicate_groups = sorted(similarity_dict.keys(), key=lambda x: -similarity_dict[x])
    for potential_duplicate_group in sorted_potential_duplicate_groups:
        if count % 1 == 0:
            print "\tFinish merging " \
                + str(float(count)/len(potential_duplicate_groups)*100) \
                + "% (" + str(count) + "/" + str(len(potential_duplicate_groups)) \
                + ") possible duplicate groups."
            print "\tStatistic about merges based on different features: " + str(statistic)
        count += 1

        author_A = potential_duplicate_group[0]
        author_B = potential_duplicate_group[1]

        name_A = id_name_dict[author_A][0]
        name_B = id_name_dict[author_B][0]

        if name_A == '' or name_B == '':
            continue

        if id_name_dict[author_A][0] not in name_instance_dict or id_name_dict[author_B][0] not in name_instance_dict:
            print "\t\t" + id_name_dict[author_A][0] + str(author_A)
            print "\t\t" + id_name_dict[author_B][0] + str(author_B)
            continue

        # if not name_comparable(name_instance_dict[name_A], name_instance_dict[name_B], name_statistics):
        #     continue

        name_instance_A = name_instance_dict[id_name_dict[author_A][0]]
        name_instance_B = name_instance_dict[id_name_dict[author_A][0]]

        # Merge two name instances
        # Merge two name instances
        if name_A != name_B:
            if len(name_A) <= 10 or len(name_B) <= 10:
                pass
            elif name_B.replace(' ', '').find(name_A.replace(' ', '')) >= 0 \
                    or name_A.replace(' ', '').find(name_B.replace(' ', '')) >= 0 \
                    or name_A.replace(' ', '') == name_B.replace(' ', '') \
                    or sorted(name_A.replace(' ', '')) == sorted(name_B.replace(' ', '')) \
                    or my_string_match_score(name_A, name_B, name_statistics,
                                             name_instance_A.is_asian or name_instance_B.is_asian) >= 10:
                if len(name_A.split()) > len(name_B.split()):
                    print "\t\tMerge two name instances: " + id_name_dict[author_A][1] + ': ' + str(
                        len(name_instance_dict[name_A].author_ids)) + \
                          '   <--   ' + id_name_dict[author_B][1] + ': ' + str(
                        len(name_instance_dict[name_B].author_ids))
                    merge_name_instances(name_instance_dict, id_name_dict, author_A, author_B)
                elif len(name_A.split()) < len(name_B.split()):
                    print "\t\tMerge two name instances: " + id_name_dict[author_B][1] + ': ' + str(
                        len(name_instance_dict[name_B].author_ids)) + \
                          '   <--   ' + id_name_dict[author_A][1] + ': ' + str(
                        len(name_instance_dict[name_A].author_ids))
                    merge_name_instances(name_instance_dict, id_name_dict, author_B, author_A)
                elif len(name_instance_dict[name_A].author_ids) > len(name_instance_dict[name_B].author_ids):
                    print "\t\tMerge two name instances: " + id_name_dict[author_A][1] + ': ' + str(
                        len(name_instance_dict[name_A].author_ids)) + \
                          '   <--   ' + id_name_dict[author_B][1] + ': ' + str(
                        len(name_instance_dict[name_B].author_ids))
                    merge_name_instances(name_instance_dict, id_name_dict, author_A, author_B)

                elif len(name_instance_dict[name_A].author_ids) == len(name_instance_dict[name_B].author_ids):
                    score_A = 0
                    elements = name_A.split()
                    for i in xrange(len(elements) - 1):
                        if elements[i] + ' ' + elements[i + 1] in name_statistics:
                            score_A += name_statistics[elements[i] + ' ' + elements[i + 1]]
                    if len(elements) == 1:
                        score_A = 0
                    else:
                        score_A /= len(elements)
                    score_B = 0
                    elements = name_B.split()
                    for i in xrange(len(elements) - 1):
                        if elements[i] + ' ' + elements[i + 1] in name_statistics:
                            score_B += name_statistics[elements[i] + ' ' + elements[i + 1]]
                    if len(elements) == 1:
                        score_B = 0
                    else:
                        score_B /= len(elements)
                    if score_A > score_B:
                        print "\t\tMerge two name instances: " + id_name_dict[author_A][1] + ': ' + str(
                            len(name_instance_dict[name_A].author_ids)) + \
                              '   <--   ' + id_name_dict[author_B][1] + ': ' + str(
                            len(name_instance_dict[name_B].author_ids))
                        merge_name_instances(name_instance_dict, id_name_dict, author_A, author_B)
                    elif score_A == score_B:
                        if len(name_B) >= len(name_A):
                            print "\t\tMerge two name instances: " + id_name_dict[author_A][1] + ': ' + str(
                                len(name_instance_dict[name_A].author_ids)) + \
                                  '   <--   ' + id_name_dict[author_B][1] + ': ' + str(
                                len(name_instance_dict[name_B].author_ids))
                            merge_name_instances(name_instance_dict, id_name_dict, author_A, author_B)
                        else:
                            print "\t\tMerge two name instances: " + id_name_dict[author_B][1] + ': ' + str(
                                len(name_instance_dict[name_B].author_ids)) + \
                                  '   <--   ' + id_name_dict[author_A][1] + ': ' + str(
                                len(name_instance_dict[name_A].author_ids))
                            merge_name_instances(name_instance_dict, id_name_dict, author_B, author_A)
                    else:
                        print "\t\tMerge two name instances: " + id_name_dict[author_B][1] + ': ' + str(
                            len(name_instance_dict[name_B].author_ids)) + \
                              '   <--   ' + id_name_dict[author_A][1] + ': ' + str(
                            len(name_instance_dict[name_A].author_ids))
                        merge_name_instances(name_instance_dict, id_name_dict, author_B, author_A)
                else:
                    print "\t\tMerge two name instances: " + id_name_dict[author_B][1] + ': ' + str(
                        len(name_instance_dict[name_B].author_ids)) + \
                          '   <--   ' + id_name_dict[author_A][1] + ': ' + str(
                        len(name_instance_dict[name_A].author_ids))
                    merge_name_instances(name_instance_dict, id_name_dict, author_B, author_A)


        real_duplicate_groups.add(potential_duplicate_group)

    return real_duplicate_groups