import argparse # most familiar with this library
import collections
import configparser
from datetime import datetime
import grp, pwd
from fnmatch import fnmatch
import hashlib
from math import ceil
import os
import re
import sys
import zlib

argparser = argparse.ArgumentParser(description="Content tracker")

# for subparsers
argsubparsers = argparser.add_subparsers (title="Commands", dest="command")
argsubparsers.required = True

# each subpraser will be returned as a string in their respective fields
def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        case "add"          : cmd_add(args)
        case "cat-file"     : cmd_cat_file(args)
        case "check-ignore" : cmd_check_ignore(args)
        case "checkout"     : cmd_checkout(args)
        case "commit"       : cmd_commit(args)
        case "hash-object"  : cmd_hash_object(args)
        case "init"         : cmd_init(args)
        case "log"          : cmd_log(args)
        case "ls-files"     : cmd_ls_files(args)
        case "ls-tree"      : cmd_ls_tree(args)
        case "rev-parse"    : cmd_rev_parse(args)
        case "rm"           : cmd_rm(args)
        case "show-ref"     : cmd_show_ref(args)
        case "status"       : cmd_status(args)
        case "tag"          : cmd_tag(args)
        case _              : print("You didn't give a command dumbass.")



class GitRepo (object):
    '''git repo'''

    worktree = None
    gitdir = None
    conf = None

    def __init__(self, path, force = False):
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception("Bro.... this isn't a Git repo... %s" % path)
        
        #read config from .git/config
        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")
 
        #check for if config exists
        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("She's busy lil bro (the config file)")
        
        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception("Unsupported repositoryformatversion %s" % vers)
            
        
def repo_path(repo, *path):
    #compute path under repos gitdir (* on path makes function variadic)
    return os.path.join(repo.gitdir, *path)

def repo_file(repo, *path, mkdir=False):
    # same thing as repo_path but creates dirname(*path) if absent
    # eg, repo_file(r, \"dog\",\"cat\",\"mouse\")
    #will make .git\dog\cat\mouse

    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)
    
def repo_dir(repo, *path, mkdir = False):
    #also same as repo_path, but mkdir

    path = repo_path(repo, *path)

    if os.path.exists(path):
        if (os.path.isdir(path)):
            return path
        else:
            raise Exception("Are you retarded? Not a fucking directory %s" % path)
        
    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None
    

