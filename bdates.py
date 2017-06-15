# -*- coding: utf-8 -*-
"""
Important date listings -- BDATES
=================================
Author: Toni Heittola (toni.heittola@gmail.com)

"""

import os
import shutil
import logging
import copy
from bs4 import BeautifulSoup
from jinja2 import Template
from pelican import signals, contents
import datetime
import yaml
import operator

logger = logging.getLogger(__name__)
__version__ = '0.1.0'

bdates_default_settings = {
    'panel-color': 'panel-default',
    'header': 'Dates',
    'mode': 'panel',
    'template': {
        'panel': """
            <div class="panel {{ panel_color }} hidden-print">
              {% if header %}
              <div class="panel-heading">
                <h3 class="panel-title">{{header}}</h3>
              </div>
              {% endif %}
              <ul class="bdates-container list-group">
              {{list}}
              </ul>
            </div>
         """,
        'list': """
            {% if header %}<h3 class="section-heading text-center">{{header}}</h3>{% endif %}
            <div class="list-group bdates-container">
            {{list}}
            </div>
        """},
    'item-template': {
        'panel': """
            <a class="list-group-item {{item_color}}" href="{{site_url}}/{{item_url}}">
            <div class="row">
                <div class="col-md-12"><h5 class="list-group-item-heading {{item_css}}"><strong>{{item_date}}</strong></h5></div>
                <div class="col-md-12"><h5 class="list-group-item-heading {{item_css}}">{{item_title}}</h5></div>
            </div>
            </a>
            """,
        'list': """<a class="list-group-item {{item_color}}" href="{{site_url}}/{{item_url}}">
            <div class="row">
                <div class="col-md-9"><h4 class="list-group-item-heading {{item_css}}">{{item_title}}</h4></div>
                <div class="col-md-3"><h5 class="list-group-item-heading {{item_css}}"><strong>{{item_date}}</strong></h5></div>
            </div>
            </a>
        """},
    'data-source': None,
    'category': None,
    'count': None,
    'past-dates': 'muted', # None, muted
    'show': False,
    'minified': True,
    'generate_minified': True,
    'show-categories': False,
    'shorten-category-label': True,
    'category-label-css': {},
    'template-variable': False,
    'site-url': '',
    'date-format': '%d %b %Y',
}

bdates_settings = copy.deepcopy(bdates_default_settings)


def load_dates_registry(source=None):
    """

    :param source: filename of the data file
    :return: dates registry
    """

    if source and os.path.isfile(source):
        try:
            with open(source, 'r') as field:
                dates = yaml.load(field)

            if 'data' in dates:
                dates = dates['data']

            for item_id, item in enumerate(dates):
                item['datetime'] = datetime.datetime.strptime(item['date'], '%d-%m-%Y')

            dates.sort(key=operator.itemgetter('datetime'))
            return dates

        except ValueError:
            logger.warn('`pelican-bdates` failed to load file [' + str(source) + ']')
            return False

    else:
        logger.warn('`pelican-bdates` failed to load file [' + str(source) + ']')
        return False


def get_attribute(attrs, name, default=None):
    """
    Get div attribute
    :param attrs: attribute dict
    :param name: name field
    :param default: default value
    :return: value
    """

    if 'data-'+name in attrs:
        return attrs['data-'+name]
    else:
        return default


def item_link(item, settings):
    past_date = item['datetime'] > datetime.datetime.now()
    if not past_date:
        item_css = 'text-muted'
        item_color = ''
    else:
        item_css = ''
        # only use colors for upcoming dates
        if 'color' in item:
            item_color = item['color']
        else:
            item_color = ''

    template = Template(settings['item-template'][settings['mode']].strip('\t\r\n').replace('&gt;', '>').replace('&lt;', '<'))
    if 'duration_days' not in item:
        item_date = item['datetime'].strftime(settings['date-format'])
    else:
        start_date = item['datetime']
        stop_date = item['datetime'] + datetime.timedelta(days=item['duration_days']-1)
        item_date = start_date.strftime(settings['date-format'])+' - '+stop_date.strftime(settings['date-format'])

    html = BeautifulSoup(template.render(site_url=settings['site-url'],
                                         item_css=item_css,
                                         item_url=item['url'] if 'url' in item else '',
                                         item_title=item['title'],
                                         item_date=item_date,
                                         item_color=item_color,
                                         ), "html.parser")

    return html.decode()


