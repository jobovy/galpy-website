#
# add_paper_using_galpy.py: Script to semi-automate adding a paper to the
#                           JSON file containing papers using galpy.
#
#                           Run as python add_paper_using_galpy.py [arxiv_id]
#
#                           Note that arxiv_id can also be an ADS bibcode
#
import sys
import os, os.path
import urllib.parse
import shutil
import glob
import re
import json
import numpy
import ads

_PAPERS_FILE_DIR= os.path.join('..','src','data')
_ALPHABET= 'abcdefghijklmnopqrstuvwxyz'
_JOURNAL_ABBREV= {'Monthly Notices of the Royal Astronomical Society': 'Mon. Not. Roy. Astron. Soc.',
                  'The Astrophysical Journal': 'Astrophys. J.',
                  'The Astrophysical Journal Supplement Series': 'Astrophys. J. Supp.',
                  'The Astronomical Journal': 'Astron. J.',
                  'Astronomy and Astrophysics': 'Astron. & Astrophys.',
                  'Research in Astronomy and Astrophysics': 'Res. Astron. Astrophys.',
                  'Physical Review D': 'Phys. Rev. D',
                  'Journal of Astrophysics and Astronomy': 'J. Astrophys. Astron.',
                  "arXiv e-prints": ""}

def build_internal_id(ads_paper,papers_data):
    # Build identifier
    internal_id= ads_paper.author[0].split(',')[0]+ads_paper.year[-2:]
    internal_id= re.sub('[^A-Za-z0-9]+', '',internal_id) # remove special char
    for letter in _ALPHABET:
        if internal_id+letter not in papers_data.keys():
            internal_id+= letter
            break
    return internal_id

def parse_author(author):
    try:
        last, first= author.split(',')
    except ValueError:
        # Probably no first name
        return author
    else:
        return '{} {}'.format(first.strip(),last.strip())

def parse_authors(authors):
    if len(authors) == 1:
        return parse_author(authors[0])
    out= ''
    cnt= 0
    for author in authors:
        if cnt > 4:
            out+= 'et al.'
            break
        else:
            if cnt == len(authors)-1:
                out+= '& '
            out+= parse_author(author)
            if cnt < len(authors)-1 and not len(authors) == 2:
                out+= ', '
            elif cnt < len(authors)-1:
                out+= ' '
        cnt+= 1
    return out

def parse_journal(pub):
    return _JOURNAL_ABBREV.get(pub,pub)

def build_and_edit_new_entry(ads_paper,internal_id,arxiv_id,id_is_bibcode):
    new_entry= {'author': parse_authors(ads_paper.author),
                'title': ads_paper.title[0],
                'year': ads_paper.year,
                'journal': parse_journal(ads_paper.pub),
                'volume': ads_paper.volume if ads_paper.volume is not None else "",
                'pages': ads_paper.page[0] if not ads_paper.page[0].startswith('arXiv') else ""}
    pretty_print_new_entry(arxiv_id,internal_id,new_entry,id_is_bibcode)
    write_output= input('Looks good? [Y/n] ')
    write_output= write_output == '' or write_output.lower() == 'y'
    if not write_output:
        edit= input('Do you want to edit the new entry? [y/N] ')
        edit= edit.lower() == 'y'
        if edit:
            while True:
                entry_to_edit= input('Which field do you want to edit? ')
                entry_edit= input('What do you want to field to say? ')
                new_entry[entry_to_edit]= entry_edit
                print('Okay, new entry is ')
                pretty_print_new_entry(arxiv_id,internal_id,new_entry,id_is_bibcode)
                looks_good= input('Looks good? [Y/n] ')
                looks_good= looks_good == '' or looks_good.lower() == 'y'
                if looks_good: break
        else:
            print("Okay, aborting then...")
            sys.exit(-1)
    return new_entry

def pretty_print_new_entry(arxiv_id,internal_id,entry,id_is_bibcode,
                           print_func=print):
    print_func('  "{}": {{'.format(internal_id))
    print_func('    "author": "{}",'.format(entry['author']))
    print_func('    "title": "{}",'.format(entry['title']))
    print_func('    "year": "{}",'.format(entry['year']))
    print_func('    "journal": "{}",'.format(entry['journal']))
    print_func('    "volume": "{}",'.format(entry['volume']))
    print_func('    "pages": "{}",'.format(entry['pages']))
    print_func('    "url": "{}",'.format(f"http://ui.adsabs.harvard.edu/abs/{urllib.parse.quote_plus(arxiv_id)}" 
                                         if id_is_bibcode else f"https://arxiv.org/abs/{arxiv_id}"))
    print_func('    "img": "{}.png"'.format(internal_id.lower()))
    print_func('  },')
    return None

