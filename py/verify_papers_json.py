# verify_papers_json.py: verify that JSON structure of 
# the file holding the papers using galpy
import sys
import os
import os.path
import json
import urllib.request, urllib.error
import warnings
import tqdm
import random

def verify_one_entry(entry,name,export_arxiv=False):
    """Verify a single entry
    entry: full entry dictionary
    name: name of the entry"""
    # Basic structure
    assert 'author' in entry
    assert 'title' in entry
    assert 'year' in entry
    assert 'journal' in entry
    assert 'volume' in entry
    assert 'pages' in entry
    assert 'url' in entry
    if not 'img' in entry:
        warnings.warn(f'Missing image for entry {name}')
    if name == '_template': return None
    # Test whether the URL exists
    try:
        urllib.request.urlopen(entry['url'].replace('arxiv','export.arxiv') if export_arxiv
                               else entry['url'])
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"'HTTPError 429: Too many requests.' received for URL {entry['url']}; skipping ...")
    except:
        raise AssertionError(f"URL {entry['url']} does not seem to exist ...")
    # Test whether the image is present if the img attribute is given
    if 'img' in entry and \
       not os.path.exists(os.path.join('..','src','data',
                                       'paper-figs',entry['img'])):
        raise AssertionError("Paper image does not appear to exist at {} ..."\
                                 .format(os.path.join('data','paper-figs',entry['img'])))
    return None

if __name__ == '__main__':
    # Function to check for duplicate keys (https://stackoverflow.com/a/16172132/10195320)
    def dupe_checking_hook(pairs):
        result = dict()
        for key,val in pairs:
            if key in result:
                raise KeyError(f"Duplicate key specified: {key}")
            result[key] = val
        return result
    # Read the JSON file
    with open('../src/data/papers-using-galpy.json','r') as jsonfile:
        data= json.load(jsonfile,object_pairs_hook=dupe_checking_hook)
    print(f"Papers file contains {len(data)-1} publications")
    if len(sys.argv) > 1 and sys.argv[1] == 'count':
        sys.exit(0)
    # Randomize the order of keys and verify each entry
    for key in tqdm.tqdm(random.sample(list(data),len(data))):
        verify_one_entry(data[key],key)
    
