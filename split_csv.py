import csv,requests,json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def get_metadata(doi):
    headers = {"accept": "application/x-bibtex"}
    title, year, journal = '', '', ''
    sessions = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    sessions.mount('http://', adapter)
    sessions.mount('https://', adapter)

    try:
        response = requests.get("http://dx.doi.org/" + doi, headers=headers)
    except requests.exceptions.ConnectionError:
        print "ConnectionError"
        return title, year, journal

    if (response.status_code != 200):
        print 'Did not find '+doi+' article, error code '+str(response.status_code)
    else:
        try:
            line = response.text.encode()
            line = line.split('\n\t')
            line = line[1:]
        except UnicodeEncodeError:
            print "UnicodeEncodeError"
            return title, year, journal

        for field in line:
            if len(field) >= 8 and field[0:6] == "year =":
                year = field[7:-1]
            if len(field) >= 9 and field[0:7] == "title =":
                title = field[9:-2]
            if len(field) >= 11 and field[0:9] == "journal =":
                journal = field[11:-3]
    return title, year, journal


def split_csv():
    author_fn = 'data/Author.csv'
    paper_fn = 'data/Paper.csv'
    paper_author_fn = 'data/PaperAuthor.csv'

    with open("data/authorinfo.csv") as data_file:
        f_author = open(author_fn, 'w')
        f_paper = open(paper_fn, 'w')
        f_paper_author = open(paper_author_fn,'w')

        f_author.write('author_id,surname,given_name,email,affiliation\n')
        f_paper.write('pmid,pmcid,doi,title,year,pulication\n')
        f_paper_author.write('pmid,author_id,surname,given_name \n')

        data_reader = csv.reader(data_file, delimiter='\t')
        next(data_reader)
        counter = 0

        for row in data_reader:
            if len(row) < 8 or row[1] == 'None':
                continue

            author = str(counter)+','+row[3]+','+row[4]+','+row[6]+','+row[7]
            paper_author= row[1] + ',' +str(counter)+','+row[3]+','+row[4]
            f_author.write(author+'\n')
            f_paper_author.write(paper_author + '\n')

            doi = row[2]
            if counter < 1000:
                title, year, journal = get_metadata(doi)
            else:
                title, year, journal = '', '', ''
            paper = row[1] + ',' + row[0] + ',' + row[2]+','+title+ ',' +year+ ',' +journal
            f_paper.write(paper + '\n')
            counter += 1


split_csv()