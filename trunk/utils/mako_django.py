# developed by huangyi
# changed by limodou
# MAKO_TEMPLATE_DIRS to TEMPLATE_DIRS
# 2007/06/15
#   add MAKO_FILESYSTEM_CHECKS option, default value is settings.DEBUG
#   add MAKO_OUTPUT_ENCODING option, default value is settings.DEFAULT_CHARSET 
#   add MAKO_INPUT_ENCODING option, default value is settings.DEFAULT_CHARSET
#   add MAKO_DEFAULT_FILTERS option, default value is ['decode.' + settings.DEFAULT_CHARSET.replace('-', '_')]

from django.conf import settings
from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.template.context import Context
from mako.lookup import TemplateLookup
from mako.exceptions import TopLevelLookupException
import os

from common import app_dirs, uni_str

'''
configurations:
    TEMPLATE_DIRS:
        A tuple, specify the directories in which to find the mako templates
    MAKO_MODULE_DIR:
        A string, if specified, all of the compiled template module files will be
        stored in this directory.
    MAKO_MODULENAME_CALLABLE:
        A callable, if MAKO_MODULE_DIR is not specified, this will be
        used to determine the filename of compiled template module file.
        See [http://www.makotemplates.org/trac/ticket/14]
        Default to the function `default_module_name`, which
        just appends '.py' to the template filename.
'''

app_template_dirs = []
for app_dir in app_dirs:
    template_dir = os.path.join(app_dir, 'templates')
    if os.path.isdir(template_dir):
        app_template_dirs.append(template_dir)

template_dirs = getattr(settings, 'TEMPLATE_DIRS', ())
template_dirs += tuple(app_template_dirs)

def default_module_name(filename, uri):
    '''
    Will store module files in the same directory as the corresponding template files.
    detail about module_name_callable, go to 
    http://www.makotemplates.org/trac/ticket/14
    '''
    return filename+'.py'

filesystem_checks = getattr(settings, 'MAKO_FILESYSTEM_CHECKS', settings.DEBUG)
output_encoding = getattr(settings, 'MAKO_OUTPUT_ENCODING', settings.DEFAULT_CHARSET)
input_encoding = getattr(settings, 'MAKO_INPUT_ENCODING', settings.DEFAULT_CHARSET)
default_filters = getattr(settings, 'MAKO_DEFAULT_FILTERS', ['decode.' + settings.DEFAULT_CHARSET.replace('-', '_')])
module_dir = getattr(settings, 'MAKO_MODULE_DIR', None)
module_name_callable = getattr(settings, 'MAKO_MODULENAME_CALLABLE', default_module_name)
lookup = TemplateLookup(directories=template_dirs,
        modulename_callable=module_name_callable, 
        module_directory=module_dir, 
        filesystem_checks=filesystem_checks,
        output_encoding=output_encoding,
        input_encoding=input_encoding,
        default_filters=default_filters)

def select_template(template_name_list):
    for template_name in template_name_list:
        try:
            return lookup.get_template(template_name)
        except TopLevelLookupException:
            pass

    raise TemplateDoesNotExist, 'mako templates: '+', '.join(template_name_list)

def get_template(template_name):
    try:
        return lookup.get_template(template_name)
    except TopLevelLookupException:
        raise TemplateDoesNotExist, 'mako templates: '+template_name

def render_to_response(template_name, dictionary=None,
        context_instance=None):
    if isinstance(template_name, (list, tuple)):
        template = select_template(template_name)
    else:
        template = get_template(template_name)

    dictionary = dictionary or {}
    if context_instance is None:
        context_instance = Context(dictionary)
    else:
        context_instance.update(dictionary)
    data = {}
    [data.update(d) for d in context_instance]
    data = uni_str(data, encoding=settings.DEFAULT_CHARSET, key_convert=False)
    return HttpResponse(template.render(**data))
