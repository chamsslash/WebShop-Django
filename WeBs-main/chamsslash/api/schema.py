def only_api_paths(endpoints, **kwargs):
    """В Swagger показываем только /api/: старые URL шаблонов ведут на те же вьюхи и дублировали бы их."""
    return [e for e in endpoints if e[0].startswith('/api/') and not e[0].startswith('/api/schema')]
