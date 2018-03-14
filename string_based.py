import fuzzy
from difflib import SequenceMatcher
from name import *

soundex = fuzzy.Soundex(4)

def add_similar_ids_under_name(name_instance_dict, id_name_dict):
    # Find similar id for each name in name_instance_dict.
    print "\tBuilding virtual names."
    virtual_name_set = set()
    for (author_name, name_instance) in name_instance_dict.iteritems():
        alternatives = name_instance.get_alternatives()
        for alternative in alternatives:
            if alternative not in name_instance_dict:
                virtual_name_set.add(alternative)

    for virtual_author_name in virtual_name_set:
        new_name_instance = Name(virtual_author_name)
        name_instance_dict[virtual_author_name] = new_name_instance

    print "\tAdding similar author ids into each name instance."
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            alternatives = name_instance.alternatives
            for alternative in alternatives:
                # Add author_ids into the similar_author_ids of the name's alternative.
                for id in name_instance.author_ids:
                    name_instance_dict[alternative].add_similar_author_id(id)
                # Add alternative's author_ids into the similar_author_ids of the current name.
                for id in name_instance_dict[alternative].author_ids:
                    name_instance_dict[author_name].add_similar_author_id(id)

    reduced_name_pool = {}
    print "\tBuilding reduced_name dict."
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            elements = sorted(author_name.split())
            reduced_name = ''.join(elements)
            reduced_name_pool.setdefault(reduced_name, set()).add(author_name)

    print "\tAdding similar ids for the same reduced_names."
    for (author_name1, name_instance1) in name_instance_dict.iteritems():
        if author_name1 not in virtual_name_set:
            # name = "b a" -> split -> ['b', 'a'] -> sorted -> ['a', 'b']
            elements = sorted(author_name1.split())
            reduced_name = ''.join(elements)
            pool = reduced_name_pool[reduced_name]
            for author_name2 in pool:
                name_instance2 = name_instance_dict[author_name2]
                for id in name_instance1.author_ids:
                    name_instance2.add_similar_author_id(id)
                for id in name_instance2.author_ids:
                    name_instance1.add_similar_author_id(id)

    sorted_name_pool = {}
    print "\tBuilding sorted name dict."
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            elements = author_name.split()
            sorted_name = ''.join(elements)
            sorted_name_pool.setdefault(sorted_name, set()).add(author_name)

    print "\tAdding similar ids for the same sorted_names."
    for (author_name1, name_instance1) in name_instance_dict.iteritems():
        if author_name1 not in virtual_name_set:
            elements = author_name1.split()
            sorted_name = ''.join(elements)
            pool = sorted_name_pool[sorted_name]
            for author_name2 in pool:
                if author_name1 < author_name2:
                    name_instance2 = name_instance_dict[author_name2]
                    for id in name_instance1.author_ids:
                        name_instance2.add_similar_author_id(id)
                    for id in name_instance2.author_ids:
                        name_instance1.add_similar_author_id(id)

    name_unit_pool = {}
    print "\tBuilding name unit dict."
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            if len(author_name) < 10:
                continue
            elements = name_instance.name.split()
            for element in elements:
                name_unit_pool.setdefault(element, set()).add(author_name)

    name_finger_dict = {}
    for (author_name, name_instance) in name_instance_dict.iteritems():
        name_finger_dict[author_name] = ''.join(sorted(author_name.split()))

    print "\tAdding similar ids for the same name units."
    for (author_name1, name_instance1) in name_instance_dict.iteritems():
        if author_name1 not in virtual_name_set:
            if len(author_name1) < 10:
                continue
            elements = name_instance1.name.split()
            for element in elements:
                pool = name_unit_pool[element]
                for author_name2 in pool:
                    if author_name1 < author_name2:
                        if author_name1.find(author_name2) >= 0 or author_name2.find(author_name1) >= 0:
                            if abs(len(author_name1) - len(author_name2)) <= 3 and len(author_name1) >= 8 and len(author_name2) >= 8 or\
                                    len(author_name1) > 15 and len(author_name2) > 15:
                                name_instance2 = name_instance_dict[author_name2]
                                for id in name_instance1.author_ids:
                                    name_instance2.add_similar_author_id(id)
                                for id in name_instance2.author_ids:
                                    name_instance1.add_similar_author_id(id)

    init_full_dict = {}
    full_init_dict = {}
    initlen_full_dict = {}
    print "\tBuilding name initials mapping."
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            initials = ''
            if name_instance.first_name != '':
                initials += name_instance.first_name[0]
            if name_instance.middle_name != '':
                initials += name_instance.middle_name[0]
            if name_instance.last_name != '':
                initials += name_instance.last_name[0]
            init_full_dict.setdefault(initials, set()).add(author_name)
            full_init_dict[author_name] = initials
            initlen_full_dict.setdefault((initials, len(author_name)), set()).add(author_name)

    print "\tStart noisy last name comparison:"
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            pool = init_full_dict[full_init_dict[author_name]]
            for candidate in pool:
                if author_name[:-1] == candidate:
                    name_instance_candidate = name_instance_dict[candidate]
                    for id in name_instance.author_ids:
                        name_instance_candidate.add_similar_author_id(id)
                    for id in name_instance_candidate.author_ids:
                        name_instance.add_similar_author_id(id)

    print "\tStart question marks or non askii name comparison:"
    for (author_id, author_name_list) in id_name_dict.iteritems():
        if not all(ord(char) < 128 for char in author_name_list[1]) or author_name_list[1].find('?') >= 0:
            name_instance_dict[author_name_list[0]].bad_name_flag = True
            pool = init_full_dict[full_init_dict[author_name_list[0]]]
            for candidate in pool:
                if SequenceMatcher(None, author_name_list[0], candidate).ratio() >= 0.90 or SequenceMatcher(None, author_name_list[1], candidate).ratio() >= 0.90:
                    name_instance_candidate = name_instance_dict[candidate]
                    for id in name_instance_dict[author_name_list[0]].author_ids:
                        name_instance_candidate.add_similar_author_id(id)
                    for id in name_instance_candidate.author_ids:
                        name_instance_dict[author_name_list[0]].add_similar_author_id(id)

    print "\tStart arbitrary name comparison:"
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if author_name not in virtual_name_set:
            name_length = len(author_name)
            for area in range(-3, 4):
                if name_length + area > 0 and (full_init_dict[author_name], name_length + area) in initlen_full_dict:
                    pool = initlen_full_dict[(full_init_dict[author_name], name_length + area)]
                    for candidate in pool:
                        if SequenceMatcher(None, author_name, candidate).ratio() >= 0.90:
                            name_instance_candidate = name_instance_dict[candidate]
                            for id in name_instance_dict[author_name].author_ids:
                                name_instance_candidate.add_similar_author_id(id)
                            for id in name_instance_candidate.author_ids:
                                name_instance_dict[author_name].add_similar_author_id(id)

    print "\tStart nicknames comparison:"
    for (author_name, name_instance) in name_instance_dict.iteritems():
        if name_instance.first_name in nickname_dict:
            for nickname in nickname_dict[name_instance.first_name]:
                s = ' '.join([nickname, name_instance.middle_name, name_instance.last_name]).strip()
                new_name = ' '.join(s.split())
                if new_name in name_instance_dict:
                    for id in name_instance_dict[new_name].author_ids:
                        name_instance.add_similar_author_id(id)
                    for id in name_instance.author_ids:
                        name_instance_dict[new_name].add_similar_author_id(id)


