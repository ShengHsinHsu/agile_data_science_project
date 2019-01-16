import re


# Process Elasticsearch hits and return flight reocrds
def process_search(results):

    records = []
    if results['hits'] and results['hits']['hits']:
        total = results['hits']['total']
        hits = results['hits']['hits']

        for hit in hits:
            print(hit)
            record = hit['_source']
            records.append(record)

    return records, total


# Calculate offsets for fetching lists  of flights from MongoDB
def get_navigation_offsets(start, end, size):

    offsets = {}
    offsets['Next'] = {
        'top_offset': end + size,
        'bottom_offset': start+ size
    }

    offsets['Previous'] = {
        'top_offset': max(end + size, 0),
        'bottom_offset': max(start + size, 0) # Don't go < 0
    }

    return offsets


# Strip the existing start and end parameters from the query string
def strip_place(url):
    try:
        p = re.match('(.+)&start=.+&end=.+', url).group(1)
    except AttributeError as e:
        return url
    return p


def build_query():
    query = {
        'query': {
            'bool': {
                'must': []
            }
        },
        'sort': ['_score']
    }

    return query


def set_sorting(sorting_list, query):

    for field in sorting_list:
        sorting = {field : {'order': 'asc'}}
        query['sort'].append(sorting)

    return query


def set_pagination(start, page_size, query):
    query['from'] = start
    query['size'] = page_size

    return query


def set_search_critieria(criteria_dict, query):

    for c in criteria_dict:
        dic = {'match': {c: criteria_dict[c]}}
        query['query']['bool']['must'].append(dic)

    return query
