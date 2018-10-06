FROM continuumio/miniconda3

################################################################################
# MyConnectome Results Portal
# 
# docker build -t vanessa/myconnectome-explore .
# docker run -p 80:5000 vanessa/myconnectome-explore
################################################################################

LABEL maintainer vsochat@stanford.edu

RUN apt-get update && apt-get install -y git
RUN conda update -n base conda && \
    /opt/conda/bin/conda install pandas

RUN mkdir /code
ADD . /code
RUN /opt/conda/bin/pip install flask flask-autoindex
WORKDIR /code
ENTRYPOINT ["/opt/conda/bin/python", "/code/databrowser.py"]
EXPOSE 5000
