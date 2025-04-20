from django.db.models import Q
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    SearchHeadline,
)

from main.models import Products

from django.db.models import Q
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    SearchHeadline,
)

from main.models import Products

def q_search(query):
    if query.isdigit() and len(query) <= 5:
        return Products.objects.filter(id=int(query))
    vector = SearchVector("name", "description")#превращает имя и описание(продукта с шаблона) в векторный обьект в котором мы ищем(типо красная машина === машина красная) -----> спец обьект для поиска
    query = SearchQuery(query)#превращает наш запрос в  обьект для поиска(типо красная машина === машина красная) -----> спец обьект для поиска
    result = Products.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gt=0).order_by("-rank")
    result = result.annotate(
        headline=SearchHeadline(
            "name",
            query,
            start_sel='<span style="background-color: yellow;">',
            stop_sel="</span>",
        )
    )
 

    #выделение желтеньким совпаления в заголовке и описании товара (мол если написали машин  то у товара машина загорится машин)
    return result