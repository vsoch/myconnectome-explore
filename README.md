# myconnectome-explore

This code base provides a flask-driven infrastructure to explore the myconnectome project data, either integrated in the [myconnectome-vm](https://github.com/poldrack/myconnectome-vm) or as a standalone application. This branch in particular is intended to just deploy a
static myconnectome explore results portal (meaning we have pre-generated timeseries, and
no active generation). If you want the version intended for use with myconnectome-vm, please
see the master branch.

## myConnectome-vm
If you are interested in reproducing all analyses in your own virtual machine, it is recommended to follow instructions in the [myconnectome-vm repository](https://github.com/poldrack/myconnectome-vm). This vm will use myconnectome-explore to provide interactive exploration for the data that you produce. The installation is automatic and you do not need to do anything beyond following instructions to set up the virtual machine.

## Run with Docker
The recommended approach is to run this with Docker. We have a pre-built Docker
container to help you do this:

```bash
docker build -t vanessa/myconnectome-explore .
docker run -p 80:5000 vanessa/myconnectome-explore
```
And then open up your browser to `http://localhost/`

## standalone application
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

      #!/usr/bin/env python
      from flup.server.fcgi import WSGIServer
      from databrowser import app as application
      WSGIServer(application).run()

The first line is the path to your python executable with flup and flask installed. 

Your .htaccess should look like this, given the location of the fcgi file in `/code/myconnectome.fcgi`:

      Options +ExecCGI
      AddHandler fcgid-script .fcgi 
      RewriteEngine On
      RewriteCond %{REQUEST_FILENAME} !=/code/myconnectome.fcgi
      RewriteRule ^(.*)$ myconnectome.fcgi/$1 [QSA,L]

Finally, you need to make your myconnectome.fcgi executable

      chmod u+x myconnectome.fcgi

That should be it! Going to the url yourserver/myconnectome should show the databrowser.
