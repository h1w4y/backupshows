#!/usr/local/bin/python
"""backs up watched shows from local drive to some other storage
dependency on python psutil library
dependency on mpv
dependency on mpv playlist addon written in .lua
"""

import os
import shutil
import pdb

# print full path to imported libs
print (os)
print (shutil)
print (pdb)

LOCAL_SHOWS = "/Users/mike/Movies/TV1/"
REMOTE_SHOWS = "/Users/mike/Movies/TV2/"

# showlist file built by mpv playlist-maker addon
# https://github.com/donmaiq/unseen-playlistmaker
# shows are added when watched 80% in mpv
SHOWLIST = "/Users/mike/Movies/list"

# list of shows without full path, used for finding processes and reporting
SHOWS = []
# list of shows with full path, used for moving files
SHOWSWITHPATH = []

def find(name, path):
    """ function to find a file and return the full path """
    for root, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def find_all(name, path):
    """ function to find files and return the full path """
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result


#print ""
#print "local directory set to: " + LOCAL_SHOWS
#print "remote directory set to: " + REMOTE_SHOWS
#print ""

# check if directories exist
if not os.path.isdir(LOCAL_SHOWS):
    print "[Error] " + LOCAL_SHOWS + " not found"
    print ""
    raise ValueError('directory not found')

if not os.path.isdir(REMOTE_SHOWS):
    print "[Error] " + REMOTE_SHOWS + " not found"
    print ""
    raise ValueError('directory not found')

# read watched list from mpv addon
# try catch this file operation
with open(SHOWLIST) as f:
    SHOWS = f.readlines()
f.close()

print "==================================================="
print "These ", len(SHOWS), " Shows were found in your \"played\" list:\n"
for show in SHOWS:
    print "\t", show.strip()

SHOWCOUNTER = 0
for show in SHOWS:
    foundshow = find_all(show.strip(), LOCAL_SHOWS)
    for found in foundshow:
        SHOWSWITHPATH.append(found)
    # don't count multiple copies of the same show
    # and don't count if the show isn't found
    if len(foundshow) > 0:
        SHOWCOUNTER += 1

print "==================================================="
if len(SHOWSWITHPATH) > 0:
    print len(SHOWSWITHPATH), " local files found for", SHOWCOUNTER, "shows in your played list:\n"
    for showpath in SHOWSWITHPATH:
        print "\t", showpath.strip()

# TODO: move the shows from source to target
# TODO: capture what user ran sudo, for later chown usage
# TODO: chown files/folders because sudo creates them as root

print "\n\nnew code\n\n"

# replicate directory structure at destination
for src_dir, dirs, files in os.walk(LOCAL_SHOWS):
    dst_dir = src_dir.replace(LOCAL_SHOWS, REMOTE_SHOWS, 1)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

# TODO: why doesn't having the file open lock it for move/rm?
# TODO: try holding the file open with another program
# TODO: open file handles in /proc? or what is osx equiv of /proc?
for src_file in SHOWSWITHPATH:
    dst_file = src_file.replace(LOCAL_SHOWS, REMOTE_SHOWS)
    # test if file exists in destination and remove it
    if os.path.exists(dst_file):
        os.remove(dst_file)
    shutil.move(src_file, dst_dir)

# TODO: print a cool progress hash and percentage
# TODO: run on usb connect event

print "\nEnd..."
