#!/usr/bin/python

import binascii
import cgi
import cgitb; cgitb.enable()
import commands
import Cookie
import copy
import cPickle
import hashlib
import os
import subprocess
import sys
import urllib

os.umask(0077);

def cl(message):
    open('/tmp/cl', 'a').write(repr(message) + '\n')

try:
    import cracklib
    cracklib_available = True
except:
    cracklib_available = False

hashing_scheme = 'sha512'

dirname = os.path.dirname(os.path.dirname(__file__))

def check_user(username, password):
    filename = os.path.join(dirname, 'database', 'users',
      binascii.hexlify(username))
    if os.path.isfile(filename):
        hashing_scheme, salt, stored_password = (
          open(filename).read().split('-'))
        workbench = hashlib.new(hashing_scheme)
        workbench.update(salt + binascii.hexlify(password))
        if stored_password == workbench.hexdigest():
            return ''
        else:
            return 'Password is incorrect.'
    else:
        return 'User does not exist.'

cgi_form = cgi.FieldStorage()

def get_cgi(field, default = ''):
    if cgi_form.has_key(field):
        if type(cgi_form[field]) == type([]):
            return cgi_form[field][0].value
        else:
            return cgi_form[field].value
    else:
        return default

username = get_cgi('username')
password = get_cgi('password')
escaped_username = ''
escaped_password = ''
if check_user(username, password) == '':
    print 'Set-Cookie: username=' + binascii.hexlify(username);
    print 'Set-Cookie: password=' + binascii.hexlify(password);
else:
    if 'HTTP_COOKIE' in os.environ:
        cookie_string = os.environ.get('HTTP_COOKIE')
        cookie = Cookie.SimpleCookie()
        cookie.load(cookie_string)
        try:
            username = binascii.unhexlify(cookie['username'].value)
            password = binascii.unhexlify(cookie['password'].value)
            if check_user(username, password) != '':
                username = ''
                password = ''
        except:
            username = ''
            password = ''

stored = {}
stored['logged_in'] = 'false'
stored['username'] = username
stored['password'] = password
if get_cgi('stay_logged_in'):
    stored['stay_logged_in'] = 'true'
else:
    stored['stay_logged_in'] = 'false'
stored['logged_in'] = 'false'
stored['monolith'] = ''
if check_user(username, password):
    filename = os.path.join(dirname, 'pickled', binascii.hexlify(username))
    try:
        stored['monolith'] = binascii.unhexlify(open(filename).read())
        stored['logged_in'] = 'true';
    except IOError, ioe:
        pass
    try:
        saved = cPickle.load(open(filename))
    except IOError:
        saved = {
          'companies': [],
          'hours': [],
          'notes': [],
          }
        filename = os.path.join(dirname, 'database/key-value',
          binascii.hexlify(username) + '-' +
          binascii.hexlify('monolith'))
        stored['logged_in'] = 'true'

escaped = {}

for key in stored.keys():
    escaped[key] = stored[key].replace('\\', '\\\\').replace("'", "\\'")

