import os
import nbformat as nbf

try:
    from openeo_to_eodatareaders import openeo_to_eodatareaders
except:
    from .openeo_to_eodatareaders import openeo_to_eodatareaders


def write_jupyter_nb(process_graph_json, job_data):
    """
    
    """

    # Convert from openEO to eoDataReaders syntax
    nodes, graph = openeo_to_eodatareaders(process_graph_json, job_data)
    
    # Instantiate jupyter notebook
    nb = nbf.v4.new_notebook()
    # Set kernel
    nb = add_metadata(nb)
    
    # Add imports
    code = '''\
import glob
from eodatareaders.eo_data_reader import eoDataReader'''
    nb['cells'].append(nbf.v4.new_code_cell(code))
    # nbf.v4.new_markdown_cell(text)

    translated_nodes = {}
    translated_nodes_keys = []
    for node in nodes:
        node_id = node[0]
        params = node[1]
        filepaths = node[2]
        node_dependencies = node[3]
        
        if filepaths:
            filepaths0 = 'filepaths = '
        else:
            if not node_dependencies:
                error("No filepaths and no node dependencies for node:{node_id}".format(node_id=node_id))
            
            filepaths0 = ''
            filepaths = []
            for dep in node_dependencies:
                filepaths.append(job_data + os.path.sep + dep + os.path.sep)
            filepaths = get_file_list(filepaths)
            

        translated_nodes[node_id] = '''\
### {node_id} ###

# node input files
{filepaths0}{filepaths}

# node input parameters
params = {params}

# evaluate node
{node_id} = eoDataReader(filepaths, params)\
'''.format(node_id=node_id, params=params, filepaths=filepaths, filepaths0=filepaths0)
                
        translated_nodes_keys.append(node_id)
    
    for node in nodes:
        node_id = node[0]
        params = node[1]
        filepaths = node[2]
        node_dependencies = node[3]
        
        current_index = translated_nodes_keys.index(node_id)
        dep_indices = []
        if node_dependencies:
            for dep in node_dependencies:
                dep_indices.append(translated_nodes_keys.index(dep)) 
        else:
            dep_indices.append(0)
        
        this_node = translated_nodes_keys.pop(current_index)
        translated_nodes_keys.insert(max(dep_indices) + 1, this_node)
    
    # Write to jupyter notebook in correct order
    for node_id in translated_nodes_keys:
        nb['cells'].append(nbf.v4.new_code_cell(translated_nodes[node_id]))
    nbf.write(nb, 'test.ipynb')
        
        
def get_file_list(filepaths):
    """
    
    """
            
    if isinstance(filepaths, str):
        
        file_list = """\
filepaths = sorted(glob.glob('{input_filepaths}' + '/*'))""".format(input_filepaths=filepaths)

    elif isinstance(filepaths, list):
        file_list = """\
input_filepaths = {input_filepaths}
filepaths = []
for path in {input_filepaths}:
    filepaths.extend(sorted(glob.glob(path + '/*')))""".format(input_filepaths=filepaths)
    
    return file_list
    
    
def add_metadata(nb):
    """
    
    """
    
    nb["metadata"]: {
        "kernelspec": {
             "display_name": "Python [conda env:eoDataReaders]",
             "language": "python",
             "name": "conda-env-eoDataReaders-py"
            },
            "language_info": {
             "codemirror_mode": {
              "name": "ipython",
              "version": 3
             },
         "file_extension": ".py",
         "mimetype": "text/x-python",
         "name": "python",
         "nbconvert_exporter": "python",
         "pygments_lexer": "ipython3",
         "version": "3.7.3"
            }
         }
         
    return nb
