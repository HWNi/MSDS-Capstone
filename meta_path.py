import csv
import math
from custom_setting import *
from textblob import TextBlob as tb
from scipy.sparse import lil_matrix
from sklearn.preprocessing import normalize
from string_based import *
from name import *

duplicate_author_dict = {}
normalized_feature_dict = {}

class Metapaths(object):
    # Keep metapaths features for computing similarity between author id pairs.

    def __init__(self, AP, APV, APW, AO, AY, APA, APVPA, APAPA, APAPV):
        self.AP = AP    # AP: author-paper
        self.APV = APV  # APV: author-venue
        self.APW = APW  # APW: author-paper-titleword
        self.AO = AO    # AO: author-orgnization
        self.AY = AY    # AY: author-year
        self.APA = APA  # APA: author-paper-author
        self.APVPA = APVPA  # APVPA: author-venue-author
        self.APAPA = APAPA  # APAPA: author-paper-author-paper-author
        self.APAPV = APAPV  # APAPV: author-paper-author-paper-venue


def load_coauthor_files(name_instance_dict, id_name_dict):
    # A function load coauthor relationship.
    all_author_paper_matrix = lil_matrix((max_author + 1, max_paper + 1))
    author_paper_matrix = lil_matrix((max_author + 1, max_paper + 1))
    with open(paper_author_file, 'rb') as csv_file:
        paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        # Skip first line
        next(paper_author_reader)
        for row in paper_author_reader:
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

    coauthor_matrix = author_paper_matrix * all_author_paper_matrix.transpose()
    coauthor_2hop_matrix = coauthor_matrix * coauthor_matrix.transpose()

    return author_paper_matrix, all_author_paper_matrix, coauthor_matrix, coauthor_2hop_matrix, name_instance_dict, id_name_dict


def load_covenue_files(author_paper_matrix):
    # Load covenue relationship
    paper_venue_matrix = lil_matrix((max_paper + 1, max_conference+ 1))
    with open(paper_file, 'rb') as csv_file:
        paper_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        # Skip first line
        next(paper_reader)
        for row in paper_reader:
            paper_id = int(row[0])
            conference = int(row[3])
            if conference > 0:
                paper_venue_matrix[paper_id, conference] = 1

    author_venue_matrix = author_paper_matrix * paper_venue_matrix
    covenue_matrix = author_venue_matrix * author_venue_matrix.transpose()

    return covenue_matrix, author_venue_matrix


def load_author_word_files(author_paper_matrix):
    # Load author-paper-titleword relationship
    word_statistic_dict = {}
    with open(paper_file, 'rb') as csv_file:
        paper_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        # skip first line
        next(paper_reader)
        for row in paper_reader:
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
    max_word -= 1
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

    author_word_matrix = author_paper_matrix * paper_word_matrix

    author_word_count = author_word_matrix.sum(0)
    count = 0

    # View high frequent words as stopwords
    for word_index in xrange(max_word + 1):
        if author_word_count[0, word_index] <= 1 or author_word_count[0, word_index] > word_title_count_threshold:
            stopwords.add(id_word_dict[word_index])
            count += 1
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

    author_word_matrix = author_paper_matrix * paper_word_matrix

    return author_word_matrix


def load_author_affili_matrix_files():
    def denoise_affiliation():
        # remove noise for each affiliation
        affiliation_list = []
        header = True
        with open(author_file, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if header:
                    header = False
                    continue
                affiliation_list.append(row[2].lower())
            f.close()

        blob_list = [tb(re.sub(r'[^a-z ]', '', s)) for s in affiliation_list]

        def tf(word, blob):
            return float(blob.words.count(word)) / float(len(blob.words))

        def n_containing(word, bloblist):
            return sum(1 for blob in bloblist if word in blob.words)

        def idf(word, bloblist):
            return math.log(len(bloblist) / float((1 + n_containing(word, bloblist))))

        def tfidf(word, blob, bloblist):
            return tf(word, blob) * idf(word, bloblist)

        affiliation_refine = []

        for i, blob in enumerate(blob_list):
            print("Top words in document {}".format(i + 1))
            scores = {word: tfidf(word, blob, blob_list) for word in blob.words}
            sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            s = ""
            for word, score in sorted_words[:3]:
                s = s + word + " "
                print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))
            s = s.strip()
            affiliation_refine.append(str(s))

        with open(author_file_refined, 'wb') as csv_write:
            paper_writer = csv.writer(csv_write)
            with open(author_file, 'rb') as csv_read:
                paper_reader = csv.reader(csv_read, delimiter=',')
                # Skip first line
                header = next(paper_reader)
                header.append('affiliation_refined')
                paper_writer.writerow(header)
                count = 0
                for row in paper_reader:
                    row.append(affiliation_refine[count])
                    paper_writer.writerow(row)
                    count += 1
                csv_read.close()
            csv_write.close()

    # remove noise for each affiliation
    denoise_affiliation()
    dict_author_affi = dict()
    dict_affi = dict()
    cnt_affi = 1
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

    # n_unique_affi is the number of unique affliations
    n_unique_affi = cnt_affi

    # Create author-affiliation matrix
    author_affi_matrix = lil_matrix((max_author + 1, n_unique_affi + 1))
    for author_id in dict_author_affi.iterkeys():
        author_affi = dict_author_affi[author_id]
        for affi in author_affi:
            author_affi_matrix[author_id, dict_affi[affi]] += 1

    author_affi_matrix = author_affi_matrix.tocsr()

    return author_affi_matrix


