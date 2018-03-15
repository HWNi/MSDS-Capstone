"""
Note: make sure the paths for all the input (raw data) and output (results) files
"""

# Raw data
author_file = "./data/Author.csv"
paper_author_file = "./data/PaperAuthor.csv"
paper_file = './data/Paper.csv'
author_file_refined = './data/Author_refined_affiliation.csv'

# Refine Affiliation
author_file_refined = './data_filtered/Author_refined_v2.csv'

# Result Directory
result_dir = './result/'
duplicate_authors_file = "./result/duplicate_authors.csv"
duplicate_authors_full_name_file = "./result/duplicate_authors_fullname.csv"

word_title_count_threshold = 2000
organization_count_threshold = 10000
merge_threshold = 0.00000000001

# Aminer setting
max_author = 3358 # Max Author id in sample
max_paper = 1755784 # Max paper id
max_conference = 1980 # Max conference id

# PubMed Setting 
# max_author = 5232561 # Max Author id in sample
# max_paper = 25928577 # Max paper id
# max_affiliation = 83224 # Max affliation id