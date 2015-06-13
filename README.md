### myconnectome-explore

This code base provides a flask-driven infrastructure to explore the myconnectome project data, either integrated in the [myconnectome-vm](https://github.com/poldrack/myconnectome-vm) or as a standalone application.

#### myConnectome-vm
If you are interested in reproducing all analyses in your own virtual machine, it is recommended to follow instructions in the [myconnectome-vm repository](https://github.com/poldrack/myconnectome-vm). This vm will use myconnectome-explore to provide interactive exploration for the data that you produce. The installation is automatic and you do not need to do anything beyond following instructions to set up the virtual machine.

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

1. Your deployment environment will need flask installed to the python that will be running the application. If you are creating a local python environment to run the application, we reccommend using anaconda, as it comes with most of the libraries that you should need,
2. You should change "debug" "True" to debug "False" in the databrowser.py file.
3. In the folder you need two files: an .htaccess and a myconnectome.fcgi. The myconnectome.fcgi should look as follows:


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

4. Finally, you need to make your myconnectome.fcgi executable

      chmod u+x myconnectome.fcgi

That should be it! Going to the url yourserver/myconnectome should show the databrowser.
