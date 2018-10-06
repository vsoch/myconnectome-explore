# myconnectome-explore

This code base provides a flask-driven infrastructure to explore the myconnectome project data, either integrated in the [myconnectome-vm](https://github.com/poldrack/myconnectome-vm) or as a standalone application. This branch in particular is intended to just deploy a
static myconnectome explore results portal (meaning we have pre-generated timeseries, and
no active generation). If you want the version intended for use with myconnectome-vm, please
see the master branch.

## myConnectome-vm
If you are interested in reproducing all analyses in your own virtual machine, it is recommended to follow instructions in the [myconnectome-vm repository](https://github.com/poldrack/myconnectome-vm). This vm will use myconnectome-explore to provide interactive exploration for the data that you produce. The installation is automatic and you do not need to do anything beyond following instructions to set up the virtual machine.

## Run with Docker
The recommended approach is to run this with Docker. We have a pre-built Docker
container [here](https://hub.docker.com/r/poldracklab/myconnectome-explore/) 
to help you do this. You will need to bind your local port "80" to port
"5000" in the container where Flask is serving the application.

```bash
docker run -p 80:5000 poldracklab/myconnectome-explore
```

And then open up your browser to `http://127.0.0.1`

If you have something running on your port 80, you can of course use port 5000 instead:

```bash
docker run -p 5000:5000 poldracklab/myconnectome-explore
```

## Development
You can also choose to build the container locally, if you want to edit the
Dockerfile or otherwise.

```bash
git clone -b add/dockerfile https://github.com/vsoch/myconnectome-explore
cd myconnectome-explore
docker build -t poldracklab/myconnectome-explore .
```

Specifically, here are the steps we take to deploy the images. This code is
represented in [deploy.sh](deploy.sh). First, the version represented in
[VERSION](VERSION) *must* coincide with the 
[release version](https://github.com/poldrack/myconnectome/releases)
 of myconnectome that generated the timeseries. 
In this case, it corrects with version 1.0.0. Then, you should run the deploy.sh
script to build the new container using the version, and push both.

```bash
chmod u+x deploy.sh
./deploy.sh
```


## standalone application
Running the application locally is not recommended. However, it is possible 
if you run the steps in the Dockerfile to download the myconnectome data and
install dependencies. That might look something like this.
You should again first clone this repository

```bash
git clone -b add/dockerfile https://github.com/vsoch/myconnectome-explore
cd myconnectome-explore
```
For your python installation (whether system, virtual environment, or conda 
environment) you need to install dependencies:
 
```bash
conda install pandas
pip install flask flask-autoindex
```

Then, to run the application:

```bash
python databrowser.py
```

If you are interested in a deployment of that, see the master branch and
how it's deployed in the [myconnectome-vm](https://github.com/poldrack/myconnectome-vm/blob/master/Vagrantfile#L76).
