from flask import Flask, render_template
from banner import generate, format_data
from flask_autoindex import AutoIndex
from glob import glob
import pandas
import json
import os

app = Flask(__name__)
index = AutoIndex(app, browse_root='results', add_url_rules=False)
@app.route('/results')
@app.route('/results/<path:path>')
def autoindex(path='.'):
    print(path)
    return index.render_autoindex(path)

def get_lookup():
    return {"metab":"metabolomics clustering",
            "fullmetab":"single metabolites",
            "wgcna":"weighted correlation network analysis",
            "behav":"behavioral variables",
            "netdata":"brain network measures",
            "bwcorr":"between network correlation",
            "wincorr":"within-network correlation",
            "immport":"gene expression (immune)"}

def prepare_banner():
    letters, colors, xcoords, ycoords = generate(hidden="MYCONNECTOME",
                                                 color="#CCC",
                                                 color_hidden="#000")

    # Format for d3 input
    letters = format_data(letters)
    colors = format_data(colors)
    xcoords = format_data([str(x) for x in xcoords])
    ycoords = format_data([str(x) for x in ycoords])
    return letters, colors, xcoords, ycoords

def prepare_data():

    data_files = glob('results/pre-generated/timeseries/out*.txt')
    data_files.sort()
    dont_include = ['fd','pindex']

    # Split files into different categories, subcategories
    categories = [f.split('.')[2].split('_')[0] for f in data_files]
    subcategories = [f.split('.')[2].split('_')[1] for f in data_files]

    dropdown = dict()
    for d in list(set(categories)):
        if d not in dont_include:
            dropdown[d] = [subcategories[x] for x in range(0,len(categories)) if categories[x]==d]

    return dropdown

# No variable selection
@app.route('/')
def data_chooser():
 
    dropdown = prepare_data()

    # Human interpretable labels
    lookup = get_lookup()
    
    # Generate banner
    letters, colors, xcoords, ycoords = prepare_banner()

    return render_template('explore.html', 
                            dropdown=dropdown,
                            letters=letters,
                            colors=colors,
                            xcoords=xcoords,
                            ycoords=ycoords,
                            lookup=lookup)

# Variable selection
@app.route('/<variable1>/<variable2>')
def render_table(variable1,variable2):
 
    dropdown = prepare_data()

    # Human interpretable labels
    lookup = get_lookup()
    table = make_table(variable1, variable2)

    # Generate banner
    letters, colors, xcoords, ycoords = prepare_banner()

    # Link to download file
    download_link = '/results/pre-generated/timeseries/out.dat.%s_%s.txt' %(variable1, variable2)

    return render_template('explore.html', dropdown=dropdown,
                                           download_link=download_link,
                                           lookup=lookup,
                                           letters=letters,
                                           colors=colors,
                                           xcoords=xcoords,
                                           ycoords=ycoords,
                                           table=table)


# Read in a particular input file to render table
def make_table(variable1,variable2):

    # Read in appropriate data file
    data_file = 'results/pre-generated/timeseries/out.dat.%s_%s.txt' %(variable1,variable2)
    tmp = pandas.read_csv(data_file,sep=" ")
    
    # Variables we want to save
    xvar = tmp.xvar.tolist()
    yvar = tmp.yvar.tolist()
    corval = tmp["cor.val"].tolist()
    tarima = tmp["t.arima"].tolist()
    tdrift = tmp["t.drift"].tolist()
    nobs = tmp.nobs.tolist()
    pval_bh = tmp.pval_bh.tolist()

    return zip(xvar,yvar,corval,tarima,tdrift,nobs,pval_bh)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