scripts = '''
    <script>
        'use strict';
        ;var clone = function(original)
            {
            // console.log('clone');
            var literal_types = ['undefined'];
            for(var index = 0; index < literal_types.length; ++index)
                {
                if (typeof original === literal_types[index] ||
                  original === literal_types[index])
                    {
                    return original;
                    }
                }
            return JSON.parse(JSON.stringify(original));
            }
        var compare_json = function(first, second)
            {
            // console.log('compare_json');
            return JSON.stringify(first) === JSON.stringify(second);
            }
        var contact_initialized = false;
        var ran_once = false;
        var drilldown = null;
        jQuery('body').tooltip();
        jQuery('#tabs').tabs();
        jQuery('#tabs').on('tabsactivate', function(event, ui)
            {
            var workbench = '' + ui['newTab']['context'];
            var marker = workbench.indexOf('#');
            workbench = workbench.slice(marker);
            if (workbench === '#tabs-view')
                {
                display_not_edit = true;
                }
            else
                {
                display_not_edit = false;
                }
            });
        var display_not_edit = false;
        var cmp = function(first, second)
            {
            // console.log(cmp)
            if (typeof first !== typeof second)
                {
                return cmp(typeof first, typeof second);
                }
            else if (first > second)
                {
                return 1;
                }
            else if (first < second)
                {
                return -1;
                }
            else
                {
                return 0;
                }
            };
        var display_lightbox = function(url)
            {
            // console.log('display_lightbox');
            jQuery('#lightbox').show();
            jQuery('#lightbox-contents').show();
            jQuery('#lightbox-contents').html('<iframe src="' + url +
              '"></iframe>');
            return false;
            }
        var monolith;
        var pickled_monolith = '%(monolith)s';
        var logged_in = '%(logged_in)s';
        if (logged_in)
            {
            jQuery('#login').hide();
            jQuery('#login_offer').hide();
            jQuery('#logout').show();
            }
        else
            {
            jQuery('#login').show();
            jQuery('#login_offer').hide();
            jQuery('#logout').show();
            }
        if (logged_in || localStorage['monolith'])
            {
            jQuery('#tabs').tabs('option', 'active', 1);
            }
        var guid = 0;
        var username = '%(username)s';
        var password = '%(password)s';
        var monolith_restored_from_localstorage = false;
        var define_monolith = function()
            {
            // console.log('define_monolith');
            if (typeof monolith === 'undefined' || !monolith)
                {
                if (localStorage['monolith'] &&
                  JSON.parse(localStorage['monolith']) &&
                  localStorage['monolith'] !== 'null')
                    {
                    monolith_restored_from_localstorage = true;
                    monolith = JSON.parse(localStorage['monolith']);
                    }
                else
                    {
                    monolith = {
                      'companies': [],
                      'last-modified': [],
                      'next-guid': 0,
                      'pickled': [],
                      'statistics': []
                      };
                    }
                }
            };
        define_monolith();
        var save = function(event)
            {
            // console.log('save');
            if (typeof event !== 'undefined')
                {
                event.preventDefault();
                }
            if (JSON.stringify(monolith) !== previous_monolith)
                {
                previous_monolith = JSON.stringify(monolith);
                localStorage['monolith'] = previous_monolith;
                if (logged_in && username && password)
                    {
                    jQuery.ajax({
                        'data':
                            {
                            'monolith': JSON.stringify(monolith),
                            'mode': 'save',
                            'password': password,
                            'username': username
                            },
                        'method': 'POST',
                        'error': function(jqXHR)
                            {
                            // jQuery('#error-banner').html(jqXHR.responseText);
                            },
                        'url': ''
                        });
                    }
                }
            };
        if (monolith && logged_in && !pickled_monolith)
            {
            save();
            }
        var add_new = function()
            {
            // console.log('add_new');
            (monolith['companies'][guid]
              = extract_current_company(create_company_if_not_exists(guid)));
            save();
            var identifier = monolith['next-guid'];
            guid = identifier;
            var company = create_company_if_not_exists(guid);
            monolith['companies'][identifier] = company;
            monolith['companies'][identifier]['guid'] = identifier;
            monolith['next-guid'] = identifier + 1;
            render_company(company);
            save();
            jQuery('#tabs').tabs('option', 'active', 1);
            return false;
            }
        var add_statistics_entry = function()
            {
            // console.log('add_statistics_entry');
            if (document.getElementById('hours').value === '0' &&
              document.getElementById('job-postings').value === '0' &&
              document.getElementById('networking').value === '0' &&
              document.getElementById('interviews').value === '0' &&
              document.getElementById('offers').value === '0' &&
              document.getElementById('comments').value === '')
                {
                return;
                }
            var to_save = {};
            (to_save['hours'] =
              parseInt(document.getElementById('hours').value), 10);
            (to_save['job-postings'] =
              parseInt(document.getElementById('job-postings').value), 10);
            (to_save['networking'] =
              parseInt(document.getElementById('networking').value), 10);
            (to_save['interviews'] =
              parseInt(document.getElementById('interviews').value), 10);
            (to_save['offers'] =
              parseInt(document.getElementById('offers').value), 10);
            (to_save['comments'] =
              document.getElementById('comments').value);
            to_save['timestamp'] = new Date().getTime();
            monolith['statistics'].push(to_save);
            save();
            document.getElementById('hours').value = '0';
            document.getElementById('job-postings').value = '0';
            document.getElementById('networking').value = '0';
            document.getElementById('interviews').value = '0';
            document.getElementById('offers').value = '0';
            document.getElementById('comments').value = '';
            draw_graph();
            return false;
            }
        var add_statistics_questions = function()
            {
            // console.log('add_statistics_questions');
            var workbench = [];
            if (typeof monolith['statistics'] === 'undefined')
                {
                monolith['statistics'] = [];
                save();
                }
            if (monolith['statistics'].length)
                {
                var last_entry = new Date(monolith['statistics'][length - 1
                  ]['timestamp']);
                var month = last_entry.getMonth() + 1;
                if (month < 10)
                    {
                    month = '0' + month;
                    }
                var date = last_entry.getDate();
                if (date < 10)
                    {
                    date = '0' + date;
                    }
                var last_entry_date = (last_entry.
                  getFullYear() + '-' + month + '-' + date);
                var today = new Date();
                var month = today.getMonth() + 1;
                if (month < 10)
                    {
                    month = '0' + month;
                    }
                var date = today.getDate();
                if (date < 10)
                    {
                    date = '0' + date;
                    }
                var date_of_application = (today.
                  getFullYear() + '-' + month + '-' + date);
                if (last_entry_date === today)
                    {
                    workbench.push('<p><strong>Welcome back! You last ' +
                      'entered your numbers <em>earlier today' +
                      '</em>.</strong></p>');
                    }
                else
                    {
                    workbench.push('<p><strong>Welcome back! You last ' +
                      'entered your numbers <em>' + last_entry_date + +
                      '</em>.</strong></p>');
                    }
                }
            else
                {
                workbench.push('<p><em><strong>Welcome to statistics to help you keep on track!</strong></em></p>');
                workbench.push('<p><strong>Fill this out weekly, perhaps on Fridays, or maybe every few days.</strong></p>');
                }
            workbench.push('<form name="statistics" id="statistics">');
            workbench.push('<table class="statistics">');
            workbench.push('<tbody>');
            workbench.push('<tr>');
            workbench.push('<th>Hours you have spent in your job search</th>');
            workbench.push('<td>');
            workbench.push('<input type="number" min="0" name="hours" id="hours" value="0" />');
            workbench.push('</td>');
            workbench.push('</tr>');
            workbench.push('<tr>');
            workbench.push('<th>Number of job postings you responded to</th>');
            workbench.push('<td>');
            workbench.push('<input type="number" step="1" min="0" name="job-postings" id="job-postings" value="0" />');
            workbench.push('</td>');
            workbench.push('</tr>');
            workbench.push('<tr>');
            workbench.push('<th>Number of networking connections you made</th>');
            workbench.push('<td>');
            workbench.push('<input type="number" step="1" min="0" name="networking" id="networking" value="0" />');
            workbench.push('</td>');
            workbench.push('</tr>');
            workbench.push('<tr>');
            workbench.push('<th>Number of interviews</th>');
            workbench.push('<td>');
            workbench.push('<input type="number" step="1" min="0" name="interviews" id="interviews" value="0" />');
            workbench.push('</td>');
            workbench.push('</tr>');
            workbench.push('<tr>');
            workbench.push('<th>Number of offers</th>');
            workbench.push('<td>');
            workbench.push('<input type="number" step="1" min="0" name="offers" id="offers" value="0" />');
            workbench.push('</td>');
            workbench.push('</tr>');
            workbench.push('<tr>');
            workbench.push('<th>Notes or comments</th>');
            workbench.push('<td>');
            workbench.push('<textarea name="comments" id="comments"></textarea>');
            workbench.push('</td>');
            workbench.push('</tr>');
            workbench.push('</tbody>');
            workbench.push('</table>');
            workbench.push('</form>');
            workbench.push('<div class="button"><a class="button" ' +
              'href="javascript:add_statistics_entry(); draw_graph();" ' +
              'onclick="add_statistics_entry(); draw_graph();">' +
              'Save and graph</a></div>');
            draw_graph();
            return workbench.join('');
            }
        var edit_existing = function(identifier)
            {
            // console.log('edit_existing');
            var company = monolith['companies'][identifier];
            display_not_edit = false;
            document.getElementById('name').value = company['name'];
            (document.getElementById('description').value = company['description']);
            jQuery('#notes').html(render_company(extract_current_company(
              company)));
            jQuery('#tabs').tabs('option', 'active', 1);
            return false;
            }
        var render_company = function(company)
            {
            // console.log('render_company');
            var html = prerender_company(company)['html'];
            jQuery('#notes').html(html);
            // jQuery('.repeating').blur(add_any_needed_entry);
            // jQuery('.repeating').click(add_any_needed_entry);
            // jQuery('.repeating').focus(add_any_needed_entry);
            // jQuery('.repeating').keydown(add_any_needed_entry);
            // jQuery('.repeating').keypress(add_any_needed_entry);
            // jQuery('.repeating').keyup(add_any_needed_entry);
            if (jQuery('[type="date"]').prop('type') != 'date')
                {
                jQuery('[type="date"]').datepicker();
                }
            jQuery(document).tooltip();
            };
        var create_company_if_not_exists = function(identifier)
            {
            // console.log('create_company_if_not_exists');
            if (typeof monolith['companies'][identifier] === 'undefined')
                {
                guid = parseInt(monolith['next-guid']);
                monolith['next-guid'] += 1;
                var workbench = {};
                workbench['email'] = [];
                workbench['name'] = '';
                workbench['phone'] = [];
                workbench['other'] = [];
                workbench['skype'] = [];
                workbench['url'] = [];
                workbench['update'] = [];
                workbench['updatetimestamp'] = [];
                var today = new Date();
                var month = today.getMonth() + 1;
                if (month < 10)
                    {
                    month = '0' + month;
                    }
                var date = today.getDate();
                if (date < 10)
                    {
                    date = '0' + date;
                    }
                var date_of_application = (today.
                  getFullYear() + '-' + month + '-' + date);
                (workbench['date-of-application'] =
                  date_of_application);
                workbench['use-reminders'] = true;
                workbench['reminder-date'] = date_of_application;
                workbench['reminder-weeks'] = 1;
                workbench['guid'] = identifier;
                monolith['companies'][identifier] = workbench;
                save();
                }
            return monolith['companies'][identifier];
            };
        var extract_current_company = function(identifier)
            {
            var workbench = {};
            // console.log('extract_current_company');
            var company = create_company_if_not_exists(identifier);
            if (document.getElementById('name'))
                {
                (workbench['name'] =
                  document.getElementById('name').value);
                }
            else
                {
                workbench['name'] = '';
                }
            if (document.getElementById('description'))
                {
                (workbench['description'] =
                  document.getElementById('description').value);
                }
            if (document.getElementById('observation'))
                {
                (workbench['observation'] =
                  document.getElementById('observation').value);
                }
            workbench['update'] = [];
            workbench['updatetimestamp'] = [];
            var count = 0;
            while (jQuery('#update' + count).length)
                {
                if (workbench['updatetimestamp'].indexOf(Number(document.getElementById('update'
                  + count))) !== -1)
                    {
                    (workbench['update'][count] =
                      document.getElementById('update' + count));
                    (workbench['updatetimestamp'][count] =
                      document.getElementById('updatetimestamp' +
                      count));
                    }
                count += 1;
                }
            workbench['contactperson'] = [];
            for(var index = 0;
              document.getElementById('contactperson' + (index)) &&
              document.getElementById('contactperson'
              + (index)).value; index += 1)
                {
                workbench['contactperson'][index] = (
                  document.getElementById('contactperson' +
                  index).value);
                }
            if (document.getElementById('contactperson' + [index -
                1]))
                {
                workbench['contactperson'][index] = (
                  document.getElementById('contactperson' +
                  index).value);
                }
            var statuses = ['active', 'background', 'closed',
              'important', 'in-progress', 'problems', 'thank-you'];
            for(var index = 0; index < statuses.length; index += 1)
                {
                if (document.getElementById('status') &&
                  document.getElementById(status).value)
                    {
                    workbench[status] = true;
                    }
                else
                    {
                    workbench[status] = false;
                    }
                }
            for(var index = 0;
              index === 0 ||
              document.getElementById('email' + (index - 1)) &&
              document.getElementById('email' + (index - 1)).value;
              index += 1)
                {
                if (typeof workbench['email'] === 'undefined')
                    {
                    workbench['email'] = [];
                    save();
                    }
                if (document.getElementById('email' + index))
                    {
                    (workbench['email'][index] =
                      document.getElementById('email' +
                      index).value);
                    }
                else
                    {
                    workbench['email'][index] = '';
                    }
                }
            for(var index = 0;
              index === 0 ||
              document.getElementById('phone' + (index - 1)) &&
              document.getElementById('phone' + (index - 1)).value;
              index += 1)
                {
                if (document.getElementById('phone' + index))
                    {
                    if (typeof workbench['phone'] === 'undefined')
                        {
                        workbench['phone'] = [];
                        save();
                        }
                    workbench['phone'][index] = (
                      document.getElementById('phone' +
                      index).value);
                    }
                else
                    {
                    var should_save = false;
                    if (typeof workbench['phone'] === 'undefined')
                        {
                        workbench['phone'] = [];
                        should_save = true;
                        }
                    if (typeof workbench['phone'][index] === 'undefined')
                        {
                        workbench['phone'][index] = ('');
                        should_save = true;
                        }
                    if (should_save)
                        {
                        save();
                        }
                    }
                }
            for(var index = 0;
              index === 0 ||
              document.getElementById('skype' + (index - 1)) &&
              document.getElementById('skype' + (index - 1)).value;
              index += 1)
                {
                if (document.getElementById('skype' + index))
                    {
                    if (typeof workbench['skype'] === 'undefined')
                        {
                        workbench['skype'] = [];
                        save();
                        }
                    workbench['skype'][index] = (
                      document.getElementById('skype' +
                      index).value);
                    }
                else
                    {
                    if (typeof workbench['skype'] === 'undefined')
                        {
                        workbench['skype'] = [];
                        should_save = true;
                        }
                    if (typeof workbench['skype'][index] === 'undefined')
                        {
                        workbench['skype'][index] = ('');
                        should_save = true;
                        }
                    if (should_save)
                        {
                        save();
                        }
                    }
                }
            for(var index = 0;
              index === 0 ||
              document.getElementById('url' + (index - 1)) &&
              document.getElementById('url' + (index - 1)).value;
              index += 1)
                {
                if (document.getElementById('url' + index))
                    {
                    if (typeof workbench['url'] === 'undefined')
                        {
                        workbench['url'] = [];
                        save()
                        }
                    workbench['url'][index] = (
                      document.getElementById('url' +
                      index).value);
                    }
                else
                    {
                    if (typeof workbench['url'] === 'undefined')
                        {
                        workbench['url'] = [];
                        should_save = true;
                        }
                    if (typeof workbench['url'][index] === 'undefined')
                        {
                        workbench['url'][index] = ('');
                        should_save = true;
                        }
                    if (should_save)
                        {
                        save();
                        }
                    }
                }
            for(var index = 0;
              index === 0 ||
              document.getElementById('other' + (index - 1)) &&
              document.getElementById('other' + (index - 1)).value;
                index += 1)
                    {
                    if (document.getElementById('other' + index))
                        {
                        if (typeof workbench['other'] === 'undefined')
                            {
                            workbench['other'] = [];
                            save();
                            }
                        (workbench['other'][index] =
                        document.getElementById('other' + index).value);
                        }
                    }
            workbench['update'] = [];
            for(var index = 0; index === 0 ||
              document.getElementById('update' + (index - 1)) &&
              document.getElementById('update' + (index - 1)).value;
              index += 1)
                {
                if (document.getElementById('update' + index))
                    {
                    workbench['update'][index] = (
                      document.getElementById('update' +
                      index).value);
                    }
                if (typeof workbench['updatetimestamp'][index]
                  === 'undefined')
                    {
                    (workbench['updatetimestamp'][index] = new
                      Date().getTime());
                    }
                }
            var flags = ['active', 'background', 'closed', 'important',
              'in-progress', 'problems', 'thank-you'];
            for(var index = 0; index < flags.length; index += 1)
                {
                if (document.getElementById(flags[index]) &&
                  document.getElementById(flags[index]).checked)
                    {
                    workbench[flags[index]] = true;
                    }
                }
            monolith.companies[identifier] = workbench;
            return workbench;
            };
        var edit = function(identifier)
            {
            // console.log('edit');
            for(var index = 0; index < monolith['companies'].length;
              index += 1)
                {
                if (monolith['companies'][index]['guid'] === identifier)
                    {
                    display_not_edit = false;
                    jQuery('#notes').html(prerender_company(monolith['companies'][index])['html']);
                    jQuery('#tabs').tabs('option', 'active', 0);
                    }
                }
            }
        var add_additional_entry = function(identifier, guid)
            {
            // console.log('add_additional_entry');
            var company;
            var workbench = [];
            for(var index = 0; index < monolith['companies'].length;
              index += 1)
                {
                if (typeof monolith['companies'][index] !== 'undefined' &&
                  monolith['companies'][index] !== null &&
                  monolith['companies'][index]['guid'] === guid)
                    {
                    company = monolith['companies'][index];
                    }
                }
            length = 1;
            var contact_details = ['contactperson', 'url', 'email', 'phone', 'skype', 'other'];
            for(var index = 0; index < contact_details.length;
              index += 1)
                {
                var contact = contact_details[index];
                if (typeof company[contact] === 'undefined')
                    {
                    company[contact] = [];
                    save();
                    }
                else
                    {
                    length = Math.max(length,
                      company[contact].length);
                    }
                }
            var placeholder = {
              "contactperson": "The name of a contact person, and anything else you'd like to keep track of.",
              "update": "What just happened that you want a record of?",
              "url": "E.g. &quot;CJSHayward.com&quot;",
              "email": "This contact's email address.",
              "phone": "This contact's phone number.",
              "skype": "This person's Skype ID.",
              "other": "Any other contact information you may wish to keep for this person."
              };
            var types = {
              "url": "url",
              "email": "email",
              "phone": "tel"
              };
            var display_names = {
              "contactperson": "Contact person:",
              "update": "Update:",
              "url": "URL:",
              "email": "Email address:",
              "phone": "Phone number:",
              "skype": "Skype ID:",
              "other": "Any other contact information:"
              };
            if (identifier === 'contactperson')
                {
                for(var outer = 0; outer < length; outer += 1)
                    {
                    for(var inner = 0; inner < contact_details.length;
                      inner += 1)
                        {
                        var contact = contact_details[inner];
                        if (typeof company[outer] === 'undefined')
                            {
                            company[outer] = [];
                            save();
                            }
                        if (typeof company[outer][contact] !== 'undefined' &&
                          company[outer][contact].length)
                            {
                            var data = company[outer][contact];
                            }
                        else
                            {
                            var data = '';
                            }
                        workbench.push('<strong>' + display_names[contact] +
                          '</strong><br />');
                        if (contact === 'contactperson' || contact === 'other' ||
                          contact === 'update')
                            {
                            workbench.push('<textarea class="' + contact +
                              '" name="' + contact + outer +
                              '" id="' + contact + outer +
                              '" placeholder="' + placeholder[contact] +
                              '" value="' + sanitize(data) + '"></textarea>');
                            }
                        else
                            {
                            if (types[contact])
                                {
                                var input_type = types[contact];
                                }
                            else
                                {
                                var input_type = 'text';
                                }
                            workbench.push('<input type="' + input_type +
                              '" name="' + contact + outer + '" id="' + contact +
                              outer + '" value="' + sanitize(data) +
                              '" placeholder="' + placeholder[contact] +
                              '" class="contact-detail" />');
                            }
                        }
                    }
                }
            else
                {
                if (identifier === 'update')
                    {
                    workbench.push('<textarea class="' + contact +
                      '" name="' + contact + outer +
                      '" id="' + contact + outer +
                      '" placeholder="' + placeholder[identifier] +
                      '" value=""></textarea>');
                    }
                else
                    {
                    workbench.push('<input type="' + input_type +
                      '" name="' + contact + outer + '" id="' + contact +
                      outer + '" value="' + sanitize(data) +
                      '" placeholder="' + placeholder[identifier] +
                      '" class="contact-detail" />');
                    }
                }
            jQuery('div#repeat-' + identifier).append(workbench.join(''));
            };
        var add_any_needed_entry = function(event)
            {
            // console.log('add_any_needed_entry');
            var target = event.target;
            var identifier;
            var raw = jQuery(target).attr('id');
            if (!jQuery(target).attr('id'))
                {
                return;
                }
            identifier = jQuery(target).attr('id').replace(/\d/g, '');
            var number = Number(jQuery(target).attr('id'
              ).replace(/[^\d]*/g, ''));
            var next = number + 1;
            var plustwo = number + 2;
            if ((jQuery('#' + identifier + next).length ||
              jQuery('#' + identifier + plustwo).length))
                {
                return;
                }
            for(var existing_index = 0;
              (existing_index === 0 || typeof jQuery('#' + identifier +
              (existing_index - 1)).val() !== 'undefined') && typeof
              jQuery('#' + identifier).val() === 'undefined';
              existing_index += 1);
            next_slot = existing_index - 1;
            var template = jQuery('#repeat-' +
              identifier).attr('data-new-entry');
            if (typeof template === 'undefined')
                {
                return;
                }
            var container;
            if (template.substr(0, 9) === '<textarea' &&
              jQuery('#update' + existing_index).val() &&
              !jQuery('#update' + (existing_index + 1)).size())
                {
                template = template.replace(/\?/g, '' + next_slot);
                var timestamp = new Date().getTime();
                (container = '<span id="' + timestamp +
                  '" style="display: none;">' + template +
                  '</span>');
                jQuery('#repeat-update').append(container);
                jQuery('#' + timestamp).show('slow');
                }
            else
                {
                var identifier_template = template.replace(/\?/g,
                  'comment' + next_slot);
                identifier_template = identifier_template.replace(
                  '<input', '<input value="" class="comment"');
                identifier_template += '<br />';
                template = template.replace(/\?/g, '' + next_slot);
                var timestamp = new Date().getTime();
                (container = '<span id="' + timestamp +
                  '" style="display: none;">' + template + '</span>');
                jQuery('#repeat-' + identifier).append(container);
                jQuery('#' + timestamp).show('slow');
                if (jQuery('textarea#' + identifier + number).length &&
                jQuery('textarea#' + identifier + number).val())
                    {
                    var timestamp = new Date().getTime();
                    (container = '<span id="' + timestamp +
                      '" style="display: none;">' + identifier_template + '</span>');
                    jQuery('#repeat-' +
                      identifier).append(container);
                    jQuery('#' + timestamp).show('slow');
                    }
                }
            if (typeof monolith['companies'][number] !== 'undefined' &&
              monolith['companies'][number] !== null &&
              typeof monolith['companies'][number]['timestamp'] !==
              'undefined')
                {
                (monolith['companies'][number]['timestamp'] = new Date()
                  .getTime());
                }
            };
            var converter = new showdown.Converter();
            var preprocess = function(raw)
                {
                // console.log('preprocess');
                if (!raw)
                    {
                    return '';
                    }
                var workbench = '';
                for(var index = 0; index < raw.length; index += 1)
                    {
                    workbench += raw[index];
                    }
                return converter.makeHtml(workbench);
                };
            var sanitize = function(raw)
                {
                // console.log('sanitize');
                if (!raw)
                    {
                    return '';
                    }
                var workbench = '';
                for(var index = 0; index < raw.length; index += 1)
                    {
                    workbench += raw[index];
                    }
                workbench = workbench.replace(/&/g, '&amp;');
                workbench = workbench.replace(/"/g, '&quot;');
                workbench = workbench.replace(/'/g, '&apos;');
                workbench = workbench.replace(/\\\\/g, '\\\\\\\\');
                workbench = workbench.replace(/</g, '&lt;');
                workbench = workbench.replace(/>/g, '&gt;');
                return workbench;
                };
            var draw_graph = function()
                {
                // console.log('draw_graph');
                if (typeof monolith['statistics'] === 'undefined' ||
                  monolith['statistics'].length < 6)
                    {
                    jQuery('#graph').html('<p><strong>You should see a useful graph right here, <em>once you\\\'ve added a few entries.</em></strong> (Be patient. The graph will show up soon.)</p>');
                    return;
                    }
                var workbench = [];
                workbench.push('<table class="graph" cellpadding="0" cellspacing="0">');
                workbench.push('<tbody>');
                var display_names = ['Hours', 'Job postings',
                  'Networking connections', 'Interviews', 'Offers'];
                var keys = ['hours', 'job-postings', 'networking',
                  'interviews', 'offers'];
                var default_values = false;
                for(var outer = 0; outer < keys.length; outer += 1)
                    {
                    workbench.push('<tr>');
                    workbench.push('<th>');
                    workbench.push(display_names[outer]);
                    workbench.push('</th>');
                    var previous_timestamp = null;
                    var maximum = 1;
                    for(var inner = 0; inner <
                      monolith['statistics'].length; inner += 1)
                        {
                        if (monolith['statistics'][inner][keys[outer]] >
                          maximum)
                            {
                            (maximum =
                              monolith['statistics'][inner][keys[outer]]);
                            }
                        (previous_timestamp =
                          monolith['statistics'][inner]['timestamp']);
                        }
                    var height = 100;
                    previous_timestamp = null;
                    for(var inner = 0; inner <
                      monolith['statistics'].length; inner += 1)
                        {
                        var ratio;
                        if (monolith['statistics'].length < 2)
                            {
                            ratio = .5;
                            }
                        else
                            {
                            (ratio =
                              monolith['statistics'][inner][keys[outer]] /
                              maximum);
                            }
                        var formatted_date;
                        (formatted_date = new
                          Date(monolith['statistics'][inner]['timestamp'
                          ]).toLocaleString());
                        if
                          (sanitize(monolith['statistics'][inner]['comments']))
                            {
                            workbench.push(
                              '<td style="background-color: white; '
                              + 'height: 100px; border-bottom: 2px solid black;" title="'
                              + sanitize(monolith['statistics']
                              [inner]['comments']) + ', ' + formatted_date + '">');
                            }
                        else
                            {
                            workbench.push(
                              '<td style="background-color: white; '
                              + 'height: 100px; border-bottom: 2px solid black;" title="'
                              + formatted_date + '">');
                            }
                        workbench.push(
                          '<div style="background-color: white; height: '
                          + (height * (1 - ratio)) +
                          'px; width: 100%%;"></div>');
                        workbench.push(
                          '<div style="background-color: black; height: ' +
                          (height * ratio) + 'px; width: 100%%;"></div>');
                        workbench.push('</td>');
                        (previous_timestamp =
                          monolith['statistics'][inner][
                          'timestamp']);
                        }
                    workbench.push('</tr>');
                    workbench.push('<tr>');
                    for(var inner = 0; inner <
                      monolith['statistics'].length + 1; inner += 1)
                        {
                        workbench.push('<td height="1em;" style="background-color: white;">&nbsp;</td>');
                        }
                    workbench.push('</tr>');
                    }
                workbench.push('</tbody>');
                workbench.push('</table>');
                jQuery('#graph').html(workbench.join(''));
                jQuery('#graph').tooltip();
                }
            var remove_empty = function(arr)
                {
                // console.log('remove_empty');
                var empty_found = false;
                var result = [];
                if (typeof arr === 'undefined' || typeof arr === 'null')
                    {
                    return;
                    }
                if (arr.length)
                    {
                    result.push(arr[0]);
                    }
                for(var index = 1; index < arr.length; index += 1)
                    {
                    if (arr[index])
                        {
                        result.push(arr[index]);
                        }
                    else
                        {
                        if (!empty_found)
                            {
                            result.push(arr[index]);
                            empty_found = true;
                            }
                        }
                    }
                return result;
                }
            var prerender_company = function(company, display_only)
                {
                var found = null;
                if (typeof company === 'number')
                    {
                    for(var index = 0; index < monolith['companies'].length;
                      index += 1)
                        {
                        if (monolith['companies'] &&
                          monolith['companies'][index] &&
                          monolith['companies'][index]['guid'] === company)
                            {
                            found = monolith['companies'][index];
                            console.log(found);
                            }
                        }
                    }
                if (found)
                    {
                    company = found;
                    }
                // console.log('prerender_company' + company['guid'] + ',' +
                  // guid);
                if (typeof display_only === 'undefined' ||
                  typeof display_only === 'null')
                    {
                    display_only = display_not_edit;
                    }
                if (typeof company === 'undefined' || company === null)
                    {
                    company = create_company_if_not_exists();
                    }
                var workbench = [];
                workbench.push('<table>');
                workbench.push('<tbody>');
                if (display_only)
                    {
                    workbench.push('<tr>');
                    workbench.push('<th>Company name</th>');
                    workbench.push('<td>');
                    workbench.push('<a href="javascript:edit_existing( ' +
                    company['guid'] + '); jQuery(\\\'#tabs\\\').tabs(\\\'option\\\', \\\'active\\\', 1);">');
                    // console.log('Company name: ' +
                      // JSON.stringify([company['name']]));
                    // console.log(company);
                    if (typeof company['name'] !== 'undefined' &&
                      company['name'].length)
                        {
                        workbench.push(preprocess(company['name']));
                        }
                    else
                        {
                        workbench.push('Anonymous company');
                        }
                    workbench.push('</a>');
                    workbench.push('</td>');
                    workbench.push('</tr>');
                    if (typeof company['description']
                      !== 'undefined' && company['description'].length)
                        {
                        workbench.push('<tr>');
                        workbench.push('<th>Description</th>');
                        workbench.push('<td>');
                        workbench.push(preprocess(company['description']))
                        workbench.push('</td>');
                        workbench.push('</tr>');
                        }
                    if (typeof company['contactperson'] !== 'undefined' &&
                      company['contactperson'].length)
                        {
                        workbench.push('<tr>');
                        if (company['contactperson'].length === 1)
                            {
                            workbench.push('<th>Contact person</th>');
                            workbench.push('<td>');
                            }
                        else
                            {
                            workbench.push('<th>Contact people</th>');
                            workbench.push('<td>');
                            var instances = [];
                            for(var index = 0; index <
                              company['contactperson'].length; index += 1)
                                {
                                if (company['contactperson'][index])
                                    {
                                    instances.unshift(sanitize(company['contactperson'][index]));
                                    }
                                }
                            workbench.push(instances.join(', '));
                            }
                        var instances = [];
                        for(var index = 0; index <
                          company['contactperson'].length; index += 1)
                            {
                            if (company['contactperson'][index])
                                {
                                instances.unshift(sanitize(company['contactperson'][index]));
                                }
                            }
                        workbench.push(instances.join(', '));
                        workbench.push('</td>');
                        workbench.push('</tr>');
                        }
                    if (typeof company['observation'] !== 'undefined' &&
                      company['observation'].length)
                        {
                        workbench.push('<tr>');
                        workbench.push('<th>Notes</th>');
                        workbench.push('<td>');
                        workbench.push(sanitize(company['observation']));
                        workbench.push('</td>');
                        workbench.push('</tr>');
                        }
                    var nonempty_update_found = false;
                    var slimmer_updates = [];
                    if (company['update'])
                        {
                        for(var index = 0; index < company['update'].length;
                          index += 1)
                            {
                            if (company['update'][index])
                                {
                                nonempty_update_found = true;
                                slimmer_updates.push([company['update'][index],
                                  company['updatetimestamp'][index]]);
                                }
                            }
                        }
                    if (nonempty_update_found)
                        {
                        for(var index = 0; index < slimmer_updates.length;
                          index += 1)
                            {
                            var individual = slimmer_updates[index][0];
                            (individual =
                              individual.replace('\\r\\n\\r\\n',
                              '</p><p class="update">'));
                            (individual = individual.replace('\\r\\n',
                              '<br />'));
                            (individual = '<p class="update">' + individual
                              + '</p>');
                            workbench.push(individual);
                            var timestamp;
                            (timestamp = new
                              Date(slimmer_updates[index][1]));
                            var month = timestamp.getMonth() + 1;
                            if (month < 10)
                                {
                                month = '0' + month;
                                }
                            var date = timestamp.getDate();
                            if (date < 10)
                                {
                                date = '0' + date;
                                }
                            workbench.push('<p class="timestamp">' +
                              timestamp.getFullYear() + '-' + month + '-' +
                              date + '</p>');
                            }
                        }
                    var nonempty_url_found = false;
                    if (company['url'])
                        {
                        for(var index = 0; index < company['url'].length;
                          index += 1)
                            {
                            if (company['url'][index])
                                {
                                nonempty_url_found = true;
                                }
                            }
                        }
                    var toggles = [];
                    if (company['active'])
                        {
                        toggles.push('Active');
                        }
                    if (company['background'])
                        {
                        toggles.push('Background');
                        }
                    if (company['closed'])
                        {
                        toggles.push('Closed');
                        }
                    if (company['important'])
                        {
                        toggles.push('Important');
                        }
                    if (company['in-progress'])
                        {
                        toggles.push('In progress');
                        }
                    if (company['problems'])
                        {
                        toggles.push('Problems');
                        }
                    if (company['thank-you'])
                        {
                        toggles.push('Thank-you note sent.');
                        }
                    if (toggles)
                        {
                        workbench.push('<tr>');
                        workbench.push('<td>');
                        workbench.push(toggles.join(', '));
                        workbench.push('</td>');
                        workbench.push('</tr>');
                        }
                    
                    workbench.push('<tr>');
                    workbench.push('<th>Date of application</th>');
                    workbench.push('<td>');
                    workbench.push(sanitize(
                      company['date-of-application']));
                    workbench.push('</td>');
                    workbench.push('</tr>');
                    if (company['use-reminders'])
                        {
                        workbench.push('<tr>');
                        workbench.push('<th>Followup reminder</th>');
                        workbench.push('<td>');
                        workbench.push('Every ');
                        if (company['reminder-weeks'] === 1)
                            {
                            workbench.push(sanitize(company[
                              'reminder-weeks']) + ' week  from ' + 
                              sanitize(company['reminder-date']));
                            }
                        else
                            {
                            workbench.push(sanitize(company[
                              'reminder-weeks']) + ' weeks  from ' + 
                              sanitize(company['reminder-date']));
                            }
                        workbench.push('</td>');
                        workbench.push('</tr>');
                        }
                    workbench.push('</table>');
                    }
                else
                    {
                    workbench.push('<tr>');
                    workbench.push('<th>Company name</th>');
                    workbench.push('<td>');
                    var nonempty = 0;
                    if (company['name'])
                        {
                        workbench.push(
                          '<input type="text" name="name" id="name" value="' +
                          sanitize(company['name']) +
                          '" placeholder="E.g. &quot;C.J.S. Hayward Publications&quot;" />');
                        }
                    else
                        {
                        workbench.push('<input name="name" id="name" ' +
                        'placeholder="E.g. &quot;C.J.S. Hayward Publications&quot;"/>');
                        }
                    workbench.push('</td>');
                    workbench.push('</tr>');
                    workbench.push('<tr>');
                    workbench.push('<th>Description</th>');
                    workbench.push('<td>');
                    workbench.push(
                      '<textarea name="description" id="description" ' +
                      'value="' + sanitize(company['description']) +
                      '" placeholder=' +
                      '"E.g. &quot;Author and publisher of curious books.&quot;"' +
                      '/></textarea>');
                    workbench.push('</td>');
                    workbench.push('</tr>');
                    workbench.push('<tr>');
                    workbench.push('<th>Notes</th>');
                    workbench.push('<td>');
                    workbench.push('<textarea name="observation" ');
                    workbench.push('id="observation" value="' +
                      sanitize(company['observation']) + 
                      '" placeholder="E.g. &quot;The flagship of the whole collection is ' +
                      'found in &apos;The Best of Jonathan\\\'s ' +
                      'Corner&apos;, at ' + 'best-of.jonathanscorner.com.&quot;'
                      + '"></textarea>');
                    workbench.push('</td>');
                    workbench.push('</tr>');
                    workbench.push('<tr>');
                    workbench.push('<th>Updates</th>');
                    workbench.push('<td>');
                    workbench.push('<div class="repeating" id="repeat-update" data-new-entry = "' + "<textarea name='update?' id='update?' placeholder='What just happened that you want a record of&#63;'" + '></textarea>' + '">');
                    if (typeof company['update'] === 'undefined')
                        {
                        company['update'] = [];
                        save();
                        }
                    var length = Math.max(1, company['update'].length);
                    if (typeof company !== 'undefined' && typeof company['update'] !== 'undefined' && company['update'][length - 1])
                        {
                        length += 1;
                        }
                    for(var index = 0; index < length; index += 1)
                        {
                        if (typeof company === 'undefined' ||
                          typeof company['update'] === 'undefined' ||
                          !company['update'][index])
                            {
                            workbench.push('<textarea name="update' +
                              index + '" id="update' + index +
                              '" value="" ' + 'placeholder="' +
                              "What just happened that you want a record of&#63;" +
                              '">' + '</textarea>');
                            }
                        else if (jQuery('textarea#update' + (index)).size()
                          && jQuery('textarea#update' + (index)).val())
                            {
                            workbench.push('<textarea "name="update' +
                              index + '" id="update' + index +
                              '" placeholder="' +
                              "What just happened that you want a record of&#63;" +
                              '"' + index + '">' +
                              sanitize(company['update'][index]) +
                              '</textarea>');
                            }
                        }
                    workbench.push('</div>')
                    workbench.push('<p class="add-another"><a href="javascript:add_additional_entry(\\\'update\\\', ' + company['guid'] + ');">Add another update.</a></p>');
                    workbench.push('</td>');
                    workbench.push('</tr>');
                    workbench.push('<tr>');
                    workbench.push('<th>Information about contacts</th>');
                    workbench.push('<td>');
                    workbench.push('<div class="repeating" id="repeat-contactperson" data-new-entry = "<textarea class=\\\'contactperson\\\' name=\\\'contactperson?\\\' id=\\\'contactperson?\\\' placeholder=\\\'The name of a contact person, and anything else you\\\'d like to keep track of.\\\'></textarea><input type=\\\'url\\\' class=\\\'contact-detail\\\' name=\\\'url?\\\' id=\\\'url?\\\' placeholder=\\\'URL, e.g. &quot;CJSHayward.com&quot;\\\' /><input type=\\\'email\\\' name=\\\'email?\\\' id=\\\'email?\\\' class=\\\'contact-detail\\\' placeholder=\\\'Email address.\\\'/><input type=\\\'phone\\\' name=\\\'phone?\\\' id=\\\'phone?\\\' class=\\\'contact-detail\\\' placeholder=\\\'Phone number.\\\' /><input type=\\\'text\\\' name=\\\'skype?\\\' id=\\\'skype?\\\' class=\\\'contact-detail\\\' placeholder=\\\'Skype ID.\\\' /><textarea class=\\\'contact-detail\\\' name=\\\'other?\\\' id=\\\'other?\\\' placeholder=\\\'Any other form of contact information you want to keep\\\'></textarea>" />');
                    workbench.push('</div>')
                    workbench.push('<p class="add-another"><a href="javascript:add_additional_entry(\\\'contactperson\\\', ' + company['guid'] + ');">Add another contact person with notes and contact information.</a></p>');
                    setTimeout(function()
                        {
                        if (!contact_initialized)
                            {
                            add_additional_entry('contactperson',
                              company['guid']);
                            contact_initialized = true;
                            }
                        }, 0);
                    workbench.push('</td>');
                    workbench.push('</tr>');
                    workbench.push('<tr>');
                    workbench.push('<th>Followup reminders</th>');
                    workbench.push('<td>');
                    workbench.push('<label for="use-reminders">');
                    workbench.push('<input type="checkbox" ');
                    if (company['use-reminders'])
                        {
                        workbench.push(' checked="checked"');
                        }
                    workbench.push(' name="use-reminder" ');
                    workbench.push('id="use-reminder">');
                    workbench.push(' Every ');
                    workbench.push(
                      '<input name="reminder-weeks" ' +
                      'id="reminder-weeks" type="number" ' +
                      'min="0" step="1" value="' +
                      company['reminder-weeks'] + '">');
                    if (company['reminder-weeks'] === 1)
                        {
                        workbench.push(' week after ');
                        }
                    else
                        {
                        workbench.push(' weeks after');
                        }
                    workbench.push('<input type="date" name="reminder-date" id="reminder-date" value="' +
                    company['reminder-date'] + '">.');
                    workbench.push('<tr>');
                    workbench.push('<th>Date of application</th>');
                    workbench.push('<td>');
                    workbench.push('<input type="date" name="date-of-application" value="'
                    + sanitize(company['date-of-application']) + '"></label>');
                    workbench.push('</td>');
                    workbench.push('</tr>');
                    }
                workbench.push('</tbody>');
                workbench.push('</table>');
                var result = {'company': company, 'html':
                  workbench.join('')};
                return result;
                }
            jQuery(function()
                {
                jQuery('#more').css('left', jQuery(window).width() / 2 -
                  75 + 'px');
                jQuery('#more').fadeOut(2000);
                });
            var resize = function()
                {
                // console.log('resize');
                var max_size = jQuery(window).height() / 2;
                jQuery('td div.repeating').css({'max-height': max_size +
                  'px', 'overflow-y': 'auto'});
                jQuery('th').css({'max-height': max_size + 'px',
                  'overflow-y': 'auto'});
                }
            resize();
            jQuery(window).resize(resize);
            var has_rendered_existing = false;
            var last_seconds = Math.floor(new Date().getTime() / 1000);
            var render_existing = function(display_not_edit)
                {
                // console.log('render_existing');
                var seconds_now = Math.floor(new Date().getTime() / 1000);
                if (last_seconds === seconds_now)
                    {
                    return;
                    }
                else
                    {
                    last_seconds = seconds_now;
                    }
                var start = new Date().getTime()
                var history = [];
                var results = search(jQuery('#query').val());
                if (results === [])
                    {
                    history.push('<p><em>There were no matches to your search.</em></p><br />');
                    }
                var result = '';
                var existing = [];
                var displayed = [];
                for(var index = 0; index < results.length; ++index)
                    {
                    history.push(results[index]);
                    }
                for(var index = 0; index < monolith['companies'].length; index
                  += 1)
                    {
                    if (typeof results === 'undefined' ||
                      monolith['companies'][index] in results)
                        {
                        history.push(prerender_company(
                          monolith['companies'][index], true)['html']);
                        history.push('<div class="button"><a class="button" ' +
                          'href="javascript:edit_existing(  ' + index + ')"' +
                          'onclick="edit_existing(   ' + index + ');">Edit above '
                          + 'entry</a></div>');
                        }
                    }
                jQuery('#history').html(history.join(''));
                if (!has_rendered_existing)
                    {
                    has_rendered_existing = true;
                    }
                jQuery('#reminders').html(view_reminders());
                };
                var cull_companies = function()
                    {
                    var result = [];
                    for(var outer = 0; outer < monolith['companies'].length;
                      outer += 1)
                        {
                        var company = monolith['companies'][outer];
                        var company_may_be_empty = true;
                        if (!company)
                            {
                            continue;
                            }
                        if (company['name'] || company['description'] ||
                          company['notes'])
                            {
                            company_may_be_empty = false;
                            }
                        var repeated = ['update', 'url', 'contactperson',
                          'email', 'phone', 'skype', 'other'];
                        for(var middle = 0; middle < repeated.length; middle
                          += 1)
                            {
                            for(var inner = 0; inner < repeated[middle].length;
                              inner += 1)
                                {
                                if (company[repeated[middle]] &&
                                  company[repeated[middle]][inner])
                                    {
                                    company_may_be_empty = false;
                                    }
                                }
                            }
                        if (!company_may_be_empty)
                            {
                            result.push(company);
                            }
                        }
                    return result;
                    };
                var view_reminders = function()
                    {
                    // console.log('view_reminders');
                    var companies = cull_companies();
                    var workbench = [];
                    var max_weeks = 1;
                    var today = new Date();
                    var month = today.getMonth() + 1;
                    if (month < 10)
                        {
                        month = '0' + month;
                        }
                    var date = today.getDate();
                    if (date < 10)
                        {
                        date = '0' + date;
                        }
                    var min_date = (today.
                      getFullYear() + '-' + month + '-' + date);
                    var candidates = [];
                    for(var index = 0; index < companies.length;
                      index += 1)
                        {
                        var company = companies[index];
                        if (typeof company !== 'undefined' &&
                          company !== null && company['use-reminders'])
                            {
                            if (parseInt(company['reminder-weeks'], 10) >
                              max_weeks)  
                                {
                                max_weeks = company['reminder-weeks'];
                                }
                            if (company['reminder-date'] < min_date)
                                {
                                min_date = company['reminder-date'];
                                }
                            candidates.push(company);
                            }
                        }
                    var expression_table = [];
                    var translation_table = [];
                    var homebase = new Date();
                    homebase.setHours(12);
                    var target = [];
                    for(var index = -7 * (max_weeks + 2); index < 7 * (max_weeks +
                      2); index += 1)
                        {
                        var moving_copy = new Date();
                        moving_copy.setTime(homebase.getTime() +
                          index * 24 * 60 * 60 * 1000);
                        var date_expression = '' + moving_copy.getFullYear();
                        date_expression += '-';
                        var month = moving_copy.getMonth() + 1;
                        if (month < 10)
                            {
                            month = '0' + month;
                            }
                        date_expression += month + '-';
                        var date = moving_copy.getDate();
                        if (date < 10)
                            {
                            date = '0' + date;
                            }
                        date_expression += date;
                        translation_table[index] = date_expression;
                        target[index] = [];
                        expression_table[index] = moving_copy.toLocaleDateString();
                        }
                    for(var outer = 0; outer < candidates.length; ++outer)
                        {
                        var candidate = candidates[outer];
                        var weeks = parseInt(candidate['reminder-weeks'], 10);
                        var outer_index = translation_table.indexOf(candidate);
                        for(var inner = - weeks * 7 - 30;
                          inner < weeks * 7 + 30; inner += 1)
                            {
                            if (outer_index + inner >= 0)
                                {
                                if (outer_index + inner < 7 * weeks)
                                    {
                                    if ((inner - outer_index) %% (7 * weeks) === 0)
                                        {
                                        target[inner].push(candidate);
                                        }
                                    }
                                }
                            }
                        }
                    for(var outer = 0; outer < max_weeks * 7; ++outer)
                        {
                        if (target[outer].length)
                            {
                            target[outer].sort(function(a, b)
                                {
                                return cmp(a.name, b.name);
                                });
                            for(var inner = 0; inner < target[outer].length;
                              ++inner)
                                {
                                workbench.push('<h2 class="reminder">' +
                                  expression_table[outer] + '</h2>');
                                workbench.push('<p class="reminder">');
                                workbench.push('<a href="javascript:drilldown_from_reminder('
                                + target[outer][inner]['guid'] + ');">');
                                if (target[outer][inner]['name'])
                                    {
                                    workbench.push(target[outer][inner]['name']);
                                    }
                                else
                                    {
                                    workbench.push('Anonymous company');
                                    }
                                workbench.push('</a>');
                                workbench.push('</p>');
                                if (drilldown !== null &&
                                  target[outer][inner]['guid'] === drilldown)
                                    {
                                    workbench.push(prerender_company(
                                      target[outer][inner], true)['html']);
                                    }
                                workbench.push('</div>')
                                }
                            }
                        }
                    return workbench.join('');
                    };
                view_reminders();
                var erase = function()
                    {
                    // console.log('erase');
                    localStorage['monolith'] = null;
                    monolith = null;
                    window.location.assign('');
                    };
                var previous_monolith = null;
                setInterval(function()
                    {
                    if (logged_in && username && password)
                        {
                        jQuery.ajax(
                            {
                            'data':
                                {
                                'mode': 'restore',
                                'password': password,
                                'username': username
                                },
                            'method': 'POST',
                            'success': function(data, text_status, jqXHR)
                                {
                                parsed_monolith = jqXHR.responseText;
                                if (parsed_monolith && parsed_monolith[0] !== '<')
                                    {
                                    monolith = JSON.parse(parsed_monolith);
                                    }
                                },
                            'url': ''
                            });
                        }
                    }, 300 * 1000);
                var search_preprocess = function(initial)
                    {
                    // console.log('search_preproccess');
                    if (typeof initial === typeof [])
                        {
                        var split = initial;
                        }
                    else if (typeof initial == typeof '')
                        {
                        var split = initial.split(/\W+/);
                        }
                    else
                        {
                        var split = [];
                        }
                    var result = [];
                    if (split && split.length)
                        {
                        for(var index = 0; index < split.length; index += 1)
                            {
                            if (split[index] &&
                              typeof split[index] !== 'number')
                                {
                                result.push(split[index].toLowerCase());
                                }
                            }
                        }
                    return result;
                    }
                var drilldown_from_reminder = function(guid)
                    {
                    console.log('Drilling down: ' + guid);
                    drilldown = guid;
                    return;
                    jQuery('.drilldown-slot').hide('slow');
                    var result = prerender_company(guid, true)['html'];
                    console.log('drilldown_from_reminder');
                    console.log(guid);
                    console.log(result);
                    var timestamp = new Date().getTime();
                    var container;
                    (container = '<div id="' + timestamp +
                      '" style="display: none;">' + result + '</div>');
                    jQuery('#drilldown-slot-' + guid).html(container);
                    jQuery('#' + timestamp).show('slow');
                    }
                var search = function(query)
                    {
                    // console.log('search');
                    var result = [];
                    var parsed = search_preprocess(query);
                    var companies = cull_companies();
                    for(var outer = 0; outer <
                      companies.length; outer += 1)
                        {
                        var company = companies[outer];
                        var tokenized = [];
                        var unique = ['name', 'description', 'notes'];
                        for(var middle = 0; middle < unique.length;
                          middle += 1)
                            {
                            tokenized = tokenized.concat(search_preprocess(
                              company[unique[middle]]));
                            }
                        var repeated = ['update', 'url', 'contactperson',
                          'email', 'phone', 'skype', 'other'];
                        for(var middle = 0; middle < repeated.length;
                          middle += 1)
                            {
                            for(var inner = 0; inner <
                              repeated[middle].length; ++inner)
                                {
                                tokenized = tokenized.concat(search_preprocess(company[repeated[middle]]));
                                }
                            }
                        var is_candidate = true;
                        for(var middle = 0; middle < parsed.length;
                          middle += 1)
                            {
                            if (parsed[middle])
                                {
                                if (tokenized.indexOf(parsed[middle]) === -1)
                                    {
                                    is_candidate = false;
                                    }
                                }
                            }
                        if (is_candidate)
                            {
                            result.push(prerender_company(company)['html']);
                            }
                        }
                    return result;
                    }
                setTimeout(function()
                    {
                    var last_seconds = Math.floor(new Date().getTime() / 1000);
                    save();
                    render_existing(true);
                    view_reminders();
                    setInterval(function()
                        {
                        // var seconds_now = Math.floor(new Date().getTime() / 1000);
                        // last_seconds = seconds_now;
                        save();
                        render_existing(true);
                        view_reminders();
                        }, 50);
                    }, 50);
            jQuery(function()
                {
                jQuery('#more').css('left', jQuery(window).width() / 2 - 75 + 'px');
                jQuery('#more').fadeOut(2000);
                });
            jQuery('#questions').html(add_statistics_questions());
            add_new();
    </script>
''' % escaped

