"""
jquery and jqwebext
"""
import pkg_resources

from turbogears.widgets import CSSLink, JSLink, Widget, \
                               register_static_directory, \
                               WidgetDescription

js_dir = pkg_resources.resource_filename("jquery", "static")

register_static_directory("jquery", js_dir)

jquery_js = JSLink("jquery", "jquery-1.2.3.pack.js")
#import jquery only
jquery = jquery_js
