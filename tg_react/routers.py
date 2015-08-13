from rest_framework.routers import DefaultRouter


class SuffixlessRouter(DefaultRouter):
    """
        So far we have never used this feature and it just makes our life harder, so we disable it
    """
    include_format_suffixes = False
