### myconnectome-explore

This code base provides a flask-driven infrastructure to explore the myconnectome project data, either integrated in the [myconnectome-vm](https://github.com/poldrack/myconnectome-vm) or as a standalone application.

#### myConnectome-vm
If you are interested in reproducing all analyses in your own virtual machine, it is recommended to follow instructions in the [myconnectome-vm repository](https://github.com/poldrack/myconnectome-vm). This vm will use myconnectome-explore to provide interactive exploration for the data that you produce. The installation is automatic and you do not need to do anything beyond following instructions to set up the virtual machine.

If you are looking for a quick (non production) deployment container of the application,
see the [poldracklab/myconnectome-explore](https://hub.docker.com/r/poldracklab/myconnectome-explore/) container served by the [add/dockerfile](https://github.com/vsoch/myconnectome-explore/tree/add/dockerfile) branch of this repository. This is a container that you can run locally to see
the interface. If you want to see how the application is deployed in production,
please see this master branch being cloned in the [myconnectome-vm Vagrantfile](https://github.com/poldrack/myconnectome-vm/blob/master/Vagrantfile#L76).

### standalone application
You should first clone this repository

      git clone https://github.com/vsoch/myconnectome-explore
      cd myconnectome-explore

Install flask and flup

      pip install flask
      pip install flup

And then run the server locally
 
      python databrowser.py

Don't worry about index.py - that is the executable that is integrated into the myconnectome-vm.

### deployment

Your deployment environment will need flask installed to the python that will be running the application. If you are creating a local python environment to run the application, we reccommend using anaconda, as it comes with most of the libraries that you should need. You should also change "debug" "True" to debug "False" in the databrowser.py file. FInally, in the folder you need two files: an .htaccess and a myconnectome.fcgi. The myconnectome.fcgi should look as follows:

      #!/home/youruser/local/anaconda/bin/python
      from flup.server.fcgi import WSGIServer
      from databrowser import app as application
      WSGIServer(application).run()


The first line is the path to your python executable with flup and flask installed. 


Your .htaccess should look like this:

      Options +ExecCGI
      AddHandler fcgid-script .fcgi 
      RewriteEngine On
      RewriteCond %{REQUEST_FILENAME} !=/home/youruser/public_html/myconnectome/myconnectome.fcgi
      RewriteRule ^(.*)$ myconnectome.fcgi/$1 [QSA,L]

The fourth line is the path to the myconnectome.fcgi

Finally, you need to make your myconnectome.fcgi executable

      chmod u+x myconnectome.fcgi

That should be it! Going to the url yourserver/myconnectome should show the databrowser.