def create_potential_duplicate_groups(name_instance_dict):
    """
    Create potential duplicate groups for local clustering algorithm to analyse.

    Parameters:
        name_instance_dict:
            A dictionary with key: author's name string and value:
            name instance. Note that the author's name is clean after
            initialization of the Name class.

    Returns:
        A set containing lots of tuples describing the potential duplicate group.
    """
    groups = set()
    for (author_name, name_instance) in name_instance_dict.iteritems():
        group = name_instance.author_ids.union(name_instance.similar_author_ids)
        for id1 in group:
            for id2 in group:
                if id1 < id2:
                    groups.add(tuple([id1, id2]))
    return groups


def single_name_comparable(name_instance__a, name_instance__b, name_statistics):
    # Decide whether two name instances are comparable
    name__a = name_instance__a.name
    name__b = name_instance__b.name

    if name_instance__a.is_asian and name_instance__b.is_asian:
        # Han Liu and Huan Liu
        if name_instance__a.middle_name == '' and name_instance__b.middle_name == '':
            if len(name_instance__a.first_name) > 1 and len(name_instance__b.first_name) > 1:
                if name_instance__a.first_name != name_instance__b.first_name:
                    return False
        # Han Liu  and H. L. Liu
        if len(name_instance__a.first_name) == 1 and len(name_instance__a.middle_name) == 1:
            if not is_substr(name__a.replace(' ', ''), name__b):
                return False
        if len(name_instance__b.first_name) == 1 and len(name_instance__b.middle_name) == 1:
            if not is_substr(name__a, name__b.replace(' ', '')):
                return False
        # Lin Yu, Lin Yi
        if name_instance__a.last_name != name_instance__b.last_name:
            return False

    if name__b.find(name__a.replace(' ', '')) >= 0 or name__a.find(name__b.replace(' ', '')) >= 0:
        return True

    index = max(name__b.find(name__a), name__a.find(name__b))
    if index >= 0:
        string1 = max(name__a, name__b, key=len)
        string2 = min(name__a, name__b, key=len)
        if index > 0:
            if string1[index - 1] == ' ':
                return True
        else:
            if (index + len(string2)) <= len(string1) - 1:
                if string1[index + len(string2)] == ' ' or string1[index + len(string2):] == 'and' \
                        or string1[index + len(string2):] == 'yz' or string1[index + len(string2):] == 't' \
                        or string1[index + len(string2):] == 'z':
                    return True

    if name__a.replace(' ', '') == name__b.replace(' ', ''):
        return True

    score = my_string_match_score(name_instance__a.name, name_instance__b.name, name_statistics, name_instance__a.is_asian or name_instance__b.is_asian)
    if score <= 1:
        return False

    if score >= 100:
        return True
    if (name_instance__a.first_name, name_instance__b.first_name) not in nickname_set \
            and (name_instance__a.first_name, name_instance__b.first_name) not in nickname_initials_set:
        if not is_substr(name_instance__a.initials, name_instance__b.initials):
            return False
    else:
        if not is_substr(name_instance__a.initials[1:], name_instance__b.initials[1:]):
            return False

    # Chris Ding and Cui Ding
    if len(name_instance__a.first_name) > 1 and len(name_instance__b.first_name) > 1:
        if name_instance__a.first_name[0] == name_instance__b.first_name[0]:
            if (name_instance__a.first_name, name_instance__b.first_name) not in nickname_set:
                if (name_instance__a.first_name.find(name_instance__b.first_name) < 0 and name_instance__a.first_name.find(name_instance__b.first_name) < 0) \
                        or (name_instance__a.middle_name == '' and name_instance__b.middle_name == ''):
                    if not name_instance__a.bad_name_flag and not name_instance__b.bad_name_flag:
                        first_name_1 = name_instance__a.first_name.lower()
                        first_name_2 = name_instance__b.first_name.lower()
                        if name_instance__a.middle_name == name_instance__b.first_name or name_instance__b.middle_name == name_instance__a.first_name:
                            pass
                        elif name_instance__a.is_asian or name_instance__b.is_asian:
                            if SequenceMatcher(None, name_instance__a.first_name[1:], name_instance__b.first_name[1:]).ratio() < 0.93:
                                return False
                        else:
                            ldis = SequenceMatcher(None, name_instance__a.first_name[1:], name_instance__b.first_name[1:]).ratio()
                            if ldis < 0.93 and\
                                    (ldis < 0.80 or soundex(first_name_1) != soundex(first_name_2)):
                                return False
                    else:
                        if SequenceMatcher(None, name_instance__a.first_name[1:], name_instance__b.first_name[1:]).ratio() < 0.5:
                            return False

    # Michael Ia Jordan and Michael Ib jordan
    if len(name_instance__a.middle_name) > 1 and len(name_instance__b.middle_name) > 1:
        if name_instance__a.middle_name[0] == name_instance__b.middle_name[0]:
            if not is_substr(name_instance__a.middle_name.replace(' ', ''), name_instance__b.middle_name.replace(' ', '')):
                if SequenceMatcher(None, name_instance__a.middle_name[1:], name_instance__b.middle_name[1:]).ratio() <= 0.3:
                    return False

    # Michael Jordan and John Mohammed Jordan
    if name_instance__a.first_name[0] != name_instance__b.first_name[0] and (name_instance__a.first_name, name_instance__b.first_name) not in nickname_initials_set:
        if len(name_instance__b.middle_name) > 0:
            if name_instance__a.first_name[0] == name_instance__b.middle_name[0]:
                if len(name_instance__a.first_name) > 1 and len(name_instance__b.middle_name) > 1:
                    if my_string_match_score(name_instance__a.first_name, name_instance__b.middle_name, name_statistics) == 0:
                        return False
            else:
                if my_string_match_score(name_instance__a.name + ' ' + name_instance__a.middle_name,
                                         name_instance__b.first_name + ' ' + name_instance__b.first_name,
                                         name_statistics) == 0:
                    return False
        if len(name_instance__a.middle_name) > 0:
            if name_instance__b.first_name[0] == name_instance__a.middle_name[0]:
                if len(name_instance__b.first_name) > 1 and len(name_instance__a.middle_name) > 1:
                    if my_string_match_score(name_instance__a.middle_name, name_instance__b.first_name, name_statistics) == 0:
                        return False
            else:
                if my_string_match_score(name_instance__a.name + ' ' + name_instance__a.middle_name,
                                         name_instance__b.first_name + ' ' + name_instance__b.first_name,
                                         name_statistics) == 0:
                    return False

    if name_instance__a.last_name != name_instance__b.last_name:
        if SequenceMatcher(None, name_instance__a.last_name[1:], name_instance__b.last_name[1:]).ratio() <= 0.7:
            return False
        if SequenceMatcher(None, name_instance__a.last_name, name_instance__b.last_name).ratio() <= 0.7:
            return False

    return True