def add_paper_using_galpy(arxiv_id):
    # Check whether we've been given an arxiv id or a bibcode
    id_is_bibcode = len(arxiv_id) == 19
    # Read current file and check for duplicates using possible URLs
    with open(os.path.join(_PAPERS_FILE_DIR,'papers-using-galpy.json'),'r') as jsonFile:
        papers_data= json.load(jsonFile)
    duplicate= numpy.any([papers_data[p]['url'] == f'https://arxiv.org/abs/{arxiv_id}'
                            for p in papers_data.keys()])
    duplicate+= numpy.any([papers_data[p]['url'] == f'http://arxiv.org/abs/{arxiv_id}'
                            for p in papers_data.keys()])
    duplicate+= numpy.any([papers_data[p]['url'] == f'http://adsabs.harvard.edu/abs/{urllib.parse.quote_plus(arxiv_id)}'
                            for p in papers_data.keys()])
    duplicate+= numpy.any([papers_data[p]['url'] == f'http://ui.adsabs.harvard.edu/abs/{urllib.parse.quote_plus(arxiv_id)}'
                            for p in papers_data.keys()])
    if duplicate:
        print("This appears to be a duplicate of an existing entry, aborting...")
        sys.exit(-1)
    # Find paper on ADS
    if id_is_bibcode:
        ads_paper= list(ads.SearchQuery(bibcode=arxiv_id,
                                        fl=['author','title','year',
                                            'pub','volume','page']))[0]
    elif True:
        ads_paper= list(ads.SearchQuery(arxiv=arxiv_id,
                                        fl=['author','title','year',
                                            'pub','volume','page']))[0]
    else:
        # Mock up
        class ads_paper_example():
            def __init__(self):
                self.author= ['Qian, Yansong', 'Arshad, Yumna', 'Bovy, Jo']
                self.title= ['The structure of accreted stellar streams']
                self.year= '2022'
                self.pub= 'Monthly Notices of the Royal Astronomical Society'
                self.volume= '511'
                self.page= ['2339']
        ads_paper= ads_paper_example()
    internal_id= build_internal_id(ads_paper,papers_data)
    new_entry= build_and_edit_new_entry(ads_paper,internal_id,arxiv_id,id_is_bibcode)
    print("Adding entry {}".format(arxiv_id))
    # Move the screenshot in the right place
    done= input("""Now please take a screen shot of an example figure 
  and place it in the paper-figs directory. Just take 
  it with the standard Mac Screenshot app and have it 
  be saved to that directory. I'll do the rest! 
  Please press enter when done, any other input will 
  lead me to abort the operation! """)
    if not done == '':
        print("Okay, aborting then...")
        sys.exit(-1)
    # Find the Screenshot file and move it
    possible_screenshots= glob.glob(os.path.join(_PAPERS_FILE_DIR,'paper-figs','Screenshot*'))
    if len(possible_screenshots) > 1:
        print("Found multiple possible screen shots... aborting ...")
        sys.exit(-1)
    shutil.move(possible_screenshots[0],
                os.path.join(_PAPERS_FILE_DIR,'paper-figs','{}.png'.format(internal_id.lower())))
    print("Moved file to {}".format(os.path.join('paper-figs','{}.png'.format(internal_id.lower()))))
    num_lines= sum(1 for line in open(os.path.join(_PAPERS_FILE_DIR,'papers-using-galpy.json')))
    with open(os.path.join(_PAPERS_FILE_DIR,'papers-using-galpy.json'),'r+') as jsonFile:
        contents= jsonFile.readlines()
        pretty_print_new_entry(arxiv_id,internal_id,new_entry,id_is_bibcode,
                               print_func=lambda x: contents.insert(-11,x+'\n'))
        jsonFile.seek(0)
        jsonFile.writelines(contents)
    print("Success!")
    return None
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        arxiv_id= input("Please provide an arxiv identifier or an ADS bibcode: ")
    else:
        arxiv_id= sys.argv[1]
    add_paper_using_galpy(arxiv_id)