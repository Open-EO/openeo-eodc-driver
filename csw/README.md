# pycsw docker setup

This is minimal explanation how to setup pycsw inside a docker container so it works with openEO.
For a complete documentation of pycsw and also pycsw inside docker please refer to the
[pycsw documnetation](https://docs.pycsw.org/en/stable/index.html).

## Setup

Inside this folder a docker-compose file is provided. It creates two docker containers, one running a PostGIS database,
one running a pycsw server.

Next a step-by-step explanation how to set it up. (All following steps assume that you are inside the
``openeo-openshift-driver`` folder.)

1. **Environment variable**: Copy ``pycsw.env`` from the sample-envs folder to the envs folder:
    ```bash
    cp sample-envs/pycsw.env envs/pycsw.env
    ```
    (Make sure the envs folder exists already, if not create if first ``mkdir envs``)  
    Then set username, password and database name in ``envs/pycsw.env``

1. **Pycsw Config**: Copy ``csw/sample_pycsw.cfg`` to ``csw/pycsw.cfg``
    ```bash
    cd csw
    cp sample_pycsw.cfg pycsw.cfg
    ```
    Then check the server configurations in ``pycsw.cfg`` (for more detail please refer to
    [pycsw configuration](https://docs.pycsw.org/en/stable/configuration.html)). Most important is to ensure that the database
    url fits the before set username, password and database. Do not change database host or port as they have to fit
    configurations set in the docker-compose.

1. **Input Metadata (XML)**: Create a folder ``csw/xml`` and a file ``csw/file_list.json`` with content as in ``sample_file_list.json``.
    The run ``python create_xmls.py`` from within the csw folder. This will create one .xml file per file specififed in
    file_list.json (for an example see the ``sample-xml`` folder). Make sure to also insert records for your parentidentifers
    otherwise no collections can be created. You can find an example in the ``sample_file_list.json`` (last record). In
    this case no parentidentifier has be be specified.
    ```bash
    mkdir csw/xml
    cd csw
    python create_xmls.py
    ```
1. **Setup containers**: Run docker-compose. This will create the two containers and already setup the needed database schema. It should be
mentioned here that currently a hotfixed version of the pycsw image is used as otherwise metadata can not be returned
in the iso schema. (see Dockerfile provided in this folder)
    ```bash
    docker-compose up
    ```

1. **Insert Metadata into DB**: Connect to the container and load xml files into the metadata database.
    ```bash
    # to list all running dock containers and get the id of the pycsw container
    docker ps
    docker exec -it <pycsw container id> sh

    # you are now inside the pycsw container
    pycsw-admin.py -c load_records -f /etc/pycsw/pycsw.cfg -p /home/pycsw/xml
    ```

pycsw should be running on port 8000 serving all inserted files.

To later add files to the DB just copy them into the container and repeat the last step.