def generate(settings):
    dates = load_dates_registry(source=settings['data-source'])

    if dates:
        html = "\n"
        count = 0
        for item_id, item in enumerate(dates):
            if settings['count'] and count < settings['count']:
                if 'category' in bdates_settings and settings['category']:
                    if item['category'] in settings['category']:
                        html += item_link(item=item, settings=settings) + "\n"
                        count += 1
                else:
                    html += item_link(item=item, settings=settings) + "\n"
                    count += 1
            else:
                if 'category' in settings and settings['category']:
                    if item['category'] in settings['category']:
                        html += item_link(item=item, settings=settings) + "\n"
                        count += 1
                else:
                    html += item_link(item=item, settings=settings) + "\n"
                    count += 1
        html += "\n"
        template = Template(settings['template'][settings['mode']].strip('\t\r\n').replace('&gt;', '>').replace('&lt;', '<'))

        if count:
            return BeautifulSoup(template.render(list=html,
                                                 header=settings['header'],
                                                 site_url=settings['site-url'],
                                                 panel_color=settings['panel-color'],), "html.parser")
        else:
            return ''


def bdates(content):
    """
    Main processing

    """

    if isinstance(content, contents.Static):
        return

    soup = BeautifulSoup(content._content, 'html.parser')

    # Template variable
    if bdates_settings['template-variable']:
        # We have page variable set
        bdates_settings['show'] = True
        div_html = generate(settings=bdates_settings)
        content.bdates = div_html.decode()

    else:
        content.bdates = None

    bdates_divs = soup.find_all('div', class_='bdates')

    if bdates_divs:
        bdates_settings['show'] = True

        for bdates_div in bdates_divs:
            # We have div in the page
            settings = copy.deepcopy(bdates_settings)
            settings['data-source'] = get_attribute(bdates_div.attrs, 'source', bdates_settings['data-source'])
            settings['mode'] = get_attribute(bdates_div.attrs, 'mode', bdates_settings['mode'])
            settings['header'] = get_attribute(bdates_div.attrs, 'header', bdates_settings['header'])
            settings['category'] = get_attribute(bdates_div.attrs, 'category', bdates_settings['category'])
            if settings['category'] and isinstance(settings['category'], basestring):
                settings['category'] = [x.strip() for x in settings['category'].split(',')]

            settings['count'] = get_attribute(bdates_div.attrs, 'count', bdates_settings['count'])
            if settings['count']:
                settings['count'] = int(settings['count'])

            settings['panel-color'] = get_attribute(bdates_div.attrs, 'panel-color', bdates_default_settings['panel-color'])
            settings['show-categories'] = get_attribute(bdates_div.attrs, 'show-categories', bdates_default_settings['show-categories'])
            settings['date-format'] = get_attribute(bdates_div.attrs, 'date-format', bdates_default_settings['date-format'])

            div_html = generate(settings=settings)
            bdates_div.replaceWith(div_html)

    if bdates_settings['show']:

        if bdates_settings['minified']:
            html_elements = {
                'css_include': ['<link rel="stylesheet" href="' + bdates_settings['site-url'] + '/theme/css/bdates.min.css">']
             }
        else:
            html_elements = {
                'css_include': ['<link rel="stylesheet" href="' + bdates_settings['site-url'] + '/theme/css/bdates.css">']
            }

        if u'scripts' not in content.metadata:
            content.metadata[u'scripts'] = []

        if u'styles' not in content.metadata:
            content.metadata[u'styles'] = []
        for element in html_elements['css_include']:
            if element not in content.metadata[u'styles']:
                content.metadata[u'styles'].append(element)

    content._content = soup.decode()


def process_page_metadata(generator, metadata):
    """
    Process page metadata and assign css and styles

    """

    global bdates_default_settings, bdates_settings
    bdates_settings = copy.deepcopy(bdates_default_settings)

    if u'styles' not in metadata:
        metadata[u'styles'] = []
    if u'scripts' not in metadata:
        metadata[u'scripts'] = []

    if u'bdates' in metadata and (metadata['bdates'] == 'True' or metadata['bdates'] == 'true'):
        bdates_settings['show'] = True
        bdates_settings['template-variable'] = True
    else:
        bdates_settings['show'] = False
        bdates_settings['template-variable'] = False

    if u'bdates_source' in metadata:
        bdates_settings['data-source'] = metadata['bdates_source']

    if u'bdates_mode' in metadata:
        bdates_settings['mode'] = metadata['bdates_mode']

    if u'bdates_panel_color' in metadata:
        bdates_settings['panel-color'] = metadata['bdates_panel_color']

    if u'bdates_header' in metadata:
        bdates_settings['header'] = metadata['bdates_header']

    if u'bdates_category' in metadata:
        bdates_settings['category'] = [x.strip() for x in metadata['bdates_category'].split(',')]

    if u'bdates_count' in metadata:
        bdates_settings['count'] = metadata['bdates_count']
        if bdates_settings['count']:
            bdates_settings['count'] = int(bdates_settings['count'])

    if u'bdates_show_categories' in metadata:
        bdates_settings['show-categories'] = metadata['bdates_show_categories']

    if u'bdates_date_format' in metadata:
        bdates_settings['date-format'] = metadata['bdates_date_format']


