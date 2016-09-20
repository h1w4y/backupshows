#!/usr/local/bin/python
"""backs up watched shows from local drive to some other storage
dependency on python psutil library
dependency on mpv
dependency on mpv playlist addon written in .lua
"""

import os
import shutil
import psutil

LOCAL_SHOWS = "/Users/mike/Movies/TV/"
REMOTE_SHOWS = "/Users/mike/Movies/TV2/"

# the name of the movie player process
PROCNAME = "mpv"
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


print ""
print "local directory set to: " + LOCAL_SHOWS
print "remote directory set to: " + REMOTE_SHOWS
print ""

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
print "These ", SHOWCOUNTER, " Shows from your \"played\" list where found locally:\n"
for show in SHOWSWITHPATH:
    print show

# remake the SHOWS list from the SHOWSWITHPATH list that contains full paths
SHOWS = []
for show in SHOWSWITHPATH:
    SHOWS.append(os.path.basename(show))

# remove duplicates from the SHOWS list
SHOWS = list(set(SHOWS))

print "==================================================="

PLAYINGNOW = []
# iterate through all running processes (requires sudo/root)
# if one of our shows is currently playing, add it to a PLAYINGNOW list
for process in psutil.process_iter():
    cmdline = process.cmdline()
    # when the movie player process is found
    if PROCNAME in cmdline:
        # compare our list of shows
        for show in SHOWS:
            # to the last element of the commandline arguments of the movieplayer process
            # should do something better here because the movie name may not always be the last arg
            if show.strip() in os.path.basename(cmdline[-1]):
                PLAYINGNOW.append(show)

PLAYINGNOWCOUNT = len(PLAYINGNOW)

if PLAYINGNOWCOUNT == 0:
    print PLAYINGNOWCOUNT, " shows are currently playing. All found shows will be moved."

if len(PLAYINGNOW) > 0:
    print "These ", PLAYINGNOWCOUNT, " Shows are currently playing an won't be moved:\n"
    for show in PLAYINGNOW:
        print "\t", show.strip()

# don't move shows that are currently playing
for playingshow in PLAYINGNOW:
    if playingshow in SHOWS:
        SHOWS.remove(playingshow)
    else:
        print "This show is playing but doesn't appear in your \"played\" list: ", playingshow

print "==================================================="
if len(SHOWS) > 0:
    print "These ", len(SHOWS), " Shows will be moved to archive:\n"
    for show in SHOWS:
        print "\t", show.strip()

# set up the final list that contains file paths to shows that will be moved
# temp list to avoid issue with modifying the list being iterated over
SHOWSWITHPATH_TEMP = list(SHOWSWITHPATH)
for showpath in SHOWSWITHPATH:
    if os.path.basename(showpath) not in SHOWS:
        SHOWSWITHPATH_TEMP.remove(showpath)
SHOWSWITHPATH = list(SHOWSWITHPATH_TEMP)

print "==================================================="
if len(SHOWSWITHPATH) > 0:
    print "These ", len(SHOWSWITHPATH), " files will be moved:\n"
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

#        for file_ in files:
#            src_file = os.path.join(src_dir, file_)
#            dst_file = os.path.join(dst_dir, file_)
#            if os.path.exists(dst_file):
#                os.remove(dst_file)
#                shutil.move(src_file, dst_dir)
#
# TODO: print a cool progress hash and percentage
# TODO: run on usb connect event
# TODO: figure out non-sudo way to do the process check

print "\nEnd..."
