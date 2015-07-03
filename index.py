from flask import Flask, render_template, redirect, Markup
from banner import generate, format_data
from flask.ext.autoindex import AutoIndex
from subprocess import Popen
from glob import glob
import pandas
import numpy
import os

app = Flask(__name__)
index = AutoIndex(app, browse_root='/var/www/results',add_url_rules=False)

# Global Data browser functions
def get_lookup():
    return {"metab":"metabolomics clustering",
            "fullmetab":"single metabolites",
            "wgcna":"weighted gene coexpression network clusters",
            "behav":"behavioral variables",
            "netdat":"brain network measures",
            "bwcorr":"between network correlation",
            "wincorr":"within-network correlation",
            "immport":"gene expression (immune)",
            "psoriasis":"psoriasis",
            "mood":"mood",
            "food":"food"}


def prepare_banner():
    letters, colors, xcoords, ycoords = generate(hidden="MYCONNECTOME",
                                                 color="#CCC",
                                                 color_hidden="#000")

    # Format for d3 input
    letters = format_data(letters)
    colors = format_data(colors)
    xcoords = format_data([str(x) for x in xcoords])
    ycoords = format_data([str(x) for x in ycoords])
    return letters,colors,xcoords,ycoords

def get_percent_complete():
    timefile = os.path.join(os.environ['MYCONNECTOME_DIR'],'myconnectome/utils/.expected_times.txt')
    times = pandas.read_csv(timefile,sep="\t")
    total_time = times.ELAPSED.sum()
    # Find which output files exist
    exist_index = [x for x in range(0,len(times.OUTNAME)) if os.path.exists(times.OUTNAME[x])]
    remain_index = [x for x in times.index if x not in exist_index]
    time_remaining = int(times.ELAPSED.loc[remain_index].sum())/60 + 1
    percent_complete = int(100*(times.ELAPSED.loc[exist_index].sum() / total_time))
    # Show link to last analysis completed
    try:
        last_completed_path = times.OUTNAME.loc[exist_index[-1]].replace(os.environ["MYCONNECTOME_DIR"],"/results/myconnectome")
        last_completed_name = os.path.basename(last_completed_path).split(".")[0].replace("_"," ")
        if len(last_completed_name)>14:
            last_completed_name = last_completed_name[0:14]
    except:
        last_completed_path = "#"
        last_completed_name = "..."
    return last_completed_path,last_completed_name,percent_complete,time_remaining

def prepare_data():

    data_files = glob('results/myconnectome/timeseries/out*.txt')
    data_files.sort()
    dont_include = ['fd','pindex','psoriasis','mood']

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

    # Get the context for each domain and count of # analyses
    timeseries_context,rna_context,meta_context,rsfmri_context,counter,number_analyses = get_context()

    # Get analysis status
    analysis_status = get_analysis_status(counter,number_analyses)

    # Generate banner
    letters,colors,xcoords,ycoords = prepare_banner()

    return render_template('log.html',err_log=err_log,
                                      out_log=out_log,
                                      letters=letters,
                                      colors=colors,
                                      xcoords=xcoords,
                                      ycoords=ycoords,
                                      analysis_status=analysis_status)


def read_log(logfile):
    logg = open(logfile,'rb').readlines()
    logg = [l[0:-1].decode("utf-8").replace("&#39;", "'") for l in logg]
    logg = Markup('<br>'.join(logg))
    return logg


@app.route('/')
def show_analyses():

    # Get the context for each domain and count of # analyses
    timeseries_context,rna_context,meta_context,rsfmri_context,counter,number_analyses = get_context()

    # Get analysis status
    analysis_status = get_analysis_status(counter,number_analyses)

    # Get the percentage of analyses complete
    last_completed_path,last_completed_name,percent_complete,time_remaining = get_percent_complete()

    # Generate banner
    letters,colors,xcoords,ycoords = prepare_banner()

    return render_template('index.html',timeseries_context=timeseries_context,
                                        rna_context=rna_context,
                                        meta_context=meta_context,
                                        analysis_status=analysis_status,
                                        rsfmri_context=rsfmri_context,
                                        letters=letters,
                                        colors=colors,
                                        xcoords=xcoords,
                                        ycoords=ycoords,
                                        percent_complete=percent_complete,
                                        last_completed_path=last_completed_path,
                                        last_completed_name=last_completed_name,
                                        time_remaining=time_remaining)

def get_analysis_status(counter,number_analyses):

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
    return analysis_status

