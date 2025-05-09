from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css):
    existing = field.field.widget.attrs.get('class', '')
    new = f"{existing} {css}".strip()
    return field.as_widget(attrs={'class': new})
