from flask import current_app


def add_to_index(index: object, model: object) -> object:
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        # getattr equals x.y , can provide default value
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)


def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        body={'query':
            {'multi_match':
                {
                    'query': query,
                    'fields': ['*']
                }
            },
            'from': (page - 1) * per_page, 'size': per_page
        })
    # list comprehension
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    # print(ids)
    return ids, search['hits']['total']['value']