stored['scripts'] = scripts
escaped['scripts'] = scripts

def create_user(username, password):
    filename = os.path.join(dirname, 'database', 'users',
      binascii.hexlify(username))
    if os.path.isfile(filename):
        return 'Email already exists. <a href="/?mode=login">Log in</a>'
    else:
        if cracklib_available:
            try:
                cracklib.VeryFascistCheck(password)
            except ValueError, message:
                return 'The password' + message[2:] + '.'
        try:
            salt = open('/dev/random').read(16)
        except:
            try:
                salt = open('/dev/urandom').read(16)
            except:
                salt = str(os.getpid())
        workbench = hashlib.new(hashing_scheme)
        workbench.update(binascii.hexlify(salt) + binascii.hexlify(password))
        hex_hash = workbench.hexdigest()
        if os.path.isfile(filename):
            return 'This file already exists!'
        else:
            open(filename + '.' + str(os.getpid()),
              'w').write(hashing_scheme + '-' + binascii.hexlify(salt) + '-' +
              hex_hash)
            os.rename(filename + '.' + str(os.getpid()), filename)
            return ''

main_page = '''Content-type: text/html

<!DOCTYPE html>
<!--

The MIT License (MIT)

Copyright (c) 2016 Jonathan Hayward ("C.J.S. Hayward"). The source code of the
main https://JobhuntTracker.com software is a CGI script run under Apache. The
source is available from https://github.com/JonathanHayward/jobhunttracker.git

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

-->
<html>
    <head>
        <link rel="stylesheet"
          href="//code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css">
        <title>Jobhunt Tracker: A tracker tool for the details in your jobhunt</title>
        <meta name="viewport" content="initial-scale=1">
        <script src="//code.jquery.com/jquery-1.10.2.js"></script>
        <script src="//code.jquery.com/ui/1.11.4/jquery-ui.js"></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/showdown/1.3.0/showdown.js"></script>
        <meta name="keywords" content="jobhunt job hunt search tracker tool employment" />
        <meta name="description" content="Do you have trouble keeping on top of all the details of a jobhunt? This is a tool designed to help you systematically keep track of new and existing job leads, details and current status; and consistent, repeated followup to continue your conversations." />
        <style type="text/css">
            a:link, .ui-state-default a:link
                {
                color: #0000ee;
                text-decoration: underline;
                }
            a:visited, .ui-state-default a:visited
                {
                color: #551a8b;
                text-decoration: underline;
                }
            a.button
                {
                background-color: #0000ff;
                color: white;
                font-weight: bold;
                padding: 8px;
                }
            abbr
                {
                border-bottom: 2px dotted black;
                }
            body
                {
                background-color: #f8f8f8;
                font-family: Verdana, Arial, sans;
                }
            .comment
                {
                width: 20%%;
                }
            .contact-detail
                {
                width: 100%%;
                }
            div.button
                {
                float: left;
                margin: 10px;
                }
            div.buttons
                {
                margin: 10px;
                }
            div.edit
                {
                background-color: #0000ee;
                color: white;
                float: right;
                font-weight: bold;
                padding: 4px;
                }
            div.flattr
                {
                float: right;
                height: 100px;
                margin-left: 10px;
                width: 75px;
                }
            div#lightbox
                {
                background-attachment: fixed;
                background-color: rgba(0, 0, 0, .5);
                bottom: 0;
                display: none;
                height: 100%%;
                left: 0;
                position: absolute;
                right: 0;
                top: 0;
                width: 100%%;
                z-index: 900;
                }
            div#lightbox-contents
                {
                background-color: #ffffff;
                bottom: 10%%;
                display: none;
                height: 80%%;
                left: 20%%;
                overflow-y: auto;
                position: absolute;
                right: 20%%;
                top: 10%%;
                width: 60%%;
                z-index:1000;
                }
            div#main
                {
                margin-left: auto;
                margin-right: auto;
                max-width: 1024px;
                }
            div.share
                {
                float: left;
                margin-right: 20px;
                margin-top: 15px;
                }
            div.tab-content a
                {
                font-weight: bold;
                }
            div#tabs
                {
                overflow-y: auto;
                }
            div#tabs-enter
                {
                margin-top: 30px;
                overflow-y: auto;
                }
            div.unbutton
                {
                float: left;
                font-weight: bold;
                margin: 10px;
                }
            #erase
                {
                position: fixed;
                top: 0;
                left: 0;
                }
            form.complete
                {
                overflow-y: auto;
                }
            h1
                {
                margin-bottom: 14px;
                }
            h1 span
                {
                background-color: #dddddd;
                padding: 3px:
                }
            h2.tagline
                {
                margin-top: 0;
                font-style: italic;
                }
            h2.tagline em
                {
                background-color: #dddddd;
                font-size: larger;
                font-style: normal;
                padding: 3px;
                }
            @media only screen and (max-width: 700px)
                {
                h2.tagline
                    {
                    display: none;
                    }
                }
            iframe
                {
                height: 100%%;
                width: 100%%;
                }
            img#more
                {
                bottom: 75px;
                display: none;
                left: 400px;
                position: fixed;
                z-index: 1000;
                }
            input[type="text"], input[type="url"], input[type="email"],
            input[type="number"], input[type="tel"], textarea
                {
                border: 1px solid black;
                padding: 4px;
                margin-top: 6px;
                margin-bottom: 4px;
                margin-left: 0px;
                margin-right: 5px;
                }
            input.comment 
                {
                width: 100px;
                }
            input#name
                {
                border: 1px solid black;
                padding: 4px;
                width: 100%%;
                }
            input#query
                {
                border-color: "#0000ee";
                font-size: 2em;
                margin-left: 10%%;
                width: 55%%;
                }
            input#reminder-weeks
                {
                width: 50px;
                }
            input#search
                {
                background-color: #0000ee;
                border: 0;
                color: white;
                font-size: 2em;
                width: 15%%;
                }
            input.skype
                {
                width: 208px;
                }
            p.add-another
                {
                font-style: italic;
                font-weight: normal;
                margin-top: 3px;
                padding-left: 8px;
                }
            p.add-another a
                {
                font-weight: normal;
                }
            p.footer
                {
                font-style: italic;
                margin-left: auto;
                margin-right: auto;
                max-width: 950px;
                text-align: center;
                }
            p.footer a
                {
                font-style: normal;
                font-weight: bold;
                }
            p.login
                {
                display: none;
                float: right;
                line-height: 1.7em;
                }
            p.login_offer
                {
                float: right;
                }
            p.logout
                {
                display: none;
                float: right;
                }
            p.timestamp
                {
                color: silver;
                font-size: smaller;
                font-style: italic;
                margin-top: 4px;
                }
            p.update
                {
                margin-bottom: 0;
                }
            #query
                {
                margin-top: 30px;
                }
            table
                {
                width: 100%%;
                }
            table.graph tr
                {
                padding-bottom: 20px;
                }
            table.statistics th
                {
                padding: 10px;
                }
            td div#repeat-update
                {
                border: 1px solid #808080;
                padding: 10px;
                }
            td div#repeat-update textarea
                {
                width: 97%%;
                }
            textarea
                {
                height: 100px;
                width: 100%%;
                }
            th
                {
                width: 200px;
                }
            th
                {
                vertical-align: middle;
                }
            .ui-state-default, .ui-widget-content ui.state.default,
              .ui-widget-header .ui-state-default,
              .ui-state-default.ui-corner-top
                {
                background-image:
                  url(media/images/inactive-tab-background.png) !important;
                }
            .ui-widget-header
                {
                background-image:
                  url(media/images/tab-area-background.png) !important;
                }

            .ui-tabs .ui-tabs-nav
                {
                background-color: silver !important;
                }

            ul.menu
                {
                background-color: white;
                float: right;
                list-style: none;
                margin: 0;
                padding: 0;
                z-index: 2000;
                }
            ul.menu li
                {
                float: left;
                position: relative;
                width: 25em;
                }
            ul.menu li ul
                {
                list-style-type: none;
                margin-left: -9999px;
                padding-left: 0;
                position: absolute;
                top: 1em;
                }
            ul.menu li ul li
                {
                padding: 0;
                }
            ul.menu:hover li ul
                {
                margin-left: 0;
                }
            ul.ui-tabs-nav
                {
                margin-top: 0;
                max-width: 1054px;
                }
            ::-webkit-input-placeholder
                {
                color: #808080;
                }
            :-moz-placeholder
                {
                color: #808080;  
                }
            ::-moz-placeholder
                {
                color: #808080;  
                }
            :-ms-input-placeholder
                {  
                color: #808080;  
                }
        </style>

    </head>
    <body>
        <div id="error-banner"></div>
        <div id="main">
            <div class="flattr">
                <script id='fb5t8wi'>(function(i){var f,s=document.getElementById(i);f=document.createElement('iframe');f.src='//button.flattr.com/view/?fid=3peded&url='+encodeURIComponent(document.URL);f.title='Flattr';f.height=62;f.width=55;f.style.borderWidth=0;s.parentNode.insertBefore(f,s);})('fb5t8wi');</script>
            </div>
            <p class="login_offer" style="float: right;"><a href="javascript:jQuery('p.login_offer').hide(); jQuery('p.login').show('slow'); jQuery('div.flattr').hide();" onclick="jQuery('p.login_offer').hide(); jQuery('p.login').show('slow'); jQuery('div.flattr').hide();">Login options</a></p>
            <p class="login" style="display: none;">
                <strong><a
                    href="javascript:display_lightbox('?mode=register')"
                    onclick="display_lightbox('?mode=register')"
                    >You can use this from
                    other computers!</a></strong><br />
                    But you'll need an account.
                    <strong><a
                    href="javascript:display_lightbox('?mode=register')"
                    onclick="display_lightbox('?mode=register')"
                    >Sign up!</a></strong> <span
                    style="color: silver;">&bull;</span>
                    <em><a
                    href="javascript:display_lightbox('?mode=login')"
                    onclick="display_lightbox('?mode=login')"
                    >Log in</a></em>
            </p>
            <p class="logout" style="float: right;" display: none;">
                <a href="?mode=logout">Log out</a>
            </p>
            <h1><span>Jobhunt Tracker
              <span style="color: #a0a0a0;">(beta)</span></span></h1>
            <h2 class="tagline">A <em>tracker</em> tool for all the
            details in your <em>jobhunt</em>!</h2>
            <div id="tabs">
                <ul>
                    <li><a href="#tabs-about"><strong>Welcome!</strong></a></li>
                    <li><a href="#tabs-enter">Add &amp; edit jobs</a></li>
                    <li><a href="#tabs-view">Browse &amp; search saved jobs</a></li>
                    <li><a href="#tabs-reminder">See followup reminders</a></li>
                    <li><a href="#tabs-statistics">Your stats</a></li>
                </ul>
                <div class="tab-content" id="tabs-about">
                    <div class="share">
                        <span class='st_sharethis_large' displayText='ShareThis'></span>
                        <br />
                        <span class='st_facebook_large' displayText='Facebook'></span>
                        <br />
                        <span class='st_twitter_large' displayText='Tweet'></span>
                        <br />
                        <span class='st_linkedin_large' displayText='LinkedIn'></span>
                        <br />
                        <span class='st_pinterest_large' displayText='Pinterest'></span>
                        <br />
                        <span class='st_email_large' displayText='Email'></span>
                    </div>

                    <h2>About Jobhunt Tracker and a successful jobhunt</h2>
                    <p>There are a lot of details in a successful jobhunt, and
                    this website is meant to at least make the hassle more
                    manageable.</p>

                    <p><strong>How do you use this tool? Don't be timid; play
                    around and explore, and you will find support for some
                    tasks involved in jobhunting.</strong></p>

                    <p>There are some excellent jobhunting books out there;
                    people tend to find a position faster if they are working
                    with a group. It is a known fact to most employers that
                    most people run their jobhunt the way they will run their
                    lives. Most people start off with a surging flood of action
                    that somehow dries up to a trickle before too long.</p>

                    <p>This site is not intended to help you organize a job
                    search as a whole; it's a tool for taking care of details
                    once you know what you need to do. This site is doing a
                    different job from what a good jobseeker's book or
                    jobseeker's group will tell you, and you are invited to
                    read the following titles:</p>

                    <ol>
                        <li><p><a href="http://amzn.to/1LYmUD6">What Color Is
                        Your Parachute?</a>, by Richard Bolles.</p></li>
                        <li><p><a href="http://amzn.to/1LisgJc">Games Companies
                        Play</a>, by Pierre Mornell.</p></li>
                        <li><p><a
                        href="http://www.amazon.com/gp/product/0071464042/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=0071464042&linkCode=as2&tag=jonascorn-20&linkId=FP57PXSDVGT5DZOS">The
                        Unwritten Rules of Highly Effective Job
                        Search</a>, by Orville Pearson.</p></li>
                    </ol>

                    <p>You probably know you should be using <a
                    href="http://linkedin.com">LinkedIn</a>; what you may not
                    know is that you should also use a different kind of site,
                    <a href="http://linkup.com">LinkUp</a>, which is hands down
                    the best the author is aware of for that kind of site.</p>

                    <p>There are quite possibly other career and job
                    hunting resources in your area; all that glitters is not
                    gold, but they are often worth considering, and if
                    nothing else a good librarian may help you out. And if you
                    read some good books, search the area for other support,
                    and give it your best, this website may help you to keep on
                    track of the details and keep on going. Keep up entering
                    your statistics: <strong><em>what gets measured, gets
                    improved!</em></strong></p>

                    <a href="media/images/wardrobe_full.jpg"><img title="A picture of C.J.S. Hayward, taken in front of C.S. Lewis's wardrobe at the Marion E. Wade Center of Wheaton College. Click to enlarge."
                    border="0" style="height: 222px; float: left; margin-top:
                    10px; margin-left: 10px; margin-right: 40px; margin-bottom:
                    40px;" src="media/images/cjshayward.png" alt="A picture of C.J.S. Hayward, taken in front of C.S. Lewis's wardrobe at the Marion E. Wade Center of Wheaton College." /></a>
                    <h2 style="margin-bottom: 0;">About this site's author</h2>
                    <h3 style="margin-top: 0;">(Responsible for all UX,
                    usability, design, and implementation)</h3>

                    <p>Christos Jonathan Seth Hayward is a <a
                    style="font-weight: normal;"
                    href="https://skills.cjsh.name">Renaissance man</a>
                    who loves cultures and a strong desire to land a
                    position in User Experience near Chicago. (Or some silly
                    "Resident Genius" position and title, but he'd be more than
                    happy to settle for a plain old UX design and research
                    position.) Hayward is an accomplished author (<strong><a
                    href="https://CJSHayward.com/books/">Kindle &amp;
                    books</a></strong>, <strong><a
                    href="https://CJSHayward.com/">main website</a></strong>),
                    and loves to play with his nephews.</p>

                    <p>He is presently learning Russian.</p>
                </div>
                <div class="tab-content" id="tabs-enter">

                    <div class="share" style="margin-top: -15px;">
                        <span class='st_sharethis_large' displayText='ShareThis'></span>
                        <br />
                        <span class='st_facebook_large' displayText='Facebook'></span>
                        <br />
                        <span class='st_twitter_large' displayText='Tweet'></span>
                        <br />
                        <span class='st_linkedin_large' displayText='LinkedIn'></span>
                        <br />
                        <span class='st_pinterest_large' displayText='Pinterest'></span>
                        <br />
                        <span class='st_email_large' displayText='Email'></span>
                    </div>
                    <h2>Use this area to enter information for job leads you
                    are pursuing.</h2>
                    <h2><em>This area should probably be the one where you do
                    the most work.</em></h2>
                    <div id="notes">
                    </div>
                    <div class="buttons">
                        <div class="button"><a class="button" href="#main"
                          onclick="add_new();">Save and add another</a>
                        </div>
                        <!--
                        <div class="unbutton">
                          <a href="javascript:save(); add_new(); jQuery('#tabs').tabs('option', 'active', 2);">Save; then view saved jobs</a>
                        </div>
                        -->
                    </div>
                </div>
                <div class="tab-content" id="tabs-view">

                    <div class="share">
                        <span class='st_sharethis_large' displayText='ShareThis'></span>
                        <br />
                        <span class='st_facebook_large' displayText='Facebook'></span>
                        <br />
                        <span class='st_twitter_large' displayText='Tweet'></span>
                        <br />
                        <span class='st_linkedin_large' displayText='LinkedIn'></span>
                        <br />
                        <span class='st_pinterest_large' displayText='Pinterest'></span>
                        <br />
                        <span class='st_email_large' displayText='Email'></span>
                    </div>
                    <h2>Search and browse your saved job opportunities from
                    here:</h2>
                    <form action="" onsubmit="return false;">
                    <input name="query" id="query" type="text">
                    <input type="submit" name="search" id="search" value="Search">
                    </form>
                    <div id="history">
                    </div>
                </div>
                <div class="tab-content" id="tabs-reminder">

                    <div class="share">
                        <span class='st_sharethis_large' displayText='ShareThis'></span>
                        <br />
                        <span class='st_facebook_large' displayText='Facebook'></span>
                        <br />
                        <span class='st_twitter_large' displayText='Tweet'></span>
                        <br />
                        <span class='st_linkedin_large' displayText='LinkedIn'></span>
                        <br />
                        <span class='st_pinterest_large' displayText='Pinterest'></span>
                        <br />
                        <span class='st_email_large' displayText='Email'></span>
                    </div>
                    <h2>Being persistent pays off in jobhunting. This calendar
                    offers a "tickler file" to remind you to keep channels of
                    communication open for job prospects.</h2>
                    <div id="reminders">
                    </div>
                </div>
                <div class="tab-content" id="tabs-statistics">
                    <div class="share">
                        <span class='st_sharethis_large' displayText='ShareThis'></span>
                        <br />
                        <span class='st_facebook_large' displayText='Facebook'></span>
                        <br />
                        <span class='st_twitter_large' displayText='Tweet'></span>
                        <br />
                        <span class='st_linkedin_large' displayText='LinkedIn'></span>
                        <br />
                        <span class='st_pinterest_large' displayText='Pinterest'></span>
                        <br />
                        <span class='st_email_large' displayText='Email'></span>
                    </div>
                    <h2>Want to improve your job search? <em>What gets measured,
                    gets improved!</em></h2>
                    <div id="questions">
                    </div>
                    <div id="graph">
                    </div>
                </div>

            </div>
        </div>
        <div id="lightbox"></div>
        <div id="lightbox-contents"></div>

        <img src="media/images/down_arrow.png" id="more" />
        <p class="footer"> &copy; 2016, licensed under the terms of the <a href="license.txt" target="_blank">MIT License</a> (<a href="https://github.com/JonathanHayward/jobhunttracker">GitHub</a>.  <em>This website was created, in two weeks, including all aspects of User Experience and User Interface, by C.J.S. Hayward (<a href="https://CJSHayward.com">website</a>, <a href="mailto:CJSH@CJSHayward.com?subject=To+the+author">email</a>).</em>
        </p>
        %(scripts)s
        <script type="text/javascript">var switchTo5x=true;</script>
        <script type="text/javascript" src="//ws.sharethis.com/button/buttons.js"></script>
        <script type="text/javascript">stLight.options({publisher:
        "d2b18c31-e06e-4f18-bfe3-68648113dfec", doNotHash: true, doNotCopy: false, hashAddressBar: false});</script>
    </body>
</html>''' % escaped


