from django.template import Library, TemplateSyntaxError

register = Library()


@register.inclusion_tag(
    'core/includes/form.html',
    takes_context=True,
)
def display_form(context, *args, **kwargs):
    action = (args[0] if len(args) > 0
              else kwargs.get('action'))
    button = (args[1] if len(args) > 1
              else kwargs.get('button'))
    method = (args[2] if len(args) > 2
              else kwargs.get('method'))
    form = context.get('form')
    if action is None:
        raise TemplateSyntaxError(
            "form template tag requires "
            "at least one argument: action, "
            "which is a URL.")
    return {
        'action': action,
        'button': button,
        'form': form,
        'method': method}


@register.inclusion_tag(
    'core/includes/confirm_delete_form.html',
    takes_context=True,
)
def delete_form(context, *args, **kwargs):
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
        display_object._meta.verbose_name.title())
    return {
        'action': action,
        'form': form,
        'method': method,
        'object': display_object,
        'object_name': object_name,
        'object_type': object_type,
    }
