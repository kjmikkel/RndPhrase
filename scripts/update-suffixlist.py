#!/usr/bin/env python
import os
import urllib2 as urllib
import anyjson as json


URL_LIST = "http://mxr.mozilla.org/mozilla-central/source/netwerk/dns/src/effective_tld_names.dat?raw=1"

# generate json
print 'downloading suffix list..'
rules = {}
lst = urllib.urlopen(URL_LIST).read()
print 'processing list..'
lines = lst.split('\n')
for i,line in enumerate(lines):
    if line[:2] == '//' or len(line) == 0:
        continue # skip comments
    EXCEPT = line[0] == '!'
    if EXCEPT: # exception rule
        line = line[1:]
    doms = line.split('.')
    lst = rules
    # find node to update
    for d in reversed(doms):
        node = lst.get(d, None)
        if not node:
            node = {}
            lst[d] = node
        lst = node
    if EXCEPT:
        lst['!'] = {};

# functions for checking domains
def get_reg_domain(rules, doms):
    node = rules.get(doms[0],None)
    if node == None: node = rules.get('*',None)
    if node == None or (len(node) == 1 and node['!'] == 1):
        return doms[0]
    elif len(doms) == 1:
        return None
    reg = get_reg_domain(node, doms[1:])
    if(reg != None):
        return '%s.%s' % (reg, doms[0])
def get_host(domain):
    doms = list(reversed(domain.split('.')))
    return get_reg_domain(rules, doms)

# test the list
print 'testing list..'
tests = {'qwe.parliament.co.uk': 'parliament.co.uk',
         'foo.bar.version2.dk': 'version2.dk',
         'ecs.soton.ac.uk': 'soton.ac.uk'}
for (test,res) in tests.items():
    assert get_host(test) == res

# convert the dictionary into a list
def build_string(rules):
    lst = []
    for key in rules:
        c = build_string(rules[key])
        s = key
        if len(c) != 0: s += '(%s)' % c
        lst.append(s)
    return ','.join(lst)
def set_length(d):
    for key in d:
        set_length(d[key])
    d['L'] = len(d)
# output new list as javascript
set_length(rules)
print 'writing list..'
json = json.serialize(rules).replace(' ','')
file('data/suffix-list.js','w').write('var SUFFIX_LIST=%s;' % json);

print 'done.'
