#!/usr/bin/python

import sys
import danny_svn

os.environ['TRAC_ENV'] = '/srv/trac/instances/humpy'
os.environ['TRACROOT'] = os.environ['TRAC_ENV'] # compatability?
os.environ['PYTHON_EGG_CACHE'] = '/srv/trac/eggs'

#if not 'PYTHON_EGG_CACHE' in os.environ:
#    os.environ['PYTHON_EGG_CACHE'] = os.path.join(sys.argv[1], '.egg-cache')

def main():
    """ default function
    """
    print >> sys.stderr 'Called via "' +sys.argv[0] + '" which is unsupported.'
    sys.exit(1)

def post_commit():
    """ post-commit action:
    """
    danny_svn.get_changes(sys.argv[1], int(sys.argv[2]))

if __name__ == '__main__':
    if (os.path.basename(sys.argv[0]) == 'post-commit'):
        post_commit()
