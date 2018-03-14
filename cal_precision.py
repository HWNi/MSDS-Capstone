# Calculte model performance, including precision, recall, and F-1 score of the model.


import pickle
import pandas as pd
import numpy as np

model_output = pickle.load(open("data/authors_duplicates_dict_seal", "rb"))
label_data = pd.read_csv('data/label_data.csv')
label_data['authorId'] = label_data.index + 1

label_dict = {}
for i in xrange(label_data.shape[0]):
    line = label_data[i:i+1]
    personID  = int(line['personID'])
    label = int(line['label'])
    authorId = int(line['authorId'])
    if personID in label_dict: 
        if label in label_dict[personID]:
            label_dict[personID][label].add(authorId)
        else:                
            label_dict[personID][label]= {authorId}
    else:
        label_dict[personID] = {label:{authorId}}


label_per_authorId = {}
for i in xrange(label_data.shape[0]):
    line = label_data[i:i+1]
    personID  = int(line['personID'])
    label = int(line['label'])
    authorId = int(line['authorId'])
    label_per_authorId[authorId] =  label_dict[personID][label]    


# key: authoId, value:[precision, recall, f1_score]
p_r_f1 = {}
for key in model_output.keys():
    if key in label_per_authorId.keys():
        same_id = model_output[key].intersection(label_per_authorId[key])
        model_output_id = model_output[key]
        label_id = label_per_authorId[key]
        if len(model_output_id) == 0:
            p = 0
        else:
            p = 1.0*len(same_id)/len(model_output_id)
        if len(label_id) == 0:
            r = 0
        else:
            r = 1.0*len(same_id)/len(label_id)
        if p+r == 0:
            f1 = 0
        else:
            f1 = 2.0*p*r/(p+r)
        p_r_f1[key] = [p,r,f1]


precision = np.mean([val[0] for val in p_r_f1.values()])
print "precision:", precision
recall = np.mean([val[1] for val in p_r_f1.values()])
print "recall:", recall
f1 = np.mean([val[2] for val in p_r_f1.values()])
print "f1 score:", f1






