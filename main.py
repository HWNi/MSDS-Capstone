from io import *
from string_based_cluster import *
import cPickle


class Metapaths(object):
    """Keeping metapaths features for computing similarity between author id pairs."""

    def __init__(self, AP, APV, APW, APK, AO, AY, APA, APVPA, APAPA, APAPV):
        # AP: author-paper
        # APV: author-venue
        # APW: author-paper-titleword
        # APK: author-paper-keyword
        # AO: author-orgnization
        # AY: author-year
        # APA: author-paper-venue
        # APVPA: author-venue-author
        # APAPA: author-paper-author-paper-author
        # APAPV: author-paper-author-paper-venue
        self.AP = AP
        self.APV = APV
        self.APW = APW
        self.APK = APK
        self.AO = AO
        self.AY = AY
        self.APA = APA
        self.APVPA = APVPA
        self.APAPA = APAPA
        self.APAPV = APAPV

if __name__ == '__main__':
    csv.field_size_limit(500 * 1024 * 1024)

    print "Step 1/7: Load files"
    (name_statistics, raw_name_statistics, name_statistics_super, author_paper_stat) = load_name_statistic()
    (name_instance_dict, id_name_dict, name_statistics) = load_author_files(name_statistics, raw_name_statistics,
                                                                            name_statistics_super, author_paper_stat)
    print "\nStep 2/7: Find similar ids to increase recall"
    add_similar_ids_under_name(name_instance_dict, id_name_dict)

    print "\nStep 3/7: Create local clusters or potential_duplicate_groups"
    potential_duplicate_groups = create_potential_duplicate_groups(name_instance_dict, author_paper_stat)

    print "\nStep 4/7: Find and merge local clusters"
    similarity_score_dict = dict()
    real_duplicate_groups1 = local_clustering(similarity_score_dict, potential_duplicate_groups, author_paper_stat,
                                              name_instance_dict, id_name_dict, name_statistics, metapaths)
    real_duplicate_groups2 = local_clustering(similarity_score_dict, potential_duplicate_groups, author_paper_stat,
                                              name_instance_dict, id_name_dict, name_statistics, metapaths)
    real_duplicate_groups = real_duplicate_groups1.union(real_duplicate_groups2)

    print "\nStep 5/7: Obtain the closure, then filter noisy names"
    authors_duplicates_dict = merge_local_clusters(real_duplicate_groups, id_name_dict)
    find_closure(authors_duplicates_dict)
    refine_result(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics, similarity_score_dict,
                  metapaths, True)
    iter_num = 2
    while iter_num > 0:
        find_closure(authors_duplicates_dict)
        refine_result(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics, similarity_score_dict,
                      metapaths, True)
        iter_num -= 1

    print "\nStep 6/7: Final filtering and combining multiple possible guessing"
    final_filter(author_paper_stat, name_statistics, authors_duplicates_dict, name_instance_dict, id_name_dict,
                 similarity_score_dict, metapaths)

    print "\nStep 7/7: Generate submission files"
    save_result(authors_duplicates_dict, name_instance_dict, id_name_dict)
