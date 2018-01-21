''' Filter and URL Parsing for EODC Job Service'''

def parse_urls(base_url, filter_graph):
    ''' Get the URLs from the filter graph  '''
    url_tree = filter_graph.get_url_tree()

    urls = []
    parse_tree(base_url, url_tree, urls)

    return urls

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
    return "&qname={0}" \
            .format(args["product_id"])

def parse_url_filter_bbox(args):
    ''' filter_bbox URL structure '''
    return "&qgeom=(({0}, {1}, {2}, {3}, {4}))" \
            .format(args["left"], args["right"], args["top"], args["bottom"], args["finish"])

def parse_url_filter_daterange(args):
    ''' filter_daterange URL structure '''
    return "&qstartdate={0}&qenddate={1}" \
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
