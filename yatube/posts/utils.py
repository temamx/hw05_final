from django.core.paginator import Paginator

SELECT_LIMIT = 10


def paginator(request, posts):
    paginator = Paginator(posts, SELECT_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
