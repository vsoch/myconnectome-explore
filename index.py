from flask import Flask, render_template, redirect, Markup
from flask.ext.autoindex import AutoIndex
from subprocess import Popen
import os

app = Flask(__name__)
index = AutoIndex(app, browse_root='/var/www/results',add_url_rules=False)

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

if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0')
