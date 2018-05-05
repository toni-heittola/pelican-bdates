Pelican-bdates - Important date listings for Pelican
====================================================

`pelican-bdates` is an open source Pelican plugin to produce important date listings from yaml data structures. The plugin is developed to be used with Markdown content and Bootstrap 3 based template. 

**Author**

Toni Heittola (toni.heittola@gmail.com), [GitHub](https://github.com/toni-heittola), [Home page](http://www.cs.tut.fi/~heittolt/)

Installation instructions
=========================

## Requirements

**bs4** is required. To ensure that all external modules are installed, run:

    pip install -r requirements.txt

**bs4** (BeautifulSoup) for parsing HTML content

    pip install beautifulsoup4

In order to regenerate minified CSS and JS files you need also: 

**rcssmin** a CSS Minifier

    pip install rcssmin
    
**jsmin** a JS Minifier

    pip install jsmin

## Pelican installation

Make sure you include [Bootstrap](http://getbootstrap.com/) in your template.

Make sure the directory where the plugin was installed is set in `pelicanconf.py`. For example if you installed in `plugins/pelican-bdates`, add:

    PLUGIN_PATHS = ['plugins']

Enable `pelican-bdates` with:

    PLUGINS = ['pelican-bdates']

To allow plugin in include css file, one needs to add following to the `base.html` template, in the head:

    {% if article %}
        {% if article.styles %}
            {% for style in article.styles %}
    {{ style }}
            {% endfor %}
        {% endif %}
    {% endif %}
    {% if page %}
        {% if page.styles %}
            {% for style in page.styles %}
    {{ style }}
            {% endfor %}
        {% endif %}
    {% endif %}

Insert date listing in the page template:
 
    {% if page.bdates %}
        {{ page.bdates }}
    {% endif %}

Insert date listing in the article template:

    {% if article.bdates %}
        {{ article.bdates }}
    {% endif %}

Usage
=====

Date listing generation is triggered for the page either by setting BDATES metadata for the content (page or article) or using `<div>` with class `bdates`. 

There is two layout modes available for both of these: `panel` and `list`. 

## Date registry

Example yaml-file:

    - date: 9-11-2016
      title: Test 1
      category: category1
    - date: 1-12-2016
      duration_days: 10
      title: Test 2
      url: test2
      category: category2

## Parameters

The parameters can be set in global, and content level. Globally set parameters are are first overwritten content meta data, and finally with div parameters.

### Global parameters

Parameters for the plugin can be set in `pelicanconf.py' with following parameters:

| Parameter                 | Type      | Default       | Description  |
|---------------------------|-----------|---------------|--------------|
| BDATES_SOURCE             | String    |               | YAML-file to contain dates registry, see example format above. |
| BDATES_TEMPLATE           | Dict of Jinja2 templates |  | Two templates can be set for panel and list  |
| BDATES_ITEM_TEMPLATE      | Dict of Jinja2 templates |  | Two templates can be set for panel and list  |
| BDATES_PANEL_COLOR        | String    | panel-primary |  CSS class used to color the panel template in the default template. Possible values: panel-default, panel-primary, panel-success, panel-info, panel-warning, panel-danger |
| BDATES_CATEGORY_LABEL_CSS | Dict      |               | Dict with category labels as keys, second level dict with key`label-css`. |
| BDATES_HEADER             | String    | Content       | Header text  |
| BDATES_MINIFIED           | Boolean   | True          | Do we use minified CSS file. Disable in case of debugging.  |
| BDATES_GENERATE_MINIFIED  | Boolean   | False         | CSS file is minified each time, Enable in case of development.   |
| BDATES_DEBUG_PROCESSING   | Boolean   | False         | Show extra information in when run with `DEBUG=1` |

### Content wise parameters

| Parameter                 | Example value | Description  |
|---------------------------|---------------|--------------|
| BDATES                    | True          | Enable dates listing for the page | 
| BDATES_SOURCE             | content/data/dates.yaml | Dates registry file |
| BDATES_MODE               | panel         | Layout type, panel or list |
| BDATES_PANEL_COLOR        | panel-info    | CSS class used to color the panel template in the default template. Possible values: panel-default, panel-primary, panel-success, panel-info, panel-warning, panel-danger |
| BDATES_HEADER             | Personnel     | Header text  |
| BDATES_CATEGORY           | cat1, cat2    | Comma separated list of categories shown |
| BDATES_COUNT              | 3             | Count of most recent dates shown |
| BDATES_SHOW_CATEGORIES    | True          | Show category label |
| BDATES_DATE_FORMAT        | %d %B %Y      | Date format, see format supported by strftime |

Example:

    Title: Test page
    Date: 2017-01-05 10:20
    Category: test
    Slug: test-page
    Author: Test Person
    bdates: True
    bdates_header: Dates
    bdates_category: category1
    
Date listing is available in template in variable `page.bdates` or `article.bdates`
   
### Div wise parameters

| Parameter                 | Example value     | Description  |
|---------------------------|-------------|--------------|
| data-source               | content/data/dates.yaml | Date registry file
| data-mode                 | panel       | Layout type, panel or list |
| data-header               | Dates       | Header text |
| data-category             | cat1, cat2 | Comma separated list of categories shown |
| data-count                | 2 | Count of most recent dates shown |
| data-show-categories      | True | Show category label |
| data-date-format          | %d %B %Y | Date format, see format supported by strftime |
| data-panel-color          | panel-info | CSS class used to color the panel template in the default template. Possible values: panel-default, panel-primary, panel-success, panel-info, panel-warning, panel-danger |
Example listing:

    <div class="bdates" data-source="content/data/dates.yaml" data-category="category1" data-mode="panel" data-header="Important dates" data-date-format="%d %B %Y"></div>
        
Example with meta fields:   

    Title: Test page
    Date: 2017-01-05 10:20
    Category: test
    Slug: test-page
    Author: Test Person
    bdates: True
    bdates_category: category1
    bdates_header: Important dates
    bdates_panel_color: panel-default
    bdates_source: content/data/dates.yaml
    bdates_mode: panel
    <div class="bdates"></div>