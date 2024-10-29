#
# add_papers_using_galpy_from_cites.py: Script to find potential papers that use galpy
#                                       based on citations in ADS to the galpy paper
#
#                                       Run as python add_papers_using_galpy_from_cites.py [min_year] [max_year]
#
#                                       When min_year is set, but max_year is not, max_year is set to min_year.
#                                       When neither min_year nor max_year are set, min_year is set to 2010 and max_year to 2100.
#
import sys
import os
import os.path
import urllib.parse
import re
import json
import subprocess
import numpy
import ads

_GALPY_PAPER_BIBCODE = "2015ApJS..216...29B"

def find_potential_papers(min_year,max_year):
    if True:
        papers= ads.SearchQuery(q=f"citations({_GALPY_PAPER_BIBCODE}) year:{min_year}-{max_year}",
                                fl=['bibcode','identifier','alternate_bibcode'],
                                rows=1_000,max_pages=10)
    else:
        # Mock up for tests
        class ads_paper_example():
            def __init__(self,n=0):
                if n == 0:
                    self.bibcode= "2016MNRAS.463..102E"
                    self.alternate_bibcode= ['2016MNRAS.tmp.1078E', '2016arXiv160604946E']
                    self.identifier= ['10.48550/arXiv.1606.04946',
                                      '10.1093/mnras/stw1957',
                                      '2016arXiv160604946E',
                                      '2016MNRAS.463..102E',
                                      'arXiv:1606.04946',
                                      '2016MNRAS.tmp.1078E']
                elif n == 1:
                    self.bibcode= "2016ApJ...833...31B"
                    self.alternate_bibcode= ['2016arXiv160901298B']
                    self.identifier= ['arXiv:1609.01298',
                                      '2016arXiv160901298B',
                                      '10.48550/arXiv.1609.01298',
                                      '2016ApJ...833...31B',
                                      '10.3847/1538-4357/833/1/31']
                elif n == 2:
                    self.bibcode= "2024PhRvL.132j1403D"
                    self.alternate_bibcode= ['2022arXiv221209751D']
                    self.identifier= ['10.1103/PhysRevLett.132.101403',
                                      'arXiv:2212.09751',
                                      '10.48550/arXiv.2212.09751',
                                      '2022arXiv221209751D',
                                      '2024PhRvL.132j1403D']
        papers= [ads_paper_example(n=0),ads_paper_example(n=1),ads_paper_example(n=2)]
    # Prune the ones we already have, either as using galpy or as citing galpy but not using it
    with open(os.path.join('..','src','data','papers-using-galpy.json'),'r') as f:
        papers_using_galpy_data= json.load(f)
    with open('papers-citing-but-not-using-galpy.json','r') as f:
        papers_citing_but_not_using_galpy_data= json.load(f)
    potential_papers = []
    for paper in papers:
        # First add arxiv_id to the paper
        arxiv_id= None
        for identifier in paper.identifier:
            if identifier.startswith('arXiv:'):
                arxiv_id= re.match(r'.*arXiv:(.*)',identifier).group(1)
                break
        if arxiv_id is None:
            print(f"WARNING: Could not find arXiv id for {paper.bibcode}")
        paper.arxiv_id= arxiv_id
        # First check whether the paper cites galpy but doesn't use it
        if paper.bibcode in papers_citing_but_not_using_galpy_data \
            or ( 
                paper.alternate_bibcode is not None and 
                 numpy.any([alt_bibcode in papers_citing_but_not_using_galpy_data 
                            for alt_bibcode in paper.alternate_bibcode])
            ):
            continue
        # Then check whether the paper is already in the file of papers using galpy using
        # either the ADS URL or the arXiv URL
        if numpy.any([papers_using_galpy_data[p]['url'].startswith(f'http://adsabs.harvard.edu/abs/{urllib.parse.quote_plus(paper.bibcode)}')
                            for p in papers_using_galpy_data.keys()]):
                continue
        if numpy.any([papers_using_galpy_data[p]['url'].startswith(f'http://ui.adsabs.harvard.edu/abs/{urllib.parse.quote_plus(paper.bibcode)}')
                            for p in papers_using_galpy_data.keys()]):
                continue
        if paper.arxiv_id is not None:
            if numpy.any([papers_using_galpy_data[p]['url'] == f'https://arxiv.org/abs/{paper.arxiv_id}'
                            for p in papers_using_galpy_data.keys()]):
                continue
            if numpy.any([papers_using_galpy_data[p]['url'] == f'http://arxiv.org/abs/{paper.arxiv_id}'
                            for p in papers_using_galpy_data.keys()]):
                continue
        # If we get here, we have a potential paper
        potential_papers.append(paper)
    return potential_papers

