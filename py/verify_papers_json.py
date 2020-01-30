# verify_papers_json.py: verify that JSON structure of 
# the file holding the papers using galpy
import os, os.path
import json
import urllib.request

def verify_one_entry(entry,name):
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
    assert 'img' in entry
    if name == '_template': return None
    # Test whether the URL exists
    try:
        urllib.request.urlopen(entry['url'])
    except:
        raise AssertionError("URL {} does not seem to exist ...".format(entry['url']))
    # Test whether the image is present
    if not os.path.exists(os.path.join('..','src','data','paper-figs',entry['img'])):
        raise AssertionError("Paper image does not appear to exist at {} ..."\
                                 .format(os.path.join('data','paper-figs',entry['img'])))
    return None

if __name__ == '__main__':
    with open('../src/data/papers-using-galpy.json','r') as jsonfile:
        data= json.load(jsonfile)
    for key in data:
        verify_one_entry(data[key],key)
    
