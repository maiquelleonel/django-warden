import inspect

from django.apps import apps
from django.core.checks import Tags, Warning, register


def _is_field_indexed(model, field) -> bool:
    """
    Checks if a field is indexed directly, uniquely constrained, or covered as
    the leading column of an index/constraint defined in model Meta.
    """
    if field.db_index or field.unique or field.primary_key:
        return True

    # Check Meta.indexes (standalone index or leading column of composite index)
    for index in getattr(model._meta, "indexes", []):
        if index.fields and index.fields[0] == field.name:
            return True

    # Check Meta.constraints (UniqueConstraint)
    for constraint in getattr(model._meta, "constraints", []):
        fields = getattr(constraint, "fields", None)
        if fields and fields[0] == field.name:
            return True

    # Check Meta.unique_together
    for ut in getattr(model._meta, "unique_together", []):
        if ut and ut[0] == field.name:
            return True

    return False


@register(Tags.database)
def check_search_fields_indexing(app_configs, **kwargs):
    """
    Ensures that common search and lookup fields (e.g. email, phone_number, wa_id, uuid)
    are properly indexed to avoid full table scans in large datasets.
    """
    warnings = []

    # Analyze all registered models or a subset if app_configs is provided
    models_to_check = []
    if app_configs:
        for app_config in app_configs:
            models_to_check.extend(app_config.get_models())
    else:
        models_to_check = apps.get_models()

    target_field_names = ["email", "phone_number", "phone", "uuid"]

    for model in models_to_check:
        # Ignore external/django built-in apps unless explicitly targeted
        if model._meta.app_label in ["admin", "auth", "contenttypes", "sessions", "messages"]:
            continue

        for field in model._meta.fields:
            name_lower = field.name.lower()
            # If the field name contains any target search terms, ensure it is indexed or unique
            if any(term in name_lower for term in target_field_names):
                if not _is_field_indexed(model, field):
                    warnings.append(
                        Warning(
                            (
                                f"The field '{field.name}' on model '{model.__name__}' "
                                "is a typical search target but has no index."
                            ),
                            hint=(
                                "Set 'db_index=True' or 'unique=True' on this field declaration to prevent table scans."
                            ),
                            id="warden.W001",
                            obj=field,
                        )
                    )

    return warnings


@register(Tags.models)
def check_model_god_objects(app_configs, **kwargs):
    """
    Scans registered models to detect if any model is turning into a 'God Object' (Fat Model failure).
    Warns if a model has more than 10 custom methods or has external integration logic (e.g. requests, mail).
    """
    warnings = []

    models_to_check = []
    if app_configs:
        for app_config in app_configs:
            models_to_check.extend(app_config.get_models())
    else:
        models_to_check = apps.get_models()

    external_terms = ["requests.", "send_mail", "stripe.", "celery"]

    for model in models_to_check:
        # Ignore external/django built-in apps
        if model._meta.app_label in ["admin", "auth", "contenttypes", "sessions", "messages"]:
            continue

        try:
            source = inspect.getsource(model)
        except (TypeError, OSError):
            continue

        # Count defined custom methods (excluding special methods)
        custom_methods = []
        for name, attr in model.__dict__.items():
            if inspect.isfunction(attr) and not name.startswith("__"):
                custom_methods.append(name)

        has_external_integration = any(term in source for term in external_terms)
        too_many_methods = len(custom_methods) > 10

        if too_many_methods or has_external_integration:
            warnings.append(
                Warning(
                    (
                        f"The model '{model.__name__}' may be turning into a 'God Object' "
                        f"({len(custom_methods)} custom methods)."
                    ),
                    hint=(
                        "Consider moving complex workflows and external integration logic "
                        "(such as payments, emails, APIs) to a dedicated service layer ('services.py') "
                        "or orchestrator layer ('orchestrators/'). This keeps your models clean (Lean Models) "
                        "and makes the application delivery-agnostic (Views, DRF, or Django Ninja)."
                    ),
                    id="warden.W007",
                    obj=model,
                )
            )

    return warnings