def my_string_match_score(s1, s2, name_statistics, is_asian=False):
    # Give a score for similarity between s1 and s2
    elements_s1 = s1.split()
    elements_s2 = s2.split()
    if len(elements_s1) > len(elements_s2):
        elements_s1 = s2.split()
        elements_s2 = s1.split()
    count = 0
    rare_count = 0
    full_score = len(elements_s1)
    for element1 in elements_s1:
        flag = False
        candi = ""
        for element2 in elements_s2:
            if len(element1) != 1 and len(element2) != 1:
                if element2 != element1:
                    if element2 in element1:
                        idx = elements_s2.index(element2)
                        if len(elements_s2) > idx + 1:
                            if element2 + elements_s2[idx + 1] == element1 \
                                    or (SequenceMatcher(None, element1, element2 + elements_s2[idx + 1]).ratio() >= 0.9
                                        and len(element2) >= 3 and len(elements_s2[idx + 1]) >= 3) \
                                    or (element1, element2 + elements_s2[idx + 1]) in nickname_set:
                                count += 2
                                elements_s2.remove(elements_s2[idx + 1])
                                elements_s2.remove(element2)
                                break
                        if idx >= 1:
                            if elements_s2[idx - 1] + element2 == element1 \
                                    or (SequenceMatcher(None, element1, elements_s2[idx - 1] + element2).ratio() >= 0.9
                                        and len(element2) >= 3 and len(elements_s2[idx - 1]) >= 3) \
                                    or (element1, elements_s2[idx - 1] + element2) in nickname_set:
                                count += 3
                                elements_s2.remove(elements_s2[idx - 1])
                                elements_s2.remove(element2)
                                break
                    elif element1 in element2:
                        idx = elements_s1.index(element1)
                        if len(elements_s1) > idx + 1:
                            if element1 + elements_s1[idx + 1] == element2 \
                                    or (SequenceMatcher(None, element2, element1 + elements_s1[idx + 1]).ratio() >= 0.9
                                        and len(element1) >= 3 and len(elements_s1[idx + 1]) >= 3) \
                                    or (element2, element1 + elements_s1[idx + 1]) in nickname_set:
                                count += 3
                                elements_s2.remove(element2)
                                elements_s1.remove(elements_s1[idx + 1])
                                break
                        if idx >= 1:
                            if elements_s1[idx - 1] + element1 == element2 \
                                    or (SequenceMatcher(None, element1, elements_s1[idx - 1] + element1).ratio() >= 0.9
                                        and len(element1) >= 3 and len(elements_s1[idx - 1]) >= 3) \
                                    or (element2, elements_s1[idx - 1] + element1) in nickname_set:
                                count += 3
                                elements_s2.remove(element2)
                                elements_s1.remove(elements_s1[idx - 1])
                                break
                if is_asian:
                    if SequenceMatcher(None, element1, element2).ratio() > 0.90:
                        if element1 == element2 and element1 in name_statistics and (name_statistics[element1] <= 10 or name_statistics[element2] <= 10):
                            count += 1
                            rare_count += 1
                        else:
                            count += 1
                        if flag is True:
                            flag = False
                        elements_s2.remove(element2)
                        break
                else:
                    tmp1 = element1.lower()
                    tmp2 = element2.lower()
                    ldis = SequenceMatcher(None, tmp1, tmp2).ratio()
                    try:
                        if ldis > 0.88 or \
                                (ldis > 0.80 and abs(int(soundex(tmp1)[1:]) - int(soundex(tmp2)[1:])) <= 2):
                            if tmp1 == tmp2 and tmp1 in name_statistics and (
                                    name_statistics[element1] <= 10 or name_statistics[element2] <= 10):
                                count += 1
                                rare_count += 1
                            else:
                                count += 1
                            if flag is True:
                                flag = False
                            elements_s2.remove(element2)
                            break
                    except ValueError:
                        pass

            if (element1, element2) in nickname_set:
                count += 1
                elements_s2.remove(element2)
                break
            if element1 == '' or element2 == '':
                continue
            if len(element1) == 1 and len(element2) == 1 and element1 == element2:
                count += 1
                elements_s2.remove(element2)
                break
            if (element1, element2) in nickname_initials_set:
                flag = True
                candi = element2
                continue
            if element1[0] != element2[0]:
                continue
            if len(element1) == 1 and len(element2) == 1:
                count += 1
                elements_s2.remove(element2)
                break
            if len(element1) == 1 and len(element2) != 1:
                if flag is True:
                    continue
                flag = True
                candi = element2
            if len(element1) != 1 and len(element2) == 1:
                if flag is True:
                    continue
                flag = True
                candi = element2
        else:
            if flag is True:
                count += 0.49
                elements_s2.remove(candi)
                continue
            count -= 0.26
    elements_s1 = s1.split(" ")
    elements_s2 = s2.split(" ")

    # Specific operations on noisy last names.
    if elements_s1[-1] != elements_s2[-1]:
        if is_asian:
            if SequenceMatcher(None, elements_s1[-1], elements_s2[-1]).ratio() <= 0.90:
                if elements_s1[-1][:-1] == elements_s2[-1][:-1] \
                        or elements_s1[-1][:-1] == elements_s2[-1] \
                        or elements_s1[-1] == elements_s2[-1][:-1]:
                    count += 1.5
        else:
            element1 = elements_s1[-1].lower()
            element2 = elements_s2[-1].lower()
            ldis = SequenceMatcher(None, element1, element2).ratio()
            if ldis <= 0.85 and \
                    (ldis <= 0.80 or abs(int(soundex(element1)[1:]) - int(soundex(element2)[1:])) > 2):
                if elements_s1[-1][:-1] == elements_s2[-1][:-1] \
                        or elements_s1[-1][:-1] == elements_s2[-1] \
                        or elements_s1[-1] == elements_s2[-1][:-1]:
                    count += 1.5

    if count == full_score or count >= 4 or rare_count >= 2:
        return 100
    return count


def is_substr(s1, s2):
    # return whether srtring s1 appear in string in s2
    return bool(re.search(".*".join(s1), s2)) or bool(re.search(".*".join(s2), s1))


def __name_comparable(name_instance_a, name_instance_b, name_statistics, strict_mode=True):
    # Decide whether two name instances are comparable considering name reordering, not symmetric
    if single_name_comparable(name_instance_a, name_instance_b, name_statistics):
        return True

    name__a = '- '.join([name_instance_a.last_name, name_instance_a.middle_name, name_instance_a.first_name]).strip()
    new_name_instance__a = Name(name__a)
    new_name_instance__a.is_asian = name_instance_a.is_asian
    if single_name_comparable(new_name_instance__a, name_instance_b, name_statistics):
        return True

    name__a = '- '.join([name_instance_a.middle_name, name_instance_a.last_name, name_instance_a.first_name]).strip()
    new_name_instance__a = Name(name__a)
    new_name_instance__a.is_asian = name_instance_a.is_asian
    if single_name_comparable(new_name_instance__a, name_instance_b, name_statistics):
        return True

    name__a = '- '.join([name_instance_a.last_name, name_instance_a.first_name, name_instance_a.middle_name]).strip()
    new_name_instance__a = Name(name__a)
    new_name_instance__a.is_asian = name_instance_a.is_asian
    if single_name_comparable(new_name_instance__a, name_instance_b, name_statistics):
        return True

    name__a = '- '.join([name_instance_a.middle_name, name_instance_a.first_name, name_instance_a.last_name]).strip()
    new_name_instance__a = Name(name__a)
    new_name_instance__a.is_asian = name_instance_a.is_asian
    if strict_mode:
        if new_name_instance__a.name == name_instance_b.name:
            return True
    else:
        if single_name_comparable(new_name_instance__a, name_instance_b, name_statistics):
            return True

    name__a = '- '.join([name_instance_a.first_name, name_instance_a.last_name, name_instance_a.middle_name]).strip()
    new_name_instance__a = Name(name__a)
    new_name_instance__a.is_asian = name_instance_a.is_asian
    if single_name_comparable(new_name_instance__a, name_instance_b, name_statistics):
        return True

    return False


def name_comparable(name_instance_a, name_instance__b, name_statistics, strict_mode=True):
    # Decide whether two name instances are comparable considering name reordering, symmetric
    return __name_comparable(name_instance_a, name_instance__b, name_statistics, strict_mode) \
           or __name_comparable(name_instance__b, name_instance_a, name_statistics, strict_mode)
