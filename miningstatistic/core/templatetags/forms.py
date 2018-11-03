from django.template import Library, TemplateSyntaxError

from core.templatetags.names import verbose_name

register = Library()


@register.inclusion_tag(
    'core/includes/form.html',
    takes_context=True,
)
def form(context, *args, **kwargs):
    """Тег формы создания и изменения объекта.
    """
    # Формируем контекст для шаблона формы
    action = (args[0] if len(args) > 0
              else kwargs.get('action'))
    action_verbose = (args[1] if len(args) > 1
                      else kwargs.get('action_verbose'))
    method = (args[2] if len(args) > 2
              else kwargs.get('method'))
    form = context.get('form')
    view = context.get('view')

    if hasattr(view, 'model'):
        action_verbose = ' '.join(
            [action_verbose,
             verbose_name(view.model).lower()],
        )

    if action is None:
        raise TemplateSyntaxError(
            "form template tag requires "
            "at least one argument: action, "
            "which is a URL.")

    return {
        'action': action,
        'action_verbose': action_verbose,
        'form': form,
        'method': method}


@register.inclusion_tag(
    'core/includes/confirm_delete_form.html',
    takes_context=True,
)
def delete_form(context, *args, **kwargs):
    """Тег формы удаления объекта.
    """
    # Формируем контекст для шаблона формы
    action = (args[0] if len(args) > 0
              else kwargs.get('action'))
    method = (args[1] if len(args) > 1
              else kwargs.get('method'))
    form = context.get('form')
    display_object = kwargs.get(
        'object', context.get('object'))
    if action is None:
        raise TemplateSyntaxError(
            "delete_form template tag "
            "requires at least one argument: "
            "action, which is a URL.")
    if display_object is None:
        raise TemplateSyntaxError(
            "display_form needs object "
            "manually specified in this case.")
    if hasattr(display_object, 'name'):
        object_name = display_object.name
    else:
        object_name = str(display_object)
    object_type = kwargs.get(
        'obj_type',
        verbose_name(display_object),
    )
    return {
        'action': action,
        'form': form,
        'method': method,
        'object': display_object,
        'object_name': object_name,
        'object_type': object_type,
    }
