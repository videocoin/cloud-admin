from django import dispatch


drf_post_perform_create = dispatch.Signal(
    providing_args=['request', 'instance']
)

drf_post_perform_destroy = dispatch.Signal(
    providing_args=['request', 'instance']
)
