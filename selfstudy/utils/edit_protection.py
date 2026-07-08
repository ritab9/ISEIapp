from selfstudy.models import CurrentlyEditing
from django.contrib import messages

def get_form_state(form_id):
    form_state, _ = CurrentlyEditing.objects.get_or_create(
        form_id=form_id
    )
    return form_state

def get_edit_context(form_id):
    form_state = get_form_state(form_id)

    return {
        "form_id": form_id,
        "form_version": form_state.version,
    }

def validate_edit_version(request, form_id):
    """
    Ensures that the submitted form version matches the current version
    stored in CurrentlyEditing.

    Returns the locked form_state if valid.
    Returns None if validation fails.
    """

    submitted_version = request.POST.get("form_version")

    if submitted_version is None:
        messages.error(
            request,
            "The form version is missing. Please reload the page."
        )
        return None

    submitted_version = int(submitted_version)

    form_state = (
        CurrentlyEditing.objects
        .select_for_update()
        .get(form_id=form_id)
    )

    if submitted_version != form_state.version:
        username = (
            form_state.last_modified_by.get_full_name()
            if form_state.last_modified_by
            else "another user"
        )
        messages.error(
            request,
                "Your changes could not be saved because a newer version of this form already exists."
        )
        return None
    return form_state

def complete_edit(form_state, user):
    """ Marks an edit session as successfully completed. """
    form_state.version += 1
    form_state.last_modified_by = user
    form_state.user = None
    form_state.save(
        update_fields=[
            "version",
            "last_modified_by",
            "user",
            "last_active",
        ]
    )