#
# update_paper_using_galpy.py: Script to semi-automate updating a paper in the
#                              JSON file containing papers using galpy.
#
#                              Run as python update_paper_using_galpy.py [paper_id]
#
import sys
import os, os.path
import re
import json
import ads
from add_paper_using_galpy import (_PAPERS_FILE_DIR, _JOURNAL_ABBREV,
                                   build_internal_id,
                                   build_and_edit_new_entry,
                                   pretty_print_new_entry)

def update_paper_using_galpy(paper_id=None,debug=False):
    abort_msg= 'aborting' if debug else 'skipping'
    with open(os.path.join(_PAPERS_FILE_DIR,'papers-using-galpy.json'),'r') as jsonFile:
        papers_data= json.load(jsonFile)
    # Find the existing entry
    current_entry= papers_data[paper_id]
    if not current_entry['pages'] == '':
        print(f"Paper seems to have been published already, {abort_msg} ...")
        return None
    # Find paper on ADS, using arxiv ID
    if 'arxiv' in current_entry['url']:
        arxiv_id= current_entry['url'].split('/')[-1]    
    else:    
        print(f"Cowardly refusing to update a paper without arXiv ID, {abort_msg} ...")
        return None
    if True:
        ads_paper= list(ads.SearchQuery(arxiv=arxiv_id,
                            fl=['author','title','year',
                            'pub','volume','page']))[0]
    else:
        # Mock up
        class ads_paper_example():
            def __init__(self):
                self.author= ['Richings, Jack', 'Frenk, Carlos', 'Jenkins, Adrian', 'Robertson, Andrew', 'Fattahi, Azadeh', 'Grand, Robert J. J.', 'Navarro, Julio', 'Pakmor, Rüdiger', 'Gomez, Facundo A.', 'Marinacci, Federico', 'Oman, Kyle A.']
                self.title= ['Subhalo destruction in the APOSTLE and AURIGA simulations']
                self.year= '2020'
                self.pub= 'Monthly Notices of the Royal Astronomical Society'
                self.volume= '492'
                self.page= ['5780']
        ads_paper= ads_paper_example()
    if ads_paper.page is None or ads_paper.page[0].startswith('arXiv'):
        if debug:
            print("Paper does not seem to have been published yet, here's the ADS search result")
            print(ads_paper.author)
            print(ads_paper.title)
            print(ads_paper.year)
            print(ads_paper.pub)
            print(ads_paper.volume)
            print(ads_paper.page)
            print("Aborting ...")
        else:
            print("Paper does not seem to have been published yet, skipping ...")
        return None
    # Create new entry
    new_entry= build_and_edit_new_entry(ads_paper,paper_id,arxiv_id)
    print("Updating entry {}".format(arxiv_id))
    num_lines= sum(1 for line in open(os.path.join(_PAPERS_FILE_DIR,'papers-using-galpy.json')))
    with open(os.path.join(_PAPERS_FILE_DIR,'papers-using-galpy.json'),'r') as jsonFile:
        contents= jsonFile.readlines()
    # Find and delete current entry
    line_no= [line == '  "{}": {{\n'.format(paper_id) for line in contents].index(True)
    for ii in range(10):
        contents.pop(line_no)
    # Insert new entry
    pretty_print_new_entry(arxiv_id,paper_id,new_entry,
                            print_func=lambda x: contents.insert(line_no+10-num_lines,x+'\n'))
    with open(os.path.join(_PAPERS_FILE_DIR,'papers-using-galpy.json'),'w') as jsonFile:
        jsonFile.writelines(contents)
    return None

def update_papers_using_galpy():
    # Try to update all papers that weren't published yet
    with open(os.path.join(_PAPERS_FILE_DIR,'papers-using-galpy.json'),'r') as jsonFile:
        papers_data= json.load(jsonFile)
    ids_2_update= [papers_data[entry]['pages'] == '' for entry in papers_data]
    for paper_id, (ii, bl) in zip(papers_data.keys(),enumerate(ids_2_update)):
        if bl and not paper_id == '_template':
            print(f"Working on {paper_id} ...")
            update_paper_using_galpy(paper_id)
    return None

if __name__ == '__main__':
    if len(sys.argv) > 1:
        update_paper_using_galpy(sys.argv[1],debug=True)
    else:
        update_papers_using_galpy()