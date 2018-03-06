# Raw data
author_file = "./data_filtered/Author_refined.csv"
paper_author_file = "./data_filtered/PaperAuthor_refined.csv"
paper_file = './data_filtered/Paper.csv'

# Serialized files
serialization_dir = './serialization/'
result_dir = './result/'

name_statistics_file = 'name_statistics_seal'
author_paper_stat_file = 'author_paper_stat_seal'
name_instance_file = 'name_instance_seal'
id_name_file = 'id_name_seal'

duplicate_authors_file = "./result/duplicate_authors.csv"
duplicate_authors_full_name_file = "./result/duplicate_authors_fullname.csv"
duplicate_groups_file = "duplicate_groups_seal"


coauthor_matrix_file = 'coauthor_seal'
covenue_matrix_file = 'covenue_seal'
author_paper_matrix_file = 'author_paper_seal'
author_affli_matrix_file = 'author_affli_matrix_seal'
author_venue_matrix_file = 'author_venue_seal'
author_year_matrix_file = 'author_year_matrix_seal'
author_word_matrix_file = 'author_word_seal'


# Label Data Filtered
max_author = 3358 # Max Author id in sample
max_paper = 1755784 # Max paper id
max_conference = 1980 # Max conference id
word_title_count_threshold = 2000
organization_count_threshold = 10000
merge_threshold = 0.00000000001

# PubMed
# max_author = 5232561 # Max Author id in sample
# max_paper = 25928577 # Max paper id
# max_affiliation = 83224 # Max affliation id