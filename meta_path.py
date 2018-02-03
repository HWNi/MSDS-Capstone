from sklearn.preprocessing import normalize
from custom_setting import *
from name import *
from difflib import SequenceMatcher
import re
import fuzzy

normalized_feature_dict = {}
soundex = fuzzy.Soundex(4)

