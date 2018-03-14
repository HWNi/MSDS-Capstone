# UW MSDS-Capstone: Name Entity Disambiguation
## Project Poster
![Project Poster](https://github.com/HWNi/MSDS-Capstone/blob/master/result/poster.png)
  
## About the Project
### What is name entity ambiguity?
  
Name entity ambiguity is a problem that occurs when a set of named entities stored in
the digital libraries such as author names of publications, patient names of medical records,
author names of patents and etc. are same or similar. Several reasons causing name entity ambiguity: 
1. Misspelling when the text data were manually entered into the database
2. Name homography
3. Different rules and conventions of writing names such as using middle names
4. Name changes due to special reason such as marriage. 

### Why do we study this?

Name entity ambiguity reduces the quality and reliability of information retrieved from database, and the consequence of
entity ambiguity could lead to unpredictable negative impact and damage to who consume information. Therefore, name 
entity disambiguation is a critical task in digital libraries.

There is a large number of outstanding research results for named entity disambiguation in the current NLP literature, 
but not all of the solutions are generalizable. So our goal of this project is to construct a disambiguation model that 
can handle various domain of name entities.


## Getting Started
### Hardware requirement  
We suggest to run all the code on a PC with at least 16GB memory. 

### Software requirement
You will need Python 2.7.X and Jupyter notebook installed to reproduce this project. 
To install Python 2, see [download](https://www.python.org/downloads/) and [beginner's guide](https://www.python.org/about/gettingstarted/)
To install Jupyter Notebook, follow [installation](http://jupyter.readthedocs.io/en/latest/install.html)

Addtionally, you will need following Python packages:
* [numpy](http://www.numpy.org/)
* [pandas](https://pandas.pydata.org/)
* [scipy](https://www.scipy.org/install.html)
* [sklearn](http://scikit-learn.org/stable/install.html)
* [fuzzy](https://pypi.python.org/pypi/Fuzzy)

### How to run
After you install the necessary packages, you need to create a folder named *data* in the root folder and put all the input 
data sets (which will be introduced in the next section) in this folder. Then, you can start the program by running 
*main.py*. After an entire iteration of algorithm, the performance of algorithm will be displayed through precision, 
recall and F1-score in average. In addition, all the results of disambiguation will be saved as csv in the *result* 
folder. 

## Datasets Overview
### Input Data Structure
Our project followed the dataset configuration of [KDD Cup 2013 - Author Disambiguation Challenge (Track 2)](https://www.kaggle.com/c/kdd-cup-2013-author-disambiguation).
There are 3 key datasets that will be considered in our algorithm:

1. Author.csv  
This dataset contains author IDs, author names and affiliation of authors. The same author can appear more 
than once in this dataset, for instance because he/she publishes under different versions of his/her name, such as 
J. Doe, Jane Doe, and J. A. Doe.

2. Paper.csv  
This dataset contains descriptions of papers. Descriptions include title, year of publication, conference, journal, and etc.

3. PaperAuthor.csv  
This dataset connects the author and paper dataset with (paper ID, author ID) pairs.

### Data source
* [PubMed Baseline Data](ftp://ftp.ncbi.nlm.nih.gov/pubmed/)
PubMed is an open database of life sciences and biomedical publications and articles. 
It is produced by The United States National Library of Medicine.

The original PubMed baseline data are stored in XML format, so we created a script to do the transformation from XML to 
CSV and prepare the data according to the structure introduced above.
  
* [Aminer](https://aminer.org/disambiguation)


## Conclusion
The name disambiguation algorithm we built could potentially be applied to different domain beyond the ones used in the 
project. This is because we utilized some features other than the name entities themselves. The first part of our algorithm
implements a string-based name matching to find all potential duplicates; the second part uses a network-based similarity 
score to narrow down. 

During the development of the second part, we also tried some natural language processing techniques such as using
tf-idf to perform some simple disambiguation to one of the features, affiliation. However, the effect of that strategy didn't
make a huge change to the final result.

Our project initially intended to replicate an existing solution for name entity disambiguation and then parallelize the 
solution. However, we did not have enough time to finish the scaling due to several challenges we met during our investigation:
* Lack of labels and low-quality labels  

Lack of training data with labels was a big bottle neck for us at the beginning. We explored both approaches of manual 
labeling and find a label dataset. The dataset we used at the end is under the coder of unconfident labels.

* Disambiguation problem of features 
Features used in the modeling process, like affiliation and conference, are ambiguous and potentially duplicate. 
The features need to be processed and disambiguated first. 

## Reference
Liu, Jialu, et al. "Ranking-based name matching for author disambiguation in bibliographic data.
" Proceedings of the 2013 KDD Cup 2013 Workshop. ACM, 2013.

Sinha, Arnab, et al. "An overview of microsoft academic service (mas) and applications.
" Proceedings of the 24th international conference on world wide web. ACM, 2015.

## Acknowledgement
The authors’ sincere gratitude to the adviser and sponsor of the project, Jevin West in the Information School at the University of Washington; special thanks to the instructor of the capstone class, Megan Hazen and all staff members who make the
project possible, Deborah Alterman and Gary Winchester.







