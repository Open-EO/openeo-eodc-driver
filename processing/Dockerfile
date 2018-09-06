FROM continuumio/miniconda3:latest

# Creating conda environment
ADD ./eoDataReaders/conda_environment.yml /tmp/environment.yml

WORKDIR /tmp
RUN conda env create

# Install eoDataReaders
RUN mkdir -p /tmp/eoDataReaders
ADD ./eoDataReaders /tmp/eoDataReaders
WORKDIR /tmp/eoDataReaders
RUN /bin/bash -c "source activate eoDataReaders && python setup.py install"

# Install eoFunctions
RUN mkdir -p /tmp/eoFunctions
ADD ./eoFunctions /tmp/eoFunctions
WORKDIR /tmp/eoFunctions
RUN /bin/bash -c "source activate eoDataReaders && python setup.py install"

# Copy code base
RUN mkdir -p /usr/src/app
ADD ./src /usr/src/app
WORKDIR /usr/src/app

# Run processing framework
CMD /bin/bash -c "source activate eoDataReaders && python main.py"