def load_author_year_matrix_files():
    # Load author-paper-year relationship.
    min_valid_year = 1900
    max_valid_year = 2013
    n_valid_year_span = max_valid_year - min_valid_year + 1

    dict_paper_year = dict()
    dict_author_year = dict()

    with open(paper_file, 'rb') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            paper_id = int(row[0])
            year = int(row[2])
            if min_valid_year <= year <= max_valid_year:
                dict_paper_year[paper_id] = year

    with open(paper_author_file, 'rb') as csv_file:
        paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        next(paper_author_reader)
        for row in paper_author_reader:
            paper_id = int(row[0])
            author_id = int(row[1])
            if paper_id in dict_paper_year:
                year = dict_paper_year[paper_id]
                if author_id not in dict_author_year:
                    dict_author_year[author_id] = [year]
                else:
                    dict_author_year[author_id] += [year]

    # Create author-year matrix
    author_year_matrix = lil_matrix((max_author + 1, n_valid_year_span))
    for author_id in dict_author_year.iterkeys():
        allYears = dict_author_year[author_id]
        for year in allYears:
            author_year_matrix[author_id, year - min_valid_year] += 1

    return author_year_matrix


def compute_similarity_score(author_a, author_b, meta_paths):
    # Compute similarity of two author ids based on metapaths
    if author_a not in normalized_feature_dict:
        feature__a = (meta_paths.AP.getrow(author_a),
                      meta_paths.APA.getrow(author_a),
                      meta_paths.APV.getrow(author_a),
                      meta_paths.APVPA.getrow(author_a),
                      meta_paths.AO.getrow(author_a),
                      meta_paths.APAPA.getrow(author_a),
                      meta_paths.APAPV.getrow(author_a),
                      meta_paths.AY.getrow(author_a),
                      meta_paths.APW.getrow(author_a))
        normalized_feature__a = (
            normalize(feature__a[0], norm='l2', axis=1),
            normalize(feature__a[1], norm='l2', axis=1),
            normalize(feature__a[2], norm='l2', axis=1),
            normalize(feature__a[3], norm='l2', axis=1),
            normalize(feature__a[4], norm='l2', axis=1),
            normalize(feature__a[5], norm='l2', axis=1))
        normalized_feature_dict[author_a] = normalized_feature__a
    else:
        normalized_feature__a = normalized_feature_dict[author_a]

    if author_b not in normalized_feature_dict:
        feature__b = (meta_paths.AP.getrow(author_b),
                      meta_paths.APA.getrow(author_b),
                      meta_paths.APV.getrow(author_b),
                      meta_paths.APVPA.getrow(author_b),
                      meta_paths.AO.getrow(author_b),
                      meta_paths.APAPA.getrow(author_b),
                      meta_paths.APAPV.getrow(author_b),
                      meta_paths.AY.getrow(author_b),
                      meta_paths.APW.getrow(author_a))
        normalized_feature__b = (
            normalize(feature__b[0], norm='l2', axis=1),
            normalize(feature__b[1], norm='l2', axis=1),
            normalize(feature__b[2], norm='l2', axis=1),
            normalize(feature__b[3], norm='l2', axis=1),
            normalize(feature__b[4], norm='l2', axis=1),
            normalize(feature__b[5], norm='l2', axis=1))
        normalized_feature_dict[author_b] = normalized_feature__b
    else:
        normalized_feature__b = normalized_feature_dict[author_b]

    similarity = (
        normalized_feature__a[0].multiply(normalized_feature__b[0]).sum(),  # same paper
        normalized_feature__a[1].multiply(normalized_feature__b[1]).sum(),  # APA
        normalized_feature__a[2].multiply(normalized_feature__b[2]).sum(),  # AV
        normalized_feature__a[3].multiply(normalized_feature__b[3]).sum(),  # AVA
        normalized_feature__a[4].multiply(normalized_feature__b[4]).sum(),  # AO
        normalized_feature__a[5].multiply(normalized_feature__b[5]).sum(),  # APAPA
        merge_threshold)

    return similarity


