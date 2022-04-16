#
# add_paper_using_galpy.py: Script to semi-automate adding a paper to the
#                           JSON file containing papers using galpy.
#
#                           Run as python add_paper_using_galpy.py [arxiv_id]
#
import sys
import os, os.path
import shutil
import glob
import re
import json
import numpy
import ads

_PAPERS_FILE_DIR= os.path.join('..','src','data')
_ALPHABET= 'abcdefghijklmnopqrstuvwxyz'
_JOURNAL_ABBREV= {'Monthly Notices of the Royal Astronomical Society': 'Mon. Not. Roy.Astron. Soc.',
                  'The Astrophysical Journal': 'Astrophys. J.',
                  'The Astrophysical Journal Supplement Series': 'Astrophys. J. Supp.',
                  'The Astronomical Journal': 'Astron. J.',
                  'Astronomy and Astrophysics': 'Astron. & Astrophys.',
                  "arXiv e-prints": ""}

def parse_author(author):
    last, first= author.split(',')
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

def pretty_print_new_entry(arxiv_id,internal_id,entry,
                           print_func=print):
    print_func('  "{}": {{'.format(internal_id))
    print_func('    "author": "{}",'.format(entry['author']))
    print_func('    "title": "{}",'.format(entry['title']))
    print_func('    "year": "{}",'.format(entry['year']))
    print_func('    "journal": "{}",'.format(entry['journal']))
    print_func('    "volume": "{}",'.format(entry['volume']))
    print_func('    "pages": "{}",'.format(entry['pages']))
    print_func('    "url": "https://arxiv.org/abs/{}",'.format(arxiv_id))
    print_func('    "img": "{}.png"'.format(internal_id.lower()))
    print_func('  },')
    return None

def add_paper_using_galpy(arxiv_id):
    # Read current file
    with open(os.path.join(_PAPERS_FILE_DIR,'papers-using-galpy.json'),'r') as jsonFile:
        papers_data= json.load(jsonFile)
    duplicate= numpy.any([papers_data[p]['url'] == 'https://arxiv.org/abs/{}'.format(arxiv_id)
                          for p in papers_data.keys()])
    if duplicate:
        print("This appears to be a duplicate of an existing entry:")
        dup_indx= [papers_data[p]['url'] == 'https://arxiv.org/abs/{}'.format(arxiv_id)
                   for p in papers_data.keys()].index(True)
        print(json.dumps(papers_data[list(papers_data.keys())[dup_indx]],
                         indent=4,separators=(',', ': ')).replace('\\n','\n'))
        cont= input("Continue? [y/N] ")
        cont= cont.lower() == 'y'
        if not cont: 
            print("Okay, aborting then...")
            return None
    # Find paper on ADS
    if True:
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
    # Build identifier
    internal_id= ads_paper.author[0].split(',')[0]+ads_paper.year[-2:]
    internal_id= re.sub('[^A-Za-z0-9]+', '',internal_id) # remove special char
    for letter in _ALPHABET:
        if not internal_id+letter in papers_data.keys():
            internal_id+= letter
            break
    new_entry= {'author': parse_authors(ads_paper.author),
                'title': ads_paper.title[0],
                'year': ads_paper.year,
                'journal': parse_journal(ads_paper.pub),
                'volume': ads_paper.volume if not ads_paper.volume is None else "",
                'pages': ads_paper.page[0] if not ads_paper.page[0].startswith('arXiv') else ""}
    pretty_print_new_entry(arxiv_id,internal_id,new_entry)
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
                pretty_print_new_entry(arxiv_id,internal_id,new_entry)
                looks_good= input('Looks good? [Y/n] ')
                looks_good= looks_good == '' or looks_good.lower() == 'y'
                if looks_good: break
        else:
            print("Okay, aborting then...")
            return None
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
        return None
    # Find the Screenshot file and move it
    possible_screenshots= glob.glob(os.path.join(_PAPERS_FILE_DIR,'paper-figs','Screen Shot*'))
    if len(possible_screenshots) > 1:
        print("Found multiple possible screen shots... aborting ...")
        return None
    shutil.move(possible_screenshots[0],
                os.path.join(_PAPERS_FILE_DIR,'paper-figs','{}.png'.format(internal_id.lower())))
    print("Moved file to {}".format(os.path.join('paper-figs','{}.png'.format(internal_id.lower()))))
    num_lines= sum(1 for line in open(os.path.join(_PAPERS_FILE_DIR,'papers-using-galpy.json')))
    with open(os.path.join(_PAPERS_FILE_DIR,'papers-using-galpy.json'),'r+') as jsonFile:
        contents= jsonFile.readlines()
        pretty_print_new_entry(arxiv_id,internal_id,new_entry,
                               print_func=lambda x: contents.insert(-11,x+'\n'))
        jsonFile.seek(0)
        jsonFile.writelines(contents)
    print("Success!")
    return None
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        arxiv_id= input("Please provide an arxiv identifier: ")
    else:
        arxiv_id= sys.argv[1]
    add_paper_using_galpy(arxiv_id)