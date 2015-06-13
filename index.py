from flask import Flask, render_template, redirect, Markup
from flask.ext.autoindex import AutoIndex
from subprocess import Popen
import numpy
import os

app = Flask(__name__)
index = AutoIndex(app, browse_root='/var/www/results',add_url_rules=False)

# Global Data browser functions
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

    data_files = glob('results/myconnectome/myconnectome/timeseries/out*.txt')
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

@app.route('/results')
@app.route('/results/<path:path>')
def autoindex(path='.'):
    return index.render_autoindex(path)

@app.route('/log')
def show_log():
    err_log = read_log('/var/www/results/myconnectome/myconnectome_job.err')
    out_log = read_log('/var/www/results/myconnectome/myconnectome_job.out')
    return render_template('log.html',err_log=err_log,
                                      out_log=out_log)

def read_log(logfile):
    logg = open(logfile,'rb').readlines()
    logg = [l[0:-1] for l in logg]
    logg = Markup('<br>'.join(logg))
    return logg


@app.route('/')
def show_analyses():

    timeseries_files = [('/var/www/results/myconnectome/timeseries/timeseries_analyses.html','Timeseries analyses'),
                       ('/var/www/results/myconnectome/timeseries/Make_Timeseries_Heatmaps.html','Timeseries heatmaps'),
                       ('/var/www/results/myconnectome/timeseries/Make_timeseries_plots.html','Timeseries plots'),
                       ('/var/www/results/myconnectome/timeseries/behav_heatmap.pdf','Behavioral timeseries heatmap'),
                       ('/var/www/results/myconnectome/timeseries/wincorr_heatmap.pdf','Within-network connectivity timeseries heatmap'),
                       ('/var/www/results/myconnectome/timeseries/wincorr_heatmap.pdf','Within-network connectivity timeseries heatmap'),
                       ('/var/www/results/myconnectome/timeseries/wgcna_heatmap.pdf','Gene expression module timeseries heatmap'),
                       ('/var/www/results/myconnectome/timeseries','Listing of all files')]
  rna_files =        [('/var/www/results/myconnectome/rna-seq/RNAseq_data_preparation.html','RNA-seq data preparation'),
                       ('/var/www/results/myconnectome/rna-seq/Run_WGCNA.html','RNA-seq WGCNA analysis'),
                       ('/var/www/results/myconnectome/rna-seq/snyderome/Snyderome_data_preparation.html','RNA-seq Snyderome analysis'),
                       ('/var/www/results/myconnectome/rna-seq','Listing of all files')]

    meta_files =       [('/var/www/results/myconnectome/metabolomics/Metabolomics_clustering.html','Metabolomics data preparation'),
                        ('/var/www/results/myconnectome/metabolomics','Listing of all files')]

    # How many green links should we have?
    number_analyses = len(meta_files) + len(rna_files) + len(timeseries_files)

    # Check if the file exists, render context based on existence            
    counter = 0
    timeseries_context,counter = create_context(timeseries_files,counter)
    rna_context,counter = create_context(rna_files,counter)
    meta_context,counter = create_context(meta_files,counter)

    # The counter determines if we've finished running analyses
    analysis_status = 'Analysis is Running'

    # Check if the process is still running
    process_running = check_process()

    # If the process is not running
    if process_running == False:
        if counter == number_analyses:
            analysis_status = 'Analysis Complete'
        else:
            analysis_status = 'Check for Error'

    return render_template('index.html',timeseries_context=timeseries_context,
                                        rna_context=rna_context,
                                        meta_context=meta_context,
                                        analysis_status=analysis_status)

# Check if python process is still running
def check_process():
    process_id = int(open('/home/vagrant/myconnectome/.started','rb').readlines()[0][0:-1])
    try:
        os.kill(process_id, 0)
    except OSError:
        return False
    else:
        return True

def create_context(links,counter):
    urls = []; descriptions = []; styles = []; titles = []
    for link in links:
        filename = link[0]
        description = link[1]
        if os.path.exists(filename):
            counter+=1
            urls.append(filename.replace('/var/www',''))
            descriptions.append(description)
            styles.append('color:rgb(25, 234, 25)')
            titles.append(description)
        else:
            urls.append('#')
            descriptions.append('%s %s' %(description,'(in progress)'))
            styles.append('color:#ACBAC1;')
            titles.append('PROCESSING')
    return zip(urls,descriptions,styles,titles),counter


# Data browser
# No variable selection
@app.route('/explore')
def data_chooser():
 
    dropdown = prepare_data()

    # Human interpretable labels
    lookup = get_lookup()
    
    return render_template('explore.html',dropdown=dropdown,lookup=lookup)

# Variable selection
@app.route('/explore/<variable1>/<variable2>')
def render_table(variable1,variable2):
 
    dropdown = prepare_data()

    # Human interpretable labels
    lookup = get_lookup()
    table = make_table(variable1,variable2)

    return render_template('explore.html',dropdown=dropdown,lookup=lookup,table=table)


# Read in a particular input file to render table
def make_table(variable1,variable2):

    # Read in appropriate data file
    data_file = 'results/myconnectome/myconnectome/timeseries/out.dat.%s_%s.txt' %(variable1,variable2)
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
    app.debug = False
    app.run(host='0.0.0.0')
