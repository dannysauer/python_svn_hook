#!/usr/bin/python

from trac.env   import Environment
from trac.admin import AdminCommandManager
#from trac.admin import AdminCommandError, AdminCommandManager

################################################################################
## this is slightly faster than just using the admin console method:
#
# import trac.admin.console
# adm = trac.admin.console.TracAdmin('/srv/trac/instances/humpy/')
# adm.onecmd('permission list')
#
## I'm not entirely sure if either interface will remain constant.  Hopefully
## it will. :)
################################################################################

class TracWrap:
    def __init__(self, env):
        self.mgr = AdminCommandManager(Environment(env))

    def trac_admin(self, *cmd):
        self.mgr.execute_command(*cmd)
        # this probably should catch AdminCommandError, but whatever
