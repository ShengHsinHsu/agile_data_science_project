import re

# Process Elasticsearch hits and return flight reocrds
def process_search(results):
    records = []

    if results['hits'] and results['hits']['hits']:
        total = results['hits']['total']
        hits = results['hits']['hits']

        for hit in hits:
            record = hit['__source']
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
