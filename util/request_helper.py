from ..config import search_config, RECORDS_PER_PAGE


def get_search_confic_dic(request):
    arg_dict = {}
    for item in search_config:
        field = item['field']
        value = request.args.get(field)
        if value:
            arg_dict[field] = value

    return arg_dict


def get_pagination(request):
    start = request.args.get('start') or 0
    start = int(start)

    end = request.args.get('end') or RECORDS_PER_PAGE
    end = int(end)

    return start, end
