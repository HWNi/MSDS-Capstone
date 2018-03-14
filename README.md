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
* [sklearn](http://scikit-learn.org/stable/install.html)
* [scipy](https://www.scipy.org/install.html)
* [fuzzy](https://pypi.python.org/pypi/Fuzzy)

### How to run
After you install the necessary packages, you need to create a folder named *data* in the root and put all the input 
data sets in this folder. Then, you can start the program by running main.py. After an entire iteration of algorithm, 
you can open cal_precision.ipynb to check the performance. In addition, all the results of disambiguation will be saved 
as csv in the *result* folder. 


## Datasets Overview
