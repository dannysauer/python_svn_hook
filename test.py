#!/usr/bin/python

from trac_wrap import TracWrap

trac = TracWrap('/srv/trac/instances/humpy/')
trac.trac_admin('permission', 'list')
