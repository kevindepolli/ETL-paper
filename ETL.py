from time import sleep
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
url = 'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=simulated+annealing&oq=simulated'


# this function for the getting information of the web page
def get_paperinfo(paper_url):

    # download the page
    response = requests.get(paper_url, headers=headers)

    # check successful response
    if response.status_code != 200:
        print('Status code:', response.status_code)
        raise Exception('Failed to fetch web page ')

    # parse using beautiful soup
    paper_doc = BeautifulSoup(response.text, 'html.parser')

    return paper_doc


# this function for the extracting information of the tags
def get_tags(doc):
    paper_tag = doc.select('[data-lid]')
    cite_tag = doc.select('a[href*="cites="]')
    link_tag = doc.find_all('h3', {"class": "gs_rt"})
    author_tag = doc.find_all("div", {"class": "gs_a"})

    return paper_tag, cite_tag, link_tag, author_tag


# it will return the title of the paper
def get_papertitle(paper_tag):

    paper_names = []

    for tag in paper_tag:
        paper_names.append(tag.select('h3')[0].get_text())

    return paper_names


# it will return the number of citation of the paper
def get_citecount(cite_tag):
    cite_count = []
    for i in cite_tag:
        cite = i.text
        if i is None or cite is None:  # if paper has no citatation then consider 0
            cite_count.append(0)
        else:
            tmp = re.search(r'\d+', cite) # its handle the None type object error and re use to remove the string " cited by " and return only integer value
            if tmp is None :
                cite_count.append(0)
            else :
                cite_count.append(int(tmp.group()))

    return cite_count

# function for the getting link information
def get_link(link_tag):

    links = []

    for i in range(len(link_tag)) :
        links.append(link_tag[i].a['href'])

    return links


# function for the getting autho , year and publication information
def get_author_year_publi_info(authors_tag):
    years = []
    publication = []
    authors = []
    for i in range(len(authors_tag)):
        authortag_text = (authors_tag[i].text).split()
        year = int(re.search(r'\d+', authors_tag[i].text).group())
        years.append(year)
        publication.append(authortag_text[-1])
        author = authortag_text[0] + ' ' + re.sub(',','', authortag_text[1])
        authors.append(author)

    return years , publication, authors


# creating final repository
paper_repos_dict = {
    'Paper Title' : [],
    'Year' : [],
    'Author' : [],
    'Citation' : [],
    'Publication' : [],
    'Url of paper' : [] }


# adding information in repository
def add_in_paper_repo(papername, year, author, cite, publi, link):
    paper_repos_dict['Paper Title'].extend(papername)
    paper_repos_dict['Year'].extend(year)
    paper_repos_dict['Author'].extend(author)
    paper_repos_dict['Citation'].extend(cite)
    paper_repos_dict['Publication'].extend(publi)
    paper_repos_dict['Url of paper'].extend(link)

    return pd.DataFrame(paper_repos_dict)


global final


for i in range(0, 110, 10):

    # get url for the each page
    url = "https://scholar.google.com/scholar?start={}&q=object+detection+in+aerial+image+&hl=en&as_sdt=0,5".format(i)

    # function for the get content of each page
    doc = get_paperinfo(url)

    # function for the collecting tags
    paper_tag,cite_tag,link_tag,author_tag = get_tags(doc)

    # paper title from each page
    papername = get_papertitle(paper_tag)

    # year , author , publication of the paper
    year, publication, author = get_author_year_publi_info(author_tag)

    # cite count of the paper
    cite = get_citecount(cite_tag)

    # url of the paper
    link = get_link(link_tag)

    # add in paper repo dict
    try:
        if len(papername) == len(year) == len(author) == len(cite) == len(publication) == len(link):
            final = add_in_paper_repo(papername, year, author, cite, publication, link)
        else:
            print(f"Length mismatch at iteration {i}:")
            print(f"papername: {len(papername)}, year: {len(year)}, author: {len(author)}, cite: {len(cite)}, publication: {len(publication)}, link: {len(link)}")
    except Exception as e:
        print(f"Error at iteration {i}: {e}")

    print('Resultado na ', i, 'iteração:\n', final)
    # use sleep to avoid status code 429
    sleep(30)

print('Resultado final:\n', final[:10])
final.to_csv('simulated_annealing_researchpapers.csv', sep=',', index=False, header=True)