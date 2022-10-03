__author__     = 'Andrea Dainese'
__contact__    = 'andrea@adainese.it'
__copyright__  = 'Copyright 2022, Andrea Dainese'
__license__    = 'GPLv3'
__date__       = '2022-09-07'
__version__    = '0.9.8'

from django import template
from django.contrib.contenttypes.models import ContentType
from django.urls import NoReverseMatch, reverse

from extras.models import ExportTemplate
from utilities.utils import get_viewname, prepare_cloned_fields

register = template.Library()


@register.inclusion_tag('netdoc/buttons/discover.html')
def discover_button(instance):
    viewname = get_viewname(instance, 'discover')
    url = reverse(viewname, kwargs={'pk': instance.pk})

    return {
        'url': url,
    }