def check_and_add_potential_paper(paper,no_arxiv_id=False):
    if no_arxiv_id:
        print(f"Processing {paper.bibcode} without arxiv id")
    else:
        print(f"Processing {paper.bibcode} with arxiv id {paper.arxiv_id}")
    # Open the paper in the browser
    if no_arxiv_id:
        os.system(f"open https://ui.adsabs.harvard.edu/abs/{urllib.parse.quote_plus(paper.bibcode)}")
    else:
        os.system(f"open https://arxiv.org/pdf/{paper.arxiv_id}")
    add_paper = input("Add paper? [y/N] ")
    add_paper= add_paper.lower() == 'y'
    # If we want to add the paper, call add_paper_using_galpy.py with the arxiv ID / bibcode
    if add_paper:
        try:
            subprocess.check_call(['python', 'add_paper_using_galpy.py', paper.bibcode if no_arxiv_id else paper.arxiv_id ])
        except subprocess.CalledProcessError:
            raise RuntimeError(f"Adding paper {paper.bibcode} with arxiv id {paper.arxiv_id} failed")
    else:
        add_paper_to_papers_citing_but_not_using_galpy = input("Add paper to papers-citing-but-not-using-galpy.json? [Y/n] ")
        add_paper_to_papers_citing_but_not_using_galpy= add_paper_to_papers_citing_but_not_using_galpy.lower() != 'n'
        if add_paper_to_papers_citing_but_not_using_galpy:
            with open('papers-citing-but-not-using-galpy.json','r') as f:
                papers_citing_but_not_using_galpy_data= json.load(f)
            papers_citing_but_not_using_galpy_data.append(paper.bibcode)
            with open('papers-citing-but-not-using-galpy.json','w') as f:
                json.dump(papers_citing_but_not_using_galpy_data,f,indent=2)
    return None

def check_paper_no_arxivid(paper):
    print(f"Processing {paper.bibcode} without arxiv id")
    # Open the paper in the browser
    os.system(f"open https://ui.adsabs.harvard.edu/abs/{urllib.parse.quote_plus(paper.bibcode)}")
    add_arxiv_id = input("Add arXiv ID? [y/N] ")
    add_arxiv_id= add_arxiv_id.lower() == 'y'
    if add_arxiv_id:
        paper.arxiv_id= input("Enter arXiv ID: ")
        check_and_add_potential_paper(paper)
    else:
        add_paper_to_papers_citing_but_not_using_galpy = input("Add paper to papers-citing-but-not-using-galpy.json? [Y/n] ")
        add_paper_to_papers_citing_but_not_using_galpy= add_paper_to_papers_citing_but_not_using_galpy.lower() != 'n'
        if add_paper_to_papers_citing_but_not_using_galpy:
            with open('papers-citing-but-not-using-galpy.json','r') as f:
                papers_citing_but_not_using_galpy_data= json.load(f)
            papers_citing_but_not_using_galpy_data.append(paper.bibcode)
            with open('papers-citing-but-not-using-galpy.json','w') as f:
                json.dump(papers_citing_but_not_using_galpy_data,f,indent=2)
    return None

if __name__ == '__main__':
    min_year= int(sys.argv[1] if len(sys.argv) > 1 else 2010)
    max_year= int(sys.argv[2] if len(sys.argv) > 2 else (min_year if len(sys.argv) > 1 else 2100))
    potential_papers = find_potential_papers(min_year,max_year)
    print(f"\033[1mFound {len(potential_papers)} potential papers\033[0m")
    # Keep a list of papers with no arxiv ID so we can mention them for manual processing
    papers_without_arxiv_id = []
    for ii, paper in enumerate(potential_papers):
        if paper.arxiv_id is None:
            papers_without_arxiv_id.append(paper)
            continue
        check_and_add_potential_paper(paper)
        print(f"\033[1m{len(potential_papers)-ii-1} papers left to process\033[0m")
    if len(papers_without_arxiv_id) > 0:
        print(f"\033[1mFound {len(papers_without_arxiv_id)} potential papers without arxiv ID\033[0m")
        for paper in papers_without_arxiv_id:
            check_and_add_potential_paper(paper,no_arxiv_id=True)