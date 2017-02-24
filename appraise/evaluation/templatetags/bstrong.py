from django import template

register = template.Library()

@register.filter
def bstrong(value):
    return (value.replace("[b]","<strong>")).replace("[/b]","</strong>")
