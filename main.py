from calcSimScore import *
from string_based_cluster import *
from meta_path import *
import cPickle

if __name__ == '__main__':
    #csv.field_size_limit(500 * 1024 * 1024)

    print "Step 1/7: Preprocessing and calculate meta-path-based similarity"
    (name_instance_dict, id_name_dict, name_statistics, author_paper_stat, metapaths) = load_files()

    print "Step 2/7: Enlarge candidate pool of duplicates based on author name similarity"
    add_similar_ids_under_name(name_instance_dict, id_name_dict)
    print "Saving files generated in this step for debug."
    cPickle.dump(name_instance_dict, open(serialization_dir + "step2_" + name_instance_file, "wb"), 2)

    print "Step 3/7: Rank and merge candidates based on meta-path-based similarity"
    potential_duplicate_groups = create_potential_duplicate_groups(name_instance_dict, author_paper_stat)

    print "Step 4/7: Find and merge local clusters"
    similarity_score_dict = dict()
    real_duplicate_groups1 = local_clustering(similarity_score_dict, potential_duplicate_groups, author_paper_stat,
                                              name_instance_dict, id_name_dict, name_statistics, metapaths)
    real_duplicate_groups2 = local_clustering(similarity_score_dict, potential_duplicate_groups, author_paper_stat,
                                              name_instance_dict, id_name_dict, name_statistics, metapaths)
    real_duplicate_groups = real_duplicate_groups1.union(real_duplicate_groups2)

    # print "\nStep 5/7: Obtain the closure, then filter noisy names"
    authors_duplicates_dict = merge_local_clusters(real_duplicate_groups, id_name_dict)
    # find_closure(authors_duplicates_dict)
    # refine_result(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics, similarity_score_dict,
    #               metapaths, True)
    # iter_num = 2
    # while iter_num > 0:
    #     find_closure(authors_duplicates_dict)
    #     refine_result(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics, similarity_score_dict,
    #                   metapaths, True)
    #     iter_num -= 1
    #
    # print "\nStep 6/7: Final filtering and combining multiple possible guessing"
    # final_filter(author_paper_stat, name_statistics, authors_duplicates_dict, name_instance_dict, id_name_dict,
    #              similarity_score_dict, metapaths)
    #
    # print "\nStep 7/7: Generate submission files"
    # save_result(authors_duplicates_dict, name_instance_dict, id_name_dict)
