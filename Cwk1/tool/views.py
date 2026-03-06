from rest_framework.viewsets import ModelViewSet
from .models import Tool, Developer, Domain, Accessibility, ContextWindow
from .serializers import ToolSerializer, DeveloperSerializer, DomainSerializer, AccessibilitySerializer, ContextWindowSerializer
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

class DeveloperViewSet(ModelViewSet):
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer

class DomainViewSet(ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer

class AccessibilityViewSet(ModelViewSet):
    queryset = Accessibility.objects.all()
    serializer_class = AccessibilitySerializer

class ContextWindowViewSet(ModelViewSet):
    queryset = ContextWindow.objects.all()
    serializer_class = ContextWindowSerializer

class ToolViewSet(ModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer

def build_search_params():
    params = [
        OpenApiParameter("q", str, description="Search ai_name"),
        OpenApiParameter("sort-by", str, description="Field to sort by"),
        OpenApiParameter("order", str, description="asc or desc"),
    ]

    for field in Tool._meta.fields:
        name = field.name

        params.append(
            OpenApiParameter(
                name=name,
                type=str,
                description=f"Exact match filter for {name}",
                required=False,
            )
        )

        if field.get_internal_type() in ["IntegerField", "FloatField"]:
            params.append(
                OpenApiParameter(
                    name=f"{name}-min",
                    type=float,
                    description=f"Minimum {name}",
                    required=False,
                )
            )
            params.append(
                OpenApiParameter(
                    name=f"{name}-max",
                    type=float,
                    description=f"Maximum {name}",
                    required=False,
                )
            )

    return params

class ToolSearchViewSet(ViewSet):

    @extend_schema(
        description="""
Search tools using flexible query parameters.

Query Parameters
----------------
q:
    Searches the ai_name field.

Field filters:
    Any Tool field can be filtered using ?field=value.

Range filters for integer fields:
    ?field-min=value
    ?field-max=value

Examples:
    /tools/search?q=vision  
    /tools/search?primary_domain=nlp  
    /tools/search?popularity_votes-min=1000
    /tools/search?popularity_votes-min=1000&popularity_votes-max=10000  

Sorting:
    sort-by=<field>
    order=asc|desc

Examples:
    /tools/search?sort-by=popularity_votes&order=desc
""",
        parameters=build_search_params()
    )
    def list(self, request):

        queryset = Tool.objects.all()
        params = request.query_params

        # --- search query ---
        q = params.get("q")
        if q:
            queryset = queryset.filter(ai_name__icontains=q)

        # --- dynamic field filtering ---
        for field in Tool._meta.fields:

            name = field.name

            # skip id field if desired
            if name == "id":
                continue

            # exact match filter
            value = params.get(name)
            if value is not None:
                queryset = queryset.filter(**{name: value})

            # range filters for integer fields
            if field.get_internal_type() in ["IntegerField", "BigIntegerField", "FloatField"]:

                min_param = params.get(f"{name}-min")
                max_param = params.get(f"{name}-max")

                if min_param is not None:
                    queryset = queryset.filter(**{f"{name}__gte": min_param})

                if max_param is not None:
                    queryset = queryset.filter(**{f"{name}__lte": max_param})

        # --- sorting ---
        sort_by = params.get("sort-by")
        order = params.get("order", "asc")

        if sort_by:
            if order == "desc":
                sort_by = f"-{sort_by}"
            queryset = queryset.order_by(sort_by)

        serializer = ToolSerializer(queryset, many=True)
        return Response(serializer.data)