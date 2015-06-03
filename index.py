from flask import Flask, render_template
from glob import glob
import pandas
import json
import numpy
import os

app = Flask(__name__)


def get_lookup():
    return {"metab":"metabolomics clustering",
              "fullmetab":"single metabolites",
              "wgcna":"weighted correlation network analysis",
              "behav":"behavioral variables",
              "netdata":"brain network measures",
              "bwcorr":"between network correlation",
              "wincorr":"within-network correlation",
              "immport":"gene expression (immune)"}


def prepare_data():

    data_files = glob('results/myconnectome/timeseries/out*.txt')
    data_files.sort()
    dont_include = ['fd','pindex']

    # Split files into different categories, subcategories
    categories = [f.split('.')[2].split('_')[0] for f in data_files]
    subcategories = [f.split('.')[2].split('_')[1] for f in data_files]

    dropdown = dict()
    for d in numpy.unique(categories):
        if d not in dont_include:
            dropdown[d] = [subcategories[x] for x in range(0,len(categories)) if categories[x]==d]

    return dropdown

# No variable selection
@app.route('/')
def data_chooser():
 
    dropdown = prepare_data()

    # Human interpretable labels
    lookup = get_lookup()
    
    return render_template('explore.html',dropdown=dropdown,lookup=lookup)

# Variable selection
@app.route('/<variable1>/<variable2>')
def render_table(variable1,variable2):
 
    dropdown = prepare_data()

    # Human interpretable labels
    lookup = get_lookup()
    table = make_table(variable1,variable2)

    return render_template('explore.html',dropdown=dropdown,lookup=lookup,table=table)


# Read in a particular input file to render table
def make_table(variable1,variable2):

    # Read in appropriate data file
    data_file = 'results/myconnectome/timeseries/out.dat.%s_%s.txt' %(variable1,variable2)
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
    app.debug = True
    app.run()
