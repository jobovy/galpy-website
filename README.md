# galpy-website

galpy's website

![Update website](https://github.com/jobovy/galpy-website/workflows/Update%20website/badge.svg)

## Adding papers to the ``papers-using-galpy.json`` file

To easily and quickly add papers using galpy to the ``papers-using-galpy.json`` file, run the utility
```
python add_paper_using_galpy.py
```
in the ``py/`` directory. This will ask for an arXiv ID and create a new entry from there.

To even more easily add papers, you can also run
```
python add_papers_using_galpy_from_cites.py
```
in the ``py/`` directory. This first searches for papers that cite galpy on ADS and cross-checks it against the
``papers-using-galpy.json`` file to see whether the paper is already listed and another file that contains 
papers we know cite, but don't use galpy. It then goes through all the potential papers and opens a browser with the arXiv PDF version of the paper. You can then quickly check whether the paper uses galpy and add it to the ``papers-using-galpy.json`` file by following the prompts. If you want to add the paper, the ``add_paper_using_galpy.py`` utility will be called with the arXiv ID of the paper. If you don't want to add the paper, you have the option to add it to the list of papers that cite galpy, but don't use it. Finally, the utility will also ask you to check papers that cite galpy, but don't have an arXiv ID. If you want to add these papers, you can do so manually or you can add them to the file of papers that cite galpy, but don't use it.

## Updating papers in the ``papers-using-galpy.json`` file

To check whether papers were published and update the entry in the ``papers-using-galpy.json`` file, run the utility
```
python update_paper_using_galpy.py [paper_id]
```
in the ``py/`` directory. Either run this with a single paper ID (the JSON key of the entry)
to update a single entry, or without any argument, to go through all entries without publication
info.
