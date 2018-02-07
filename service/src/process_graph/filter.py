''' Filter and URL Parsing for EODC Job Service'''

from json import loads
from flask import current_app
from requests import get

def parse_tree(url_pointer, filter_tree, out_array):
    ''' Parse the url structure of the filter tree recursively '''
    url_pointer += filter_tree[0]
    filter_tree = filter_tree[1:]

    for branch in filter_tree:
        parse_tree(url_pointer, branch, out_array)

    if len(filter_tree) == 0:
        out_array.append(url_pointer)

def parse_url_product(args):
    ''' Product URL structure '''
    return "&product_id={0}" \
            .format(args["product_id"])

def parse_url_filter_bbox(args):
    ''' filter_bbox URL structure '''
    return "&srs={0}left={1}&right={2}&top={3}&bottom={4}"\
            .format(args["srs"], args["left"], args["right"], args["top"], args["bottom"])

def parse_url_filter_daterange(args):
    ''' filter_daterange URL structure '''
    return "&from={0}&to={1}" \
            .format(args["from"], args["to"])

URL_PARSER = {
    "product": parse_url_product,
    "filter_bbox": parse_url_filter_bbox,
    "filter_daterange": parse_url_filter_daterange
}

class Filter:
    ''' Filter Class for EODC Job Service '''
    def __init__(self, filter_id, filter_args):
        self.filter_id = filter_id
        self.filter_args = self.parse_collections(filter_args)

    def parse_collections(self, filter_args):
        ''' Parse the collections an instantiate Filter objects  '''
        parsed_collections = []
        if "collections" in filter_args:
            for collection in filter_args["collections"]:
                if "product_id" in collection:
                    parsed_collections.append(Filter("product", collection))
                else:
                    parsed_collections.append(Filter(collection["process_id"], collection["args"]))

            filter_args["collections"] = parsed_collections

        return filter_args

    def get_url_params(self):
        ''' Get the URL parameters connected to the filter_id '''
        return URL_PARSER[self.filter_id](self.filter_args)

    def get_url_tree(self):
        ''' Return the URL tree of the filter '''
        branches = [self.get_url_params()]

        if "collections" in self.filter_args:
            for collection in self.filter_args["collections"]:
                branches.append(collection.get_url_tree())

        return branches

    def get_paths(self):
        base_url = current_app.config["DATA_REGISTRY"] + "/data/paths?p=0"
        url_tree = self.get_url_tree()

        urls = []
        parse_tree(base_url, url_tree, urls)

        url = urls[0]
        response = get(url)

        return loads(response.text)["message"]

