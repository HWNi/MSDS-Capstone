
# coding: utf-8

# In[1]:


import xml.etree.cElementTree as et
import pandas as pd


# In[2]:


parsed_xml = et.parse("pubmedsample18n0001.xml")


# In[3]:


"""
<PubmedArticleSet>
    <PubmedArticle>
        <MedlineCitation Status="MEDLINE" Owner="NLM">
            ...
        </MedlineCitation>
        <PubmedData>
            <History>
            </History>
            <PublicationStatus>ppublish</PublicationStatus>
            <ArticleIdList>
            </ArticleIdList>
        </PubmedData>
            ...
        <MedlineCitation Status="MEDLINE" Owner="NLM">
            ...
        </MedlineCitation>
        <PubmedData>
        </PubmedData>
            ...
        <MedlineCitation Status="MEDLINE" Owner="NLM">
            ...
        </MedlineCitation>
        <PubmedData>
        </PubmedData>
            ...
    </PubmedArticle>
</PubmedArticleSet>
"""

root = parsed_xml.getroot()
medline_citation_tag = set()
pubmed_data_tag = set()

for i, child in enumerate(root):
    for subchild in child:
        if subchild.tag == "MedlineCitation":
            for sub_subchild in subchild:
                medline_citation_tag.add(sub_subchild.tag)
        elif subchild.tag == "PubmedData":
            for sub_subchild in subchild:
                pubmed_data_tag.add(sub_subchild.tag)

print("MedlineCitation: ", len(medline_citation_tag))
print(medline_citation_tag)
print("-------------------------------------------------------------------------------------------------")
print("pubmed_data_tag: ", len(pubmed_data_tag))
print(pubmed_data_tag)


# ### Demo 1

# In[4]:


for i, element in enumerate(root.iter("MedlineCitation")):
    for child in element:
        print(child.tag)
        for sub_child in child:
            print("\t", sub_child.tag)
            for sub_sub_child in sub_child:
                print("\t\t", sub_sub_child.tag)


# ### Demo 2

# In[ ]:


pmid = []
article_title = []
for i, element in enumerate(root.iter("MedlineCitation")):
    for child in element:
        if child.tag == "Article":
            for sub_child in child.iter('ArticleTitle'):
                print(i, sub_child.text)


# ### Demo 3

# In[ ]:


medline_citation = []
pubmed_data = []

for i, child in enumerate(root):
    #record = {}
    for subchild in child:
        if subchild.tag == "MedlineCitation":
            medline_citation.append(subchild)
        elif subchild.tag == "PubmedData":
            pubmed_data.append(subchild)
                
                
print(len(medline_citation))
print(len(pubmed_data))


# ### ArticleTitle

# In[7]:


titles_list = []
for i, element in enumerate(root.iter("MedlineCitation")):
    for child in element:
        if child.tag == "Article":
            for sub_child in child.iter('ArticleTitle'):
                titles_list.append((i, sub_child.text))


# ### PMID

# In[56]:


pmid_list = []
for element in root.iter('MedlineCitation'):
    pmid_list.append(element.find('PMID').text)
    
print(len(pmid_list))


# ### Author List

# In[8]:


"""
<AuthorList CompleteYN="Y">
  <Author ValidYN="Y">
    <LastName>Bose</LastName>
    <ForeName>K S</ForeName>
    <Initials>KS</Initials>
  </Author>
  <Author ValidYN="Y">
    <LastName>Sarma</LastName>
    <ForeName>R H</ForeName>
    <Initials>RH</Initials>
  </Author>
</AuthorList>
"""

name_set = set()

for element in root.iter("AuthorList"):
    for author in element.find('Author'):
        name_set.add(author.tag)

print(name_set)


# ### Author

# In[ ]:


LastName = []
ForeName = []
Initials = []
AffiliationInfo = []
Identifier = []
CollectiveName = []
for i, element in enumerate(root.iter("AuthorList")):
    for child in element:
        for sub_child in child:
            if sub_child.tag == "LastName":
                LastName.append((i, sub_child.text))
            elif sub_child.tag == "ForeName":
                ForeName.append((i, ForeName.text))
            elif sub_child.tag == "Initials":
                Initials.append((i, Initials.text))
            elif sub_child.tag == "AffiliationInfo":
                print(AffiliationInfo[])


# ### Language

# In[13]:


lang_list = []

for i, element in enumerate(root.iter("MedlineCitation")):
    for child in element:
        if child.tag == "Article":
            for sub_child in child.iter('Language'):
                lang_list.append((i, sub_child.text))


# ### Process List

# In[82]:


def process_list():
    output_list = [None]*177
    return output_list

process_list()


# ### KeywordList

# In[21]:


keyword_list = []
for i, element in enumerate(root.iter("MedlineCitation")):
    for child in element:
        if child.tag == "KeywordList":
            for sub_child in child.iter('Keyword'):
                keyword_list.append((i, sub_child.text))
len(keyword_list)


# In[78]:


for index, keyword in keyword_list:
    print(index, keyword)


# ### AbstractText

# In[44]:


abstract_text_list = []
for i, element in enumerate(root.iter("MedlineCitation")):
    for child in element:
        if child.tag == 'Article':
            for sub_child in child.iter('Abstract'):
                abstract_text_list.append((i, sub_child.find('AbstractText').text))

len(abstract_text_list)


# ### AffliationInfo

# In[53]:


affiliation_info_list = []
for i, element in enumerate(root.iter("MedlineCitation")):
    for child in element:
        if child.tag == 'Article':
            for sub_child in child.iter('AffiliationInfo'):
                affiliation_info_list.append((i, sub_child.find('Affiliation').text))
                
affiliation_info_list


# ### Parsing Name

# In[76]:


author_list = []
for i, element in enumerate(root.iter("MedlineCitation")):
    for child in element:
        if child.tag == 'Article':
            for sub_child in child.iter("Author"):
                # 'AffiliationInfo', 'Initials', 'ForeName', 'CollectiveName', 'Identifier', 'LastName'
#                 last_name = sub_child.find('LastName').text
#                 fore_name = sub_child.find('ForeName').text
#                 initials = sub_child.find('Initials').text
#                 affiliation_info = sub_child.find('AffiliationInfo').text
#                 identifier = sub_child.find('Identifier').text
#                 print(i, last_name, fore_name, initials, affiliation_info, identifier)
                for ele in sub_child.getchildren():
                    if ele.tag != "AffiliationInfo":
                        print(i, ele.tag, ele.text)
                    else:
                        print(i, ele.tag, ele.find('Affiliation').text)