if __name__ == '__main__':
    if get_cgi('mode') == '':
        print main_page
    elif get_cgi('mode') == 'register':

        print '''Content-type: text/html

<!DOCTYPE html>
<html>
    <head>
        <title>Please create an accout</title>
        <style type="text/css">
          body
            {
            font-family: Verdana, Arial, sans;
            }
          div#author
            {
            margin-top: 10px;
            min-height: 100px;
            }
          div.footer
            {
            margin-left: .5in;
            }
          div#main
            {
            background-color: white;
            margin-left: auto;
            margin-right: auto;
            margin-top: 30px;
            padding: 30px;
            width: 1054px;
            }
          div#main form
            {
            margin-left: auto;
            margin-right: auto;
            }
          ul
            {
            list-style-type: none !important;
            }
        </style>
    </head>
    <body>
<div id="main">
    <h1>Jobhunt Tracker</h1>
    <h2><em>Create an account!</em></h2>
        <form action='' method='POST'>
            <table>
              <tbody>
                <tr>
                  <th>Email:</th>
                  <td><input id="id_username" name="username" /></td>
                </tr>
                <tr>
                  <th>Password:</th>
                  <td><input id="id_password" name="password"
                    autocomplete="off" /></td>
                </tr>
              </tbody>
            </table>
            <input type="hidden" name="mode" value="create">
            <input type='image' src="media/images/submit.jpg">
            </form>
        </div>
        <div class="footer">
        </div>
    </body>
</html>
''' % escaped

    elif get_cgi('mode') == 'logout':
        print '''Set-Cookie=username; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT
Set-Cookie=password; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT
Content-Type: text/html

<!DOCTYPE html>
<html>
    <head>
        <script>
            localStorage['username'] = null;
            localStorage['password'] = null;
            localStorage['Calendar'] = null;
            localStorage['Todo'] = null;
            localStorage['Scratch'] = null;
        </script>
        <title>You're logged out.</title>
        <style type="text/css">
          body
            {
            font-family: Verdana, Arial, sans;
            }
          div#author
            {
            margin-top: 10px;
            min-height: 100px;
            }
          div#main
            {
            background-color: white;
            margin-left: auto;
            margin-right: auto;
            margin-top: 30px;
            padding: 30px;
            width: 1054px;
            }
          div#main form
            {
            margin-left: auto;
            margin-right: auto;
            }
          ul
            {
            list-style-type: none !important;
            }
        </style>
    </head>
    <body>
<div id="main">
<h1>You have successfully <em>logged out</em> from this
<a href="/">JobhuntTracker.com</a>.</h1>

<h2>A few other sites by the same author:</h2>

<div id="portfolio">
    <h2>A Few Sites</h2>
    <p>
    <a href="https://CJSHayward.com">Author Site</a> (<a
      href="https://CJSHayward.com/books/">Bookshelf</a>)<br />
    <a href="http://ClassicOrthodoxBible.com">The Classic Orthodox
    Bible</a><br />
    <a href="http://JobhuntTracker.com">Jobhunt Tracker</a><br />
    <a href="http://OrthodoxChurchFathers.com">Orthodox Church
    Fathers</a> (<a href="http://orthodoxchurchfathers.com/?page=frames">Power
      User Mode</a>)<br />
    <a href="https://Pragmatometer.com">Pragmatometer</a><br />
    <a href="http://steampunk.cjsh.name">Steampunk Clock</a><br />
    <a href="http://JonathanHayward.com">A Touch of Artistry</a><br />
    </p>
</div>

<h2>Log in to Jobhunt Tracker again:</h2>

        <form action="/" target="_top" method="POST">
            <table>
              <tbody>
                <tr>
                  <th>Email:</th>
                  <td><input id="id_username" name="username" /></td>
                </tr>
                <tr>
                  <th>Password:</th>
                  <td><input id="id_password" name="password"
                    autocomplete="off" /></td>
                </tr>
              </tbody>
            </table>
            <input type="hidden" name="mode" value="login">
            <input type='image' src="media/images/submit.jpg">
            &mdash;
            <a href="/mode=register">Register a new account</a>
            </form>
      </div>
      %(scripts)s

        </body>
</html>
''' % escaped
        
    if get_cgi('mode') == 'login':
        print '''Content-type: text/html

<!DOCTYPE html>
<html>
    <head>
        <title>Please log in</title>
        <style type="text/css">
          body
            {
            font-family: Verdana, Arial, sans;
            }
          div#author
            {
            margin-top: 10px;
            min-height: 100px;
            }
          div.footer
            {
            margin-left: .5in;
            }
          div#main
            {
            background-color: white;
            margin-left: auto;
            margin-right: auto;
            margin-top: 30px;
            padding: 30px;
            width: 1054px;
            }
          div#main form
            {
            margin-left: auto;
            margin-right: auto;
            }
          ul
            {
            list-style-type: none !important;
            }
        </style>
    </head>
    <body>
<div id="main">
    <h1>Jobhunt Tracker</h1>
    <h2><em>Log in!</em></h2>
        <form target="_top" action="/" method="POST">
            <table>
              <tbody>
                <tr>
                  <th>Email:</th>
                  <td><input id="id_username" name="username" /></td>
                </tr>
                <tr>
                  <th>Password:</th>
                  <td><input id="id_password" name="password"
                    autocomplete="off" /></td>
                </tr>
              </tbody>
            </table>
            <input type="hidden" name="mode" value="main">
            <input type='image' src="media/images/submit.jpg">
            </form>
        </div>
        <div class="footer">
        </div>
    </body>
</html>
''' % escaped
    elif get_cgi('mode') == 'create':
        username = get_cgi('username')
        password = get_cgi('password')
        error = create_user(username, password)
        if error:
            print '''Content-type: text/html

<!DOCTYPE html>
<html>
    <head>
        <title>There was an error</title>
    </head>
    <body>
    <h1>There was an error:</h1>
    <h2 style="background-color: #ffff80">%(error)s</h2>
    <p><a target="_top" href="">Go home</a></p>
    </body>
</html>''' % locals()
        else:
            print '''Content-type: text/html

<!DOCTYPE html>
<html>
    <head>
        <title>Please log in</title>
        <style type="text/css">
          body
            {
            font-family: Verdana, Arial, sans;
            }
          div#author
            {
            margin-top: 10px;
            min-height: 100px;
            }
          div#main
            {
            background-color: white;
            margin-left: auto;
            margin-right: auto;
            margin-top: 30px;
            padding: 30px;
            width: 1054px;
            }
          div#main form
            {
            margin-left: auto;
            margin-right: auto;
            }
          ul
            {
            list-style-type: none !important;
            }
        </style>
    </head>
    <body>
    <div id="main">
    <p>You have created your account successfully!</p>
    <p><strong><a href="/?mode=login">Congratulations! Your
    accout is now created. Please click here to continue to the main
    site!</a></strong></p>
    </body>
</html>''' % escaped
    elif check_user(username, password) == '':
        if get_cgi('mode') == 'main':
            print main_page
        elif get_cgi('mode') == 'save':
            cl('Recognized as saving')
            try:
                cl('username: ' + username)
                filename = os.path.join(dirname, 'database/pickled',
                  binascii.hexlify(username))
                cl('filename: ' + filename)
                open(filename + '.' + str(os.getpid()), 'w').write(
                  binascii.hexlify(get_cgi('monolith')))
                os.rename(filename + '.' + str(os.getpid()), filename)
                cl('Saved.')
                print '''Content-type: text/javascript

true'''
                cl('Response sent.')
            except IOError:
                print '''Content-type: text/javascript

false'''
        elif get_cgi('mode') == 'restore':
            try:
                filename = os.path.join(dirname, 'database/key-value',
                  binascii.hexlify(username) + '-' +
                  binascii.hexlify(get_cgi('key')))
                print '''Content-type: application/json
'''
                print binascii.unhexlify(open(filename).read())
            except IOError:
                print '''Content-type: application/json

null'''

    else:
        print '''Content-type: application/json

false'''
