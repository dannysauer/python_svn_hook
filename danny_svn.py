#!/usr/bin/python

import pprint
import os
import errno
import svn.core
import svn.fs
import svn.repos
from tempfile import NamedTemporaryFile

def dostuff():
    """Do Stuff
    """
    print 'Hello, world'

def list(root, path):
    """List the contents of 'path' under repository rooted at 'root'
    """

    print "root is ", root
    print "path is ", path

    #clean_root = svn.core.svn_dirent_canonicalize(root)
    #repos_obj = svn.repos.open(clean_root)
    repos_obj = svn.repos.open(root)
    fs_obj = svn.repos.fs(repos_obj)
    head_rev = svn.fs.youngest_rev(fs_obj)
    root_obj = svn.fs.revision_root(fs_obj, head_rev)

    print 'Fetching revision ' + str(head_rev) + ' from directory ' + path + \
            ' in repo file://' + root \

    entries = svn.fs.dir_entries(root_obj, path)
    names = entries.keys()
    for name in names:
        suffix = ""
        if svn.fs.is_dir(root_obj, path + '/' + name):
                suffix = "/"
        print name + suffix

def get_changes(repo, rev):
    """Return a list of files and their changes in revision 'rev'
    The list might look something like (file=>{add=true, del=false,
    propchange=[aprop,anotherprop], prop_aprop=newvalue, modify=false})

    """

    base_dir = "/tmp/blah"

    repos_obj = svn.repos.open(repo)
    fs_obj    = svn.repos.fs(repos_obj)
    root_obj  = svn.fs.revision_root(fs_obj, rev)

    changes = sorted(svn.fs.paths_changed2(root_obj).items())

    # should probably set umask here? get from config file?
    # should probably also chdir to base_dir?

    # c_info contains:
    #  text_mod and prop_mod booleans
    #  copyfrom_known boolean
    #    (which also adds copyfrom_rev and copyfrom_path attrs)
    #  change_kind (can be path_change_{delete,add,replace,modify})
    #  node_kind (can be svn_node_{none,file,dir,unknown})
    for c_path, c_info in changes:
        # stupid join; if any part starts with '/', preceeding parts are ignored
        export_path = os.path.join(base_dir, './' + c_path)

        ##########
        # most likely test goes first
        if c_info.node_kind == svn.core.svn_node_file:
            if c_info.change_kind == svn.fs.path_change_delete:
                # deleted a file?  Unlink it now
                print 'deleted file ' + c_path

            elif c_info.change_kind == svn.fs.path_change_modify:
                # if it's a modification, we only care about text changes.
                # Maybe properties.  I'm not sure.  Possibly svn:eol-type...
                if c_info.text_mod:
                    print 'modified text in file ' + c_path
                    _export_file(root_obj, c_path, export_path)
            elif c_info.change_kind == svn.fs.path_change_add \
              or c_info.change_kind == svn.fs.path_change_replace:
                print 'added or replaced file ' + c_path
                _export_file(root_obj, c_path, export_path)

            else:
                print 'I\'ve lost my way on file ' + c_path

        ##########
        # directory is really the only other thing we should see
        elif c_info.node_kind == svn.core.svn_node_dir:
            # deleted a directory?  Remember it and remove at the end
            if c_info.change_kind == svn.fs.path_change_delete:
                # do something
                print 'deleted dir ' + c_path

            # modified a directory?  Must be a property change.
            elif c_info.change_kind == svn.fs.path_change_modify:
                if c_info.prop_mod:
                    # we probably only care if the directory has externals
                    print 'modified property in dir ' + c_path

            # otherwise it was an add or a replace.
            elif c_info.change_kind == svn.fs.path_change_add \
              or c_info.change_kind == svn.fs.path_change_replace:
                print 'added or replaced dir ' + c_path
                _export_dir(root_obj, c_path, export_path)

            else:
                print 'I\'ve lost my way on dir ' + c_path

        ##########
        elif c_info.node_kind == svn.core.svn_node_none:
            # I don't know what to do with a none. Shouldn't happen.
            print 'did something to a none node?'
        elif c_info.node_kind == svn.core.svn_node_unknown:
            # I don't know what to do with an unknown. Also shouldn't happen.
            print 'did something to an unknown node?'
        else:
            # This *really* shouldn't happen.
            print 'big ol\' failure'
            #return

def _export_file(root, path, export):
    """ export the file at PATH in ROOT to EXPORT
    Creates a temp file, then rename()'s the tempfile to the real name.
    This makes the export atomic, hopefully eliminating problems with
    the partially-sync'd files.
    """

    export_dir = os.path.dirname(export)

    if os.path.exists(export) and not os.path.isfile(export):
        print "file exits as non-file!"
        return

    # make parent dirs if needed
    try:
        os.makedirs(export_dir)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(export_dir):
            pass
        else:
            raise

    # get file contents from svn
    try:
        stream = svn.fs.file_contents(root, path)
        data = svn.core.svn_string_from_stream(stream)
        svn.core.svn_stream_close(stream)
    except Exception:
        return None

    # get temp file and put data in there
    f = NamedTemporaryFile(
            mode   = 'w+b',
            prefix = os.path.basename(export),
            dir    = export_dir,
            delete = False,
            )
    f.write( data )
    # I'm pretty sure there should be some error handling here
    # also, the rename() should check for OSError
    os.rename( f.name, export )

def _export_dir(root, path, export):
    """ export the directory named PATH from ROOT to EXPORT
    """

    # check this for error exceptions, indicating that the directory already
    # exists (which we should have already checked for) or that creation failed
    try:
        os.makedirs(export)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(export):
            pass
        else:
            raise

def _remove_dir(export):
    """Remove a directory
    """

    if os.path.ismount(export):
        # we can't remove a mountpoint
        print "Fail!  Can't remove mountpoint"
        return

    # check for OSError
    os.rmdir(export)

def _remove_file(export):
    """Remove a file
    This should happen before any _remove_dir() calls, since that will fail on
    non-empty directories
    """

    # check for errors
    os.unlink(export)
