#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyinotify, os, shutil

# This script keeps on folder synchronized with the other. 
# It hooks file create, deletion, modification to keep track
# from a source folder to a destination folder.



# Copyright (c) 2012, François Serman <fser@code-libre.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#    - Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    - Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in
#      the documentation and/or other materials provided with the
#      distribution.  
#    - Neither the name of the code-libre.org nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.




SRC='/home/fser/tmp/toto'
DST='/home/fser/.hubic'
DEBUG = True

def log(evt, filename):
    if (DEBUG):
        print "%s %s [ok]" % (evt, filename)

class EventHandler(pyinotify.ProcessEvent):

    def __init__(self):
        self.src_file = None
        self.dst_file = None
        self.mv = False

    # File or folder created
    def process_IN_CREATE(self, event):
        dst_file = event.pathname.replace(SRC, DST)
        try:
            log ("Creating %s" % ("directory" if (event.mask & pyinotify.IN_ISDIR) else "file"), event.pathname)

            if (event.mask & pyinotify.IN_ISDIR):
                os.mkdir(dst_file)
            else:
                shutil.copy(event.pathname, dst_file)
        except Exception as e:
            log("Exception happened:", e.strerror)



    # File or folder moved
    def process_IN_MOVED_TO(self, event):
        dst_file = event.pathname.replace(SRC,DST)
        if (self.mv == True):
            self.dst_file = dst_file
            os.rename(self.src_file, self.dst_file)
            self.dst_file = None
            self.src_file = None
            self.mv = False

    def process_IN_MOVED_FROM(self, event):
        dst_file = event.pathname.replace(SRC,DST)
        self.src_file = dst_file
        self.mv = True

    # File or folder deletion
    def process_IN_DELETE(self, event):
        dst_file = event.pathname.replace(SRC, DST)
        try:
            if (event.mask & pyinotify.IN_ISDIR):
                log ("Deleting directory: ", dst_file)
                os.rmdir(dst_file)
            else:
                log("Deleting file: ", dst_file)
                os.remove(dst_file)
        except OSError as e:
            log("Error:", e.strerror)


    # File edition
    def process_IN_CLOSE_WRITE(self, event):
        dst_file = event.pathname.replace(SRC, DST)
        log ("Modified: ", event.pathname)
        shutil.copy(event.pathname, dst_file)



if __name__ == "__main__":
    wm = pyinotify.WatchManager()
    watched = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE | pyinotify.IN_MOVED_TO | pyinotify.IN_MOVED_FROM
    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch(SRC, watched, rec=True, auto_add=True)
    notifier.loop()
    #import asyncore
    #asyncore.loop()
