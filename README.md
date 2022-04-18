# galpy-website

galpy's website

![Update website](https://github.com/jobovy/galpy-website/workflows/Update%20website/badge.svg)

## Adding papers to the ``papers-using-galpy.json`` file

To easily and quickly add papers using galpy to the ``papers-using-galpy.json`` file, run the utility
```
python add_paper_using_galpy.py
```
in the ``py/`` directory. This will ask for an arXiv ID and create a new entry from there.

## Updating papers in the ``papers-using-galpy.json`` file

To check whether papers were published and update the entry in the ``papers-using-galpy.json`` file, run the utility
```
python update_paper_using_galpy.py [paper_id]
```
in the ``py/`` directory. Either run this with a single paper ID (the JSON key of the entry)
to update a single entry, or without any argument, to go through all entries without publication
info.
