from rest_framework.viewsets import ModelViewSet
from .models import Tool, Developer, Domain, Accessibility, ContextWindow, RecommendationResults
from .serializers import ToolSerializer, DeveloperSerializer, DomainSerializer, AccessibilitySerializer, ContextWindowSerializer, RecommendationResultsSerializer, RecommendationResponseSerializer, RecommendationRequestSerializer
from rest_framework.viewsets import ViewSet
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .tasks import create_recommendation
from django.urls import reverse
from django.conf import settings


# As we are using custom permissions, we set auth=[] for read only endpoints to reflect permissions accurately in the docs.
@extend_schema_view(
    list=extend_schema(auth=[]),
    retrieve=extend_schema(auth=[])
)
@extend_schema(tags=['Developers'], description="Manage tool developers. Only staff can modify.")
class DeveloperViewSet(ModelViewSet):
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer

@extend_schema_view(
    list=extend_schema(auth=[]),
    retrieve=extend_schema(auth=[])
)
@extend_schema(tags=['Domains'], description="Manage tool domains. Only staff can modify.")
class DomainViewSet(ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer

@extend_schema_view(
    list=extend_schema(auth=[]),
    retrieve=extend_schema(auth=[])
)
@extend_schema(tags=['Accessibilities'], description="Manage tool accessibilities. Only staff can modify.")
class AccessibilityViewSet(ModelViewSet):
    queryset = Accessibility.objects.all()
    serializer_class = AccessibilitySerializer

@extend_schema_view(
    list=extend_schema(auth=[]),
    retrieve=extend_schema(auth=[])
)
@extend_schema(tags=['Context Windows'], description="Manage context windows. Only staff can modify.")
class ContextWindowViewSet(ModelViewSet):
    queryset = ContextWindow.objects.all()
    serializer_class = ContextWindowSerializer

class ToolPagination(PageNumberPagination):
    page_size = 20  # default page size
    page_size_query_param = 'page_size'  # client can set page size
    max_page_size = 100

@extend_schema_view(
    list=extend_schema(auth=[]),
    retrieve=extend_schema(auth=[])
)
@extend_schema(tags=['Tools'], description="Manage AI tools. Only staff can modify.", parameters=[
    OpenApiParameter("page", int, description="Page number", required=False, default=1),
    OpenApiParameter("page_size", int, description=f"Results per page. Max: {ToolPagination.max_page_size}", required=False, default=ToolPagination.page_size),
])
class ToolViewSet(ModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    pagination_class = ToolPagination

def build_search_params():
    params = [
        OpenApiParameter("q", str, description="Search ai_name"),
        OpenApiParameter("sort-by", str, description="Field to sort by"),
        OpenApiParameter("order", str, description="asc or desc"),
        OpenApiParameter("page", int, description="Page number", required=False, default=1),
        OpenApiParameter("page_size", int, description=f"Results per page. Max: {ToolPagination.max_page_size}", required=False, default=ToolPagination.page_size),
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

@extend_schema(
        description="""
Search tools using flexible query parameters with pagination support.

Usage
----------------
q:
    Searches the ai_name field for partial matches.

Field filters:
    Any Tool field can be filtered using ?field=value.

Range filters for numeric fields:
    ?field-min=value
    ?field-max=value

Sorting:
    sort-by=<field>
    order=asc|desc

Pagination:
    page: The page number to retrieve (default=1, optional)
    page_size: Number of results per page (default=20, max=100, optional)

Examples:
    /tools/search?q=vision
    /tools/search?primary_domain=nlp
    /tools/search?popularity_votes-min=1000
    /tools/search?popularity_votes-min=1000&popularity_votes-max=10000
    /tools/search?sort-by=popularity_votes&order=desc&page=2&page_size=50
""",
    parameters=build_search_params(),  # your existing dynamic params builder
    tags=['Tool Search'],
    examples=[
        OpenApiExample(
            "Search by name",
            value="/tools/search?q=vision"
        ),
        OpenApiExample(
            "Filter by domain",
            value="/tools/search?primary_domain=nlp"
        ),
    ]
)
class ToolSearchViewSet(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = ToolSerializer
    pagination_class = ToolPagination

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
            if name == "id":
                continue

            # exact match filter
            value = params.get(name)
            if value is not None:
                queryset = queryset.filter(**{name: value})

            # range filters for numeric fields
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

        # --- pagination ---
        if 'page' in params:
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request)
            serializer = ToolSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            # no pagination, return full result
            serializer = ToolSerializer(queryset, many=True)
            return Response(serializer.data)


class RecommendToolViewSet(ViewSet):
    queryset = RecommendationResults.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Recommendations"],
        description="Create a recommendation request based on a query. Takes a query 'q' and optional 'top_n' for number of results in the request body.",
        request=RecommendationRequestSerializer,
        responses={
            201: RecommendationResponseSerializer,
            400: OpenApiResponse(description="Bad request"),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def create(self, request, *args, **kwargs):
        query = request.data.get("q")
        
        top_n = max(1, min(int(request.data.get("top_n", 5)), 100))
        if not query:
            return Response({"detail": "Query parameter 'q' is required"}, status=400)

        results = RecommendationResults.objects.create(query=query, user=request.user)
        create_recommendation.enqueue(results_id=results.id, query=query, top_n=top_n)

        serializer = RecommendationResponseSerializer({
            "detail": "Recommendation created successfully",
            "results_id": results.id,
            "results_url_http": reverse(
                "recommendation-results-detail",
                kwargs={"pk": results.id}
            ),
            "results_url_ws": reverse(
                "recommendation-results-ws",
                kwargs={"results_id": results.id},
                urlconf=settings.CHANNELS_URLCONF
            ),
        })

        return Response(serializer.data, status=201)
    
    @extend_schema(
        tags=['Recommendations'],
        description="Retrieve recommendation results using results_id. Only the user who created the request or staff can access the results.",
        responses={
            200: RecommendationResultsSerializer,
            202: OpenApiResponse(RecommendationResultsSerializer, description="Recommendation is still being processed"),
            403: OpenApiResponse(description="You can only view your own recommendations"),
            404: OpenApiResponse(description="Results not found")
        }
    )
    def retrieve(self, request, *args, **kwargs):
        results_id = self.kwargs.get("pk")
        try:
            results = RecommendationResults.objects.get(pk=results_id, user=request.user)
        except RecommendationResults.DoesNotExist:
            return Response({"detail": "Results not found"}, status=404)

        if request.user != results.user and not request.user.is_staff:
            return Response({"detail": "You can only view your own recommendations"}, status=403)
        
        if results.completed_at is None:
            code = 202
        else:
            code = 200

        serializer = RecommendationResultsSerializer(results)
        return Response(serializer.data, status=code)

    @extend_schema(
        tags=['Recommendations'],
        description="Delete a recommendation result. Only the user who created the request or staff can delete the results.",
        responses={
            204: OpenApiResponse(description="Results deleted successfully"),
            403: OpenApiResponse(description="You can only delete your own recommendations"),
            404: OpenApiResponse(description="Results not found"),
        }
    )
    def destroy(self, request, *args, **kwargs):
        results_id = self.kwargs.get("pk")
        try:
            results = RecommendationResults.objects.get(pk=results_id)
        except RecommendationResults.DoesNotExist:
            return Response({"detail": "Results not found"}, status=404)

        if request.user != results.user and not request.user.is_staff:
            return Response({"detail": "You can only delete your own recommendations"}, status=403)

        results.delete()
        return Response(status=204)
    
    @extend_schema(
        tags=['Recommendations'],
        description="List all recommendation results. Staff users can see all results, non staff see their own results.",
        parameters=[
            OpenApiParameter("completed", bool, description="Filter by completion status. true for completed, false for pending.", required=False)
        ],
        responses={
            200: RecommendationResultsSerializer(many=True),
            401: OpenApiResponse(description="Authentication required"),
        }
    )
    def list(self, request, *args, **kwargs):
        if request.user.is_staff:
            queryset = RecommendationResults.objects.all()
        else:
            queryset = RecommendationResults.objects.filter(user=request.user)

        if request.query_params.get("completed"):
            try:
                completed = bool(request.query_params.get("completed").lower())
            except ValueError:
                pass
            finally:
                queryset = queryset.filter(completed_at__isnull=not completed)

        serializer = RecommendationResultsSerializer(queryset, many=True)
        return Response(serializer.data)
