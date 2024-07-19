def get_system_base_url(request):
    return request.build_absolute_uri("/")[:-1]
