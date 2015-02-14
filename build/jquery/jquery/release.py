# Release information about jquery

version = "1.2.3"

description = "Jquery javascript library for TurboGears"
long_description = """

Feature
===============

jquery is a jquery javascript library wrapper and ajax helper for happy
TurboGears web designers.

Available widgets
====================

  * Jquery (basic jquery libray wrapper for Turbogears)

It also contains 3 extra ajax widgets based on jquery.

  * addCallback / link_to_remote(target ,update, href, callback)
        
  * addPeriodBack / periodically_call_remote(update, href, interval)

  * addFormback / form_remote_tag(target, update, href)

Which are inspired from Ruby on Rails/pquery and give them the twisted syntax.
    

Install
==============
Use setuptools to install::
    
    $easy_install jquery


Usage
==============

jquery
~~~~~~~~~

include in config/app.cfg::

    tg.include_widgets = ['jquery.jquery']

jquery ajax
~~~~~~~~~~~~~

import in controllers.py::

    from jquery import addCallback
    from jquery import addPeriodback
    from jquery import addFormback
    ....
    return dict(addCallback = addCallback, 
            addPeriodback = addPeriodback)

.. note:: 
    Update notice form 1.1.2 jquery widget: you need return dict(link = addPeriodback) instead of 
    return dict(link = addPeriodback()) in the following versions



in template::
    
    [div id="timelink"][a href = "#"]get time[/a][/div]
    [div id="timediv"][/div]
    ${addCallback(target="timelink" ,update="timediv", href="/time")}
    
or::

    [div id="timediv"][/div]
    ${addPeriodback(update="timediv", href="/time", interval="3000")}

or:: 

    [form class="timelink" action="ajax"  method="get" ]
       Field : [input type="text" name="field" /][br /]
       [input type="submit" /] 
    [/form]
    [div id="timediv"][/div]
    ${addFormback(target="timelink", update="timediv", href="ajax")}

The addCallback/addPeriodback could be placed anywhere in your template.
Check http://docs.turbogears.org/1.0/RemoteLink for detail.

Reference
============

    - jquery http://jquery.com
    - pquery http://www.ngcoders.com/pquery/

Source
============

Source is available in 

http://svn.turbogears.org/projects/tgJquery/trunk


History
=============

1.2.3:

  * update to jquery 1.2.3
  * host in TurboGears svn

1.2.2:

  * update to jquery 1.2.2
  
1.1.2w2: 

  * new twisted style ajax call
  * new addFormback/form_remote_tag call
  * passing ajax function no need extra '()' at all.


"""
author = "Fred Lin"
email = "gasolin+tg@gmail.com"
copyright = "Fred Lin 2007"

# if it's open source, you might want to specify these
# url = "http://yourcool.site/"
# download_url = "http://yourcool.site/download"
license = "MIT"