def move_resources(gen):
    """
    Move files from js/css folders to output folder, use minified files.

    """

    plugin_paths = gen.settings['PLUGIN_PATHS']
    if bdates_settings['minified']:
        if bdates_settings['generate_minified']:
            minify_css_directory(gen=gen, source='css', target='css.min')

        css_target = os.path.join(gen.output_path, 'theme', 'css', 'bdates.min.css')
        if not os.path.exists(os.path.join(gen.output_path, 'theme', 'css')):
            os.makedirs(os.path.join(gen.output_path, 'theme', 'css'))

        for path in plugin_paths:
            css_source = os.path.join(path, 'pelican-bdates', 'css.min', 'bdates.min.css')

            if os.path.isfile(css_source):
                shutil.copyfile(css_source, css_target)

            if os.path.isfile(css_target):
                break
    else:
        css_target = os.path.join(gen.output_path, 'theme', 'css', 'bdates.css')
        if not os.path.exists(os.path.join(gen.output_path, 'theme', 'css')):
            os.makedirs(os.path.join(gen.output_path, 'theme', 'css'))

        for path in plugin_paths:
            print path
            css_source = os.path.join(path, 'pelican-bdates', 'css', 'bdates.css')

            if os.path.isfile(css_source):
                shutil.copyfile(css_source, css_target)

            if os.path.isfile(css_target):
                break


def minify_css_directory(gen, source, target):
    """
    Move CSS resources from source directory to target directory and minify. Using rcssmin.

    """
    import rcssmin

    plugin_paths = gen.settings['PLUGIN_PATHS']
    for path in plugin_paths:
        source_ = os.path.join(path, 'pelican-bdates', source)
        target_ = os.path.join(path, 'pelican-bdates', target)
        if os.path.isdir(source_):
            if not os.path.exists(target_):
                os.makedirs(target_)

            for root, dirs, files in os.walk(source_):
                for current_file in files:
                    if current_file.endswith(".css"):
                        current_file_path = os.path.join(root, current_file)
                        with open(current_file_path) as css_file:
                            with open(os.path.join(target_, current_file.replace('.css', '.min.css')), "w") as minified_file:
                                minified_file.write(rcssmin.cssmin(css_file.read(), keep_bang_comments=True))


def init_default_config(pelican):
    """
    Handle settings from pelicanconf.py

    """

    global bdates_default_settings, bdates_settings

    bdates_default_settings['site-url'] = pelican.settings['SITEURL']

    if 'BDATES_SOURCE' in pelican.settings:
        bdates_default_settings['data-source'] = pelican.settings['BDATES_SOURCE']

    if 'BDATES_HEADER' in pelican.settings:
        bdates_default_settings['header'] = pelican.settings['BDATES_HEADER']

    if 'BDATES_TEMPLATE' in pelican.settings:
        bdates_default_settings['template'].update(pelican.settings['BDATES_TEMPLATE'])

    if 'BDATES_ITEM_TEMPLATE' in pelican.settings:
        bdates_default_settings['item-template'].update(pelican.settings['BDATES_ITEM_TEMPLATE'])

    if 'BDATES_CATEGORY_LABEL_CSS' in pelican.settings:
        bdates_default_settings['category-label-css'] = pelican.settings['BDATES_CATEGORY_LABEL_CSS']

    if 'BDATES_PANEL_COLOR' in pelican.settings:
        bdates_default_settings['panel-color'] = pelican.settings['BDATES_PANEL_COLOR']

    if 'BDATES_MINIFIED' in pelican.settings:
        bdates_default_settings['minified'] = pelican.settings['BDATES_MINIFIED']

    if 'BDATES_GENERATE_MINIFIED' in pelican.settings:
        bdates_default_settings['generate_minified'] = pelican.settings['BDATES_GENERATE_MINIFIED']

    bdates_settings = copy.deepcopy(bdates_default_settings)


def register():
    """
    Register signals

    """

    signals.initialized.connect(init_default_config)
    signals.article_generator_context.connect(process_page_metadata)
    signals.page_generator_context.connect(process_page_metadata)
    signals.article_generator_finalized.connect(move_resources)

    signals.content_object_init.connect(bdates)

