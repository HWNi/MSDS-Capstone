def merge_local_clusters(real_duplicate_groups, id_name_dict):
    """Merge local clusters.

    Parameters:
        real_duplicate_groups:
            A set of groups which contain duplicate author_ids separately.

    Returns:
        A dictionary of duplicate authors with key: author id and value:
        a list of duplicate author ids
    """
    id_group_dict = dict()
    print "\tMapping each author to his/her duplicate authors from duplicate groups."
    for group in real_duplicate_groups:
        for author in group:
            id_group_dict.setdefault(author, list()).append(group)

    authors_duplicates_dict = dict()
    for (author_id, real_duplicate_groups) in id_group_dict.iteritems():
        union_group = set()
        for group in real_duplicate_groups:
            union_group = union_group.union(group)
        authors_duplicates_dict[author_id] = union_group

    for author_id in id_name_dict.iterkeys():
        authors_duplicates_dict.setdefault(author_id, set()).add(author_id)

    return authors_duplicates_dict


def find_closure(authors_duplicates_dict):
    """Find the closure of duplicate authors for each author id.
       Example : {1: [1, 2, 3, 4], 2: [2, 3, 4, 5]} -> {1: [2, 3, 4, 5], 2: [1, 3, 4, 5]}

    Parameters:
        authors_duplicates_dict
            A dictionary of duplicate authors with key: author id and value:
            a list of duplicate author ids
    """
    print "\tFinding close duplicate author set for each author id."
    for author_id in authors_duplicates_dict.iterkeys():
        authors_duplicates_dict[author_id].add(author_id)

    iteration = 0
    while True:
        print "\t\tIteration " + str(iteration)
        iteration += 1
        if iteration >= 100:
            break
        do_next_recursion = False
        for (author_id, duplicate_group) in authors_duplicates_dict.iteritems():
            changed = False
            final_duplicate_group = set(duplicate_group)
            for _author_id in duplicate_group:
                if duplicate_group != authors_duplicates_dict[_author_id]:
                    changed = True
                    do_next_recursion = True
                    final_duplicate_group = final_duplicate_group.union(authors_duplicates_dict[_author_id])
            if changed:
                authors_duplicates_dict[author_id] = set(final_duplicate_group)
                for _author_id in duplicate_group:
                    authors_duplicates_dict[_author_id] = set(final_duplicate_group)
        if do_next_recursion is False:
            break

    for author_id in authors_duplicates_dict.iterkeys():
        authors_duplicates_dict[author_id].remove(author_id)


def refine_result(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics, similarity_dict, metapaths, remove_flag):
    """Filter obvious conflict names of duplicate authors for each author id."""
    for author_id in authors_duplicates_dict.iterkeys():
        if author_id in authors_duplicates_dict[author_id]:
            authors_duplicates_dict[author_id].remove(author_id)

    if remove_flag:
        count = 0
        for author_id in authors_duplicates_dict.iterkeys():
            for duplicate_author_id in set(authors_duplicates_dict[author_id]):
                if not name_comparable(name_instance_dict[id_name_dict[author_id][0]],
                                       name_instance_dict[id_name_dict[duplicate_author_id][0]],
                                       name_statistics,
                                       False):
                    authors_duplicates_dict[author_id].remove(duplicate_author_id)
                    if author_id in authors_duplicates_dict[duplicate_author_id]:
                        authors_duplicates_dict[duplicate_author_id].remove(author_id)
                    count += 1
        print "\tRemoving " + str(count) + " author_ids from name comparison."

    conflict_ids = find_conflict_name(authors_duplicates_dict, name_instance_dict, id_name_dict, name_statistics)
    print "\tFinding who are really duplicates among the conflict author_ids"
    subset_similarity_dict = {}
    count = 0
    new_group_set = set()
    for author_id in conflict_ids:
        count += 1
        if count % 100 == 0:
            print "\tAdding pairwise similarities of " \
                + str(float(count)/len(conflict_ids)*100) \
                + "% (" + str(count) + "/" + str(len(conflict_ids)) \
                + ") conflict groups."
        pool = authors_duplicates_dict[author_id]
        pool.add(author_id)
        for id in pool:
            new_group_set.add((id,))
        for candi1 in pool:
            for candi2 in pool:
                if candi1 != candi2:
                    if tuple(sorted((candi1, candi2))) not in similarity_dict:
                        similarity_dict[tuple(sorted((candi1, candi2)))] = max(compute_similarity_score(candi1, candi2, metapaths))
                    subset_similarity_dict[tuple(sorted((candi1, candi2)))] = similarity_dict[tuple(sorted((candi1, candi2)))]

    print "\tSorting conflicted author pairs according to similarity scores."
    sorted_author_pairs = sorted(subset_similarity_dict.keys(), key=lambda candi: -subset_similarity_dict[candi])

    bad_pairs = list()
    for author_pair in sorted_author_pairs:
        author1 = author_pair[0]
        author2 = author_pair[1]
        group1 = tuple()
        for group in new_group_set:
            if author1 in group:
                group1 = group
            if author2 in group:
                group2 = group
        if group1 == group2:
            continue
        new_group = set(group1 + group2)
        if not name_group_comparable(new_group, name_instance_dict, id_name_dict, name_statistics):
            bad_pairs.append(author_pair)
            continue
        else:
            new_group = tuple(sorted(new_group))
        if group1 in new_group_set:
            new_group_set.remove(group1)
        if group2 in new_group_set:
            new_group_set.remove(group2)
        new_group_set.add(new_group)

    count = 0
    for author_pair in bad_pairs:
        count += 1
        if count % 1000 == 0:
            print "\tFinish merging " \
                + str(float(count)/len(bad_pairs)*100) \
                + "% (" + str(count) + "/" + str(len(bad_pairs)) \
                + ") conflict groups with tolerance."
        author1 = author_pair[0]
        author2 = author_pair[1]
        group1 = tuple()
        for group in new_group_set:
            if author1 in group:
                group1 = group
            if author2 in group:
                group2 = group
        if group1 == group2:
            continue
        new_group = set(group1 + group2)
        if not name_group_comparable_with_tolerence(new_group, group1, group2, name_instance_dict, id_name_dict, name_statistics):
            continue
        else:
            new_group = tuple(sorted(new_group))
        if group1 in new_group_set:
            new_group_set.remove(group1)
        if group2 in new_group_set:
            new_group_set.remove(group2)
        new_group_set.add(new_group)

    for author_id in conflict_ids:
        new_group = authors_duplicates_dict[author_id]
        for group in new_group_set:
            if author_id in group:
                new_group = group
        for id in authors_duplicates_dict[author_id]:
            if id not in new_group and author_id in authors_duplicates_dict[id]:
                authors_duplicates_dict[id].remove(author_id)
        authors_duplicates_dict[author_id] = set(new_group)

    for author_id in authors_duplicates_dict.iterkeys():
        if author_id in authors_duplicates_dict[author_id]:
            authors_duplicates_dict[author_id].remove(author_id)

