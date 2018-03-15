# UW MSDS-Capstone: Name Entity Disambiguation
  
## Project Introduction
### What is name entity ambiguity?
  
Name entity ambiguity is a problem that occurs when a set of named entities stored in
the digital libraries such as author names of publications, patient names of medical records,
author names of patents and etc. are same or similar. Several reasons could cause the ambiguity problem: 
1. Misspelling when the text data is manually entered into the database
2. Name homography
3. Different rules and conventions of writing names, such as using middle names or initials
4. Name changes due to special reasons such as marriage. 

### Why do we study this?

Name entity ambiguity reduces the quality and reliability of the information retrieved from database. The consequence of
entity ambiguity could lead to unpredictable negative impact and confusion to who consume the information. Therefore name 
entity disambiguation is a critical task in digital libraries.

There is a large number of outstanding research results on name entity disambiguation in the current NLP literature, 
but not all of the solutions are generalizable. So our goal of this project is to construct a disambiguation model that 
can handle various domains of name entities.


## Getting Started
### Hardware requirement  
We suggest to run all the code on a PC with at least 16GB memory. 

### Software requirement
You will need Python 2.7.X and Jupyter notebook installed to reproduce this project. 
To install Python 2, see [download](https://www.python.org/downloads/) and [beginner's guide](https://www.python.org/about/gettingstarted/)
To install Jupyter Notebook, follow the [installation](http://jupyter.readthedocs.io/en/latest/install.html).

Addtionally, you will need following Python packages:
* [numpy](http://www.numpy.org/)
* [pandas](https://pandas.pydata.org/)
* [scipy](https://www.scipy.org/install.html)
* [sklearn](http://scikit-learn.org/stable/install.html)
* [fuzzy](https://pypi.python.org/pypi/Fuzzy)

### How to run
After you install the above necessary packages, you need to create a folder called *data* in the root folder and put all the input 
datasets (which will be explained in the next section) into this folder. Then, you can start the program by running 
*main.py*. After an entire iteration of the algorithm, the results of disambiguation will be saved as a csv file in the *result* folder. In addition, the performance of algorithm will be printed as acerage precision, recall and F1-score.

## Datasets Overview
### Input Data Structure
Our project followed the dataset configuration of [KDD Cup 2013 - Author Disambiguation Challenge (Track 2)](https://www.kaggle.com/c/kdd-cup-2013-author-disambiguation).
There are 3 key datasets that will be considered in our algorithm:

1. Author.csv  
This dataset contains author IDs, author names, and affiliation of authors. The same author can appear more 
than once in the dataset under different author IDs, for instance the author publishes under different versions of his/her name, such as 
J. Doe, Jane Doe, and J. A. Doe.

2. Paper.csv  
This dataset contains descriptions of papers. Descriptions include title, year of publication, conference, journal, and etc.

3. PaperAuthor.csv  
This dataset connects the author and paper dataset with (paper ID, author ID) pairs.

### Data Source
* [PubMed Baseline Data](https://drive.google.com/drive/folders/1VKfJJqTHUXBYUDY1Lpldp8shPHC0eXUW)
PubMed is an open database of life sciences and biomedical publications and articles. It is produced by The United States National Library of Medicine.<br />
The original PubMed baseline data are stored as XML format. We created a script to transform the data from XML to 
CSV and prepared the dataset according to the format described above.
  
* [AMiner](https://drive.google.com/drive/folders/1bx6YbxUGK1OX1yqx5oS4BV2UW-WeOBRp)
AMiner is a searchable online database provides comprehensive search and mining services for researcher social networks. It is created by professor Jie Tang from Tsinghua University, China. It was first launched in March 2006. Arnetminer also published several datasets for academic research purpose, including the Name Disambiguation dataset we used in the project.


## Conclusion
The name entity disambiguation algorithm we built could potentially be applied to domains beyond the ones studied in the project. This is because we utilized features beyond the characteristics specific to name entities. The first part of our algorithm implements a string-based name matching method to find all potential duplicates; the second part calculates a network-based similarity 
score to narrow down the results. 

During the development of the second part, we also tried some natural language processing techniques such as using
tf-idf to perform disambiguation of features used in the algorithm, for example, affiliation. However, the effect of that strategy didn't
make a huge improvement to the final result.

### Challenges
Our project initially intended to develop a model based on an existing solution and then improve the scalability using parallel computation. However, we did not have enough time to finish the scaling due to the below challenges we met during our investigation:

* Lack of labels and low-quality labels <br/>
Lack of training data with labels was a big bottle neck for us at the beginning. We explored both approaches of manual 
labeling and finding a labeled dataset. We were able to find a labeled dataset, AMiner, at the end. However, the quality of the label is under doubt. We found several records potentially wrong. 


* Disambiguation problem of features <br/>
Features used in the modeling process, like affiliation and conference, are ambiguous and potentially duplicate. 
The features themselves are disambiguation problems and need to be processed and disambiguated first. 

### Future work
Future work of our project includes improve model performance(accuracy and recall of disambiguation) and improve model efficiency. Name disambiguation, or record linkage, is a field under active research and with wide applications. Due to the time limit and scope of the project, we just explored one of the possible methods. The authors hope to continue working on the area in the future studies.


## Project Poster
![Project Poster](https://github.com/HWNi/MSDS-Capstone/blob/master/result/poster.png)

## Reference
Liu, Jialu, et al. "Ranking-based name matching for author disambiguation in bibliographic data.
" Proceedings of the 2013 KDD Cup 2013 Workshop. ACM, 2013.

Sinha, Arnab, et al. "An overview of microsoft academic service (mas) and applications.
" Proceedings of the 24th international conference on world wide web. ACM, 2015.

Tang, Jie, et al. "Arnetminer: extraction and mining of academic social networks." Proceedings of the 14th ACM SIGKDD international conference on Knowledge discovery and data mining. ACM, 2008.

## Acknowledgement
The authors’ sincere gratitude to the adviser and sponsor of the project, Jevin West in the Information School at the University of Washington; special thanks to the instructor of the capstone class, Megan Hazen and all staff members who make the project possible, Deborah Alterman and Gary Winchester.







