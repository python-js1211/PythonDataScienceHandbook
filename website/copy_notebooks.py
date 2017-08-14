"""
This script copies all notebooks from the book into the website directory, and
creates pages which wrap them and link together.
"""
import os
import nbformat
import shutil

PAGEFILE = """title: {title}
slug: {slug}
Template: {template}

{{% notebook notebooks/{notebook_file} cells[{cells}] %}}
"""


def abspath_from_here(*args):
    here = os.path.dirname(__file__)
    path = os.path.join(here, *args)
    return os.path.abspath(path)

NB_SOURCE_DIR = abspath_from_here('..', 'notebooks')
NB_DEST_DIR = abspath_from_here('content', 'notebooks')
PAGE_DEST_DIR = abspath_from_here('content', 'pages')


def copy_notebooks():
    nblist = sorted(nb for nb in os.listdir(NB_SOURCE_DIR)
                    if nb.endswith('.ipynb'))
    name_map = {nb: os.path.join('/PythonDataScienceHandbook', 'pages',
                                 nb.rsplit('.', 1)[0].lower() + '.html')
                for nb in nblist}

    figsource = abspath_from_here('..', 'notebooks', 'figures')
    figdest = abspath_from_here('content', 'figures')

    if os.path.exists(figdest):
        shutil.rmtree(figdest)
    shutil.copytree(figsource, figdest)

    figurelist = os.listdir(abspath_from_here('content', 'figures'))
    figure_map = {os.path.join('figures', fig) : os.path.join('/PythonDataScienceHandbook/figures', fig)
                  for fig in figurelist}

    for nb in nblist:
        base, ext = os.path.splitext(nb)
        print('-', nb)

        content = nbformat.read(os.path.join(NB_SOURCE_DIR, nb),
                                as_version=4)

        if nb == 'Index.ipynb':
            cells = '1:'
            template = 'page'
            title = 'Python Data Science Handbook'
        else:
            cells = '2:'
            template = 'booksection'
            title = content.cells[2].source
            if not title.startswith('#') or len(title.splitlines()) > 1:
                raise ValueError('title not found in third cell')
            title = title.lstrip('#').strip()

            # put nav below title
            content.cells[0], content.cells[1], content.cells[2] = content.cells[2], content.cells[0], content.cells[1]

        # Replace internal URLs and figure links in notebook
        for cell in content.cells:
            if cell.cell_type == 'markdown':
                for nbname, htmlname in name_map.items():
                    if nbname in cell.source:
                        cell.source = cell.source.replace(nbname, htmlname)
                for figname, newfigname in figure_map.items():
                    if figname in cell.source:
                        cell.source = cell.source.replace(figname, newfigname)
                        
        nbformat.write(content, os.path.join(NB_DEST_DIR, nb))

        pagefile = os.path.join(PAGE_DEST_DIR, base + '.md')
        with open(pagefile, 'w') as f:
            f.write(PAGEFILE.format(title=title,
                                    slug=base.lower(),
                                    notebook_file=nb,
                                    template=template,
                                    cells=cells))

if __name__ == '__main__':
    copy_notebooks()

    
