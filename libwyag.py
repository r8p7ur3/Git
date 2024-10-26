import argparse 
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


# for subparsers
argparser = argparse.ArgumentParser(description="Content tracker")
argsubparsers = argparser.add_subparsers (title="Commands", dest="command")
argsubparsers.required = True
argsp = argsubparsers.add_parser("init", help="creates a mini black hole that instantly decays and blasts open a repository")


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
    
#to make new repo at path
def repo_create(path):
    repo =GitRepository(path, True)

#making sure if path does not exists or goes to empty dir

    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
             raise Exception("%s Isn't a FUCKING directory DUMBASS" % path)
        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
             raise Exception("%s is not empty!" % path)
    else:
        os.makedirs(repo.worktree)

    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs","heads", mkdir=True)

    #.git/description
    with open(repo_file(repo, "description"),"w") as f:
         f.write("repository is an orphan, it has no parents. edit this file 'description' if you want to be it's baby daddy.\n")

    #.git/HEAD
    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")

    with open(repo_file(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo

#is repositoryformatversion is >1, git WILL have a mental breakdown. wyag will only take 0

def repo_default_config():
    ret = configparser.ConfigParser()

    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0")
    ret.set("core", "filemode", "false")
    ret.set("core", "bare", "false")

    return ret


argsp.add.argument("path",
                   metavar="directory",
                   nargs="?",
                   default=".",
                   help="Where do you want to open the black hole")


#bridge function to read arguments values from object returned
#by argparse, then call function with right values

def cmd_init(args):
    repo_create(args.path)



