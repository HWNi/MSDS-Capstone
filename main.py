from pre_processing import *
from string_based import *
from meta_path import *
from post_process import *
import cPickle

if __name__ == '__main__':
    generate_new_author_names()

    name_statistics = dict()
    name_statistics = cal_name_statistics(name_statistics, author_file, 1)
    name_statistics = cal_name_statistics(name_statistics, paper_author_file, 2)

    print "Generate name instance"
    (name_instance_dict, id_name_dict) = generate_name_instance(author_file, 0, 1, name_statistics)

    print "Update name statistics"
    for name_instance in list(name_instance_dict.itervalues()):
        elements = name_instance.name.split()
        for element in elements:
            name_statistics[element] = name_statistics.setdefault(element, 0) + len(name_instance.author_ids)
        for element1 in elements:
            for element2 in elements:
                if element1 != element2:
                    name_statistics[element1 + ' ' + element2] = \
                        name_statistics.setdefault(element1 + ' ' + element2, 0) + len(name_instance.author_ids)

    print "Enlarge candidate pool of duplicates based on author name similarity"
    add_similar_ids_under_name(name_instance_dict, id_name_dict)


    print "Create local clusters or potential_duplicate_groups"
    potential_duplicate_groups = create_potential_duplicate_groups(name_instance_dict)

    print "Calculate similarity matrices"
    (author_paper_matrix, all_author_paper_matrix, coauthor_matrix, coauthor_2hop_matrix, name_instance_dict,id_name_dict) \
        = load_coauthor_files(name_instance_dict, id_name_dict)

    (covenue_matrix, author_venue_matrix) = load_covenue_files(id_name_dict, author_paper_matrix, all_author_paper_matrix)
    author_word_matrix = load_author_word_files(id_name_dict, author_paper_matrix)

    author_org_matrix = load_author_affili_matrix_files()

    author_year_matrix = load_author_year_matrix_files()

    APAPC = coauthor_matrix * author_venue_matrix

    metapaths = Metapaths(author_paper_matrix, author_venue_matrix, author_word_matrix, author_org_matrix,
                          author_year_matrix, coauthor_matrix, covenue_matrix, coauthor_2hop_matrix, APAPC)

    print "Find and merge local clusters"
    similarity_score_dict = dict()
    potential_duplicate_groups = list(potential_duplicate_groups)
    real_duplicate_groups = local_clustering(similarity_score_dict, potential_duplicate_groups,
                                              name_instance_dict, id_name_dict, name_statistics, metapaths)


    print "Obtain the closure, then filter noisy names"
    authors_duplicates_dict = merge_local_clusters(real_duplicate_groups, id_name_dict)

    find_closure(authors_duplicates_dict)

    cPickle.dump(authors_duplicates_dict, open(serialization_dir + "authors_duplicates_dict_seal", "wb"), 2)

    refine_result(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics, similarity_score_dict,
                  metapaths, True)
    iter_num = 2
    while iter_num > 0:
        find_closure(authors_duplicates_dict)
        refine_result(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics, similarity_score_dict,
                      metapaths, True)
        iter_num -= 1

    print "Generate submission files"
    save_result(authors_duplicates_dict, name_instance_dict, id_name_dict)