def get_context():

    timeseries_files = [('/var/www/results/myconnectome/timeseries/timeseries_analyses_annot.html','Timeseries analysis results'),
                       ('/var/www/results/myconnectome/timeseries/Make_timeseries_plots.html','Timeseries plots'),
                       ('/var/www/results/myconnectome/timeseries/Make_combined_timeseries_table.html','Table of top timeseries results'),
                       ('/var/www/results/myconnectome/timeseries/Make_Timeseries_Heatmaps.html','Timeseries longitudinal heatmaps'),
                       ('/var/www/results/myconnectome/timeseries','Listing of all files')]
    rna_files =        [('/var/www/results/myconnectome/rna-seq/RNAseq_data_preparation.html','RNA-seq data preparation'),
                       ('/var/www/results/myconnectome/rna-seq/QA_summary_rnaseq.html','RNA-seq QA results'),
                       ('/var/www/results/myconnectome/rna-seq/Run_WGCNA.html','RNA-seq WGCNA analysis'),
                       ('/var/www/results/myconnectome/rna-seq/snyderome/Snyderome_data_preparation.html','Snyderome vs. MyConnectome analysis'),
                       ('/var/www/results/myconnectome/rna-seq','Listing of all files')]

    meta_files =       [('/var/www/results/myconnectome/metabolomics/Metabolomics_clustering.html','Metabolomics data preparation'),
                        ('/var/www/results/myconnectome/metabolomics','Listing of all files')]

    rsfmri_files =       [('/var/www/results/myconnectome/rsfmri/QA_summary_rsfmri.html','Resting fMRI QA results'),
                          ('/var/www/results/myconnectome/rsfmri','Listing of all files')]

    # How many green links should we have?
    number_analyses = len(meta_files) + len(rna_files) + len(timeseries_files) + len(rsfmri_files)

    # Check if the file exists, render context based on existence            
    counter = 0
    timeseries_context,counter = create_context(timeseries_files,counter)
    rna_context,counter = create_context(rna_files,counter)
    meta_context,counter = create_context(meta_files,counter)
    rsfmri_context,counter = create_context(rsfmri_files,counter)

    return timeseries_context,rna_context,meta_context,rsfmri_context,counter,number_analyses


# Check if python process is still running
def check_process():
    home_folder = os.environ['HOME']
    process_id = int(open('%s/myconnectome/.started' %(home_folder),'rb').readlines()[0][0:-1])
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
            styles.append('color:rgb(25, 234, 25);font-weight:400')
            titles.append(description)
        else:
            urls.append('#')
            descriptions.append('%s %s' %(description,'(in progress)'))
            styles.append('color:#666;')
            titles.append('PROCESSING')
    return zip(urls,descriptions,styles,titles),counter


# Data browser
# No variable selection
@app.route('/explore')
def data_chooser():

    dropdown = prepare_data()

    # Human interpretable labels
    lookup = get_lookup()

    # Get the context for each domain and count of # analyses
    timeseries_context,rna_context,meta_context,rsfmri_context,counter,number_analyses = get_context()

    # Get analysis status
    analysis_status = get_analysis_status(counter,number_analyses)

    # Generate banner
    letters,colors,xcoords,ycoords = prepare_banner()

    return render_template('explore.html',dropdown=dropdown,
                                          lookup=lookup,
                                          letters=letters,
                                          colors=colors,
                                          xcoords=xcoords,
                                          ycoords=ycoords,
                                          analysis_status=analysis_status)

# Variable selection
@app.route('/explore/<variable1>/<variable2>')
def render_table(variable1,variable2):

    dropdown = prepare_data()

    # Human interpretable labels
    lookup = get_lookup()
    table = make_table(variable1,variable2)

    # Get the context for each domain and count of # analyses
    timeseries_context,rna_context,meta_context,rsfmri_context,counter,number_analyses = get_context()

    # Get analysis status
    analysis_status = get_analysis_status(counter,number_analyses)

    # Generate banner
    letters,colors,xcoords,ycoords = prepare_banner()

    return render_template('explore.html',dropdown=dropdown,
                                          lookup=lookup,
                                          table=table,
                                          letters=letters,
                                          colors=colors,
                                          xcoords=xcoords,
                                          ycoords=ycoords,
                                          analysis_status=analysis_status)


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
    abscor = ["%.9f" %abs(x) for x in tmp["cor.val"].tolist()]
    qval_sort = ["%.9f" %x for x in tmp.pval_bh.tolist()]

    return zip(xvar,yvar,corval,tarima,tdrift,nobs,pval_bh,abscor,qval_sort)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