def merge_name_instances(name_instance_dict, id_name_dict, author_a, author_b):
    # Merge author_b's name instance into author_a's
    if id_name_dict[author_a][0] == id_name_dict[author_b][0]:
        return
    to_del = id_name_dict[author_b][0]
    for id in set(name_instance_dict[id_name_dict[author_b][0]].author_ids):
        name_instance_dict[id_name_dict[author_a][0]].add_author_id(id)
        id_name_dict[id][0] = id_name_dict[author_a][0]
    del name_instance_dict[to_del]


def local_clustering(similarity_dict, potential_duplicate_groups, name_instance_dict, id_name_dict, name_statistics, metapaths):
    # Detect duplicate pairs based on coauthor relationship between authors.
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

        author__a = potential_duplicate_group[0]
        author__b = potential_duplicate_group[1]
        name__a = id_name_dict[author__a][0]
        name__b = id_name_dict[author__b][0]
        if not name_comparable(name_instance_dict[name__a], name_instance_dict[name__b], name_statistics):
            continue

        if potential_duplicate_group not in similarity_dict:
            similarity = compute_similarity_score(author__a, author__b, metapaths)
            if max(similarity) == merge_threshold:
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

        author__a = potential_duplicate_group[0]
        author__b = potential_duplicate_group[1]

        name__a = id_name_dict[author__a][0]
        name__b = id_name_dict[author__b][0]

        if name__a == '' or name__b == '':
            continue

        if id_name_dict[author__a][0] not in name_instance_dict or id_name_dict[author__b][0] not in name_instance_dict:
            continue

        name_instance__a = name_instance_dict[id_name_dict[author__a][0]]
        name_instance__b = name_instance_dict[id_name_dict[author__a][0]]

        # Merge two name instances
        if name__a != name__b:
            if len(name__a) <= 10 or len(name__b) <= 10:
                pass
            elif name__b.replace(' ', '').find(name__a.replace(' ', '')) >= 0 \
                    or name__a.replace(' ', '').find(name__b.replace(' ', '')) >= 0 \
                    or name__a.replace(' ', '') == name__b.replace(' ', '') \
                    or sorted(name__a.replace(' ', '')) == sorted(name__b.replace(' ', '')) \
                    or my_string_match_score(name__a, name__b, name_statistics,
                                             name_instance__a.is_asian or name_instance__b.is_asian) >= 10:
                if len(name__a.split()) > len(name__b.split()):
                    merge_name_instances(name_instance_dict, id_name_dict, author__a, author__b)
                elif len(name__a.split()) < len(name__b.split()):
                    merge_name_instances(name_instance_dict, id_name_dict, author__b, author__a)
                elif len(name_instance_dict[name__a].author_ids) > len(name_instance_dict[name__b].author_ids):
                    merge_name_instances(name_instance_dict, id_name_dict, author__a, author__b)
                elif len(name_instance_dict[name__a].author_ids) == len(name_instance_dict[name__b].author_ids):
                    score__a = 0
                    elements = name__a.split()
                    for i in xrange(len(elements) - 1):
                        if elements[i] + ' ' + elements[i + 1] in name_statistics:
                            score__a += name_statistics[elements[i] + ' ' + elements[i + 1]]
                    if len(elements) == 1:
                        score__a = 0
                    else:
                        score__a /= len(elements)
                    score__b = 0
                    elements = name__b.split()
                    for i in xrange(len(elements) - 1):
                        if elements[i] + ' ' + elements[i + 1] in name_statistics:
                            score__b += name_statistics[elements[i] + ' ' + elements[i + 1]]
                    if len(elements) == 1:
                        score__b = 0
                    else:
                        score__b /= len(elements)
                    if score__a > score__b:
                        merge_name_instances(name_instance_dict, id_name_dict, author__a, author__b)
                    elif score__a == score__b:
                        if len(name__b) >= len(name__a):
                            merge_name_instances(name_instance_dict, id_name_dict, author__a, author__b)
                        else:
                            merge_name_instances(name_instance_dict, id_name_dict, author__b, author__a)
                    else:
                        merge_name_instances(name_instance_dict, id_name_dict, author__b, author__a)
                else:
                    merge_name_instances(name_instance_dict, id_name_dict, author__b, author__a)
        real_duplicate_groups.add(potential_duplicate_group)

    return real_duplicate_groups
