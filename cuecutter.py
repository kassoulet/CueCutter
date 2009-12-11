#!/usr/bin/env python

"""
CueCutter

mp3splt Gtk Front-End

mp3splt splits cue + audiofile to multiple audio files, without recompressing.

(c) 2009 Gautier Portet <kassoulet gmail com>
"""


import os
from urllib import url2pathname
from urlparse import urlparse

import pygtk
pygtk.require('2.0')
import gtk
import gobject


def extract_filename_from_cue(filename):
    try:
        for line_count, line in enumerate(file(filename)):
            if line.startswith('FILE'):
                return '"'.join(line.split('"')[1:-1])
            if line_count > 10:
                return
    except IOError:
        return

def check_mp3splt():
    retcode = os.system('mp3splt -v > /dev/null')
    if retcode != 0:
        msg = 'I need mp3splt!'
        print msg
        dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
            gtk.BUTTONS_OK, msg)
        dlg.run()
        dlg.hide()
        raise SystemExit

check_mp3splt()


# -m m3u_file

def split(**kwargs):
    args = '-Q -c "%(cue)s" -d "%(folder)s" -o @n-@p-@t "%(mp3)s"'
    args = args % kwargs

    retcode = os.system('mp3splt '+ args)
    return retcode == 0


def idle(func):
    def wrapper(*args, **kwargs):
        def task():
            func(*args, **kwargs)
        gobject.idle_add(task)
    return wrapper


class Window:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('delete_event', self.delete_event)
        self.window.connect('destroy', self.destroy)
        self.window.set_border_width(12)
        self.window.set_size_request(256+24, 200)

        self.label = gtk.Label('Drop cue files here...')

        self.window.drag_dest_set(gtk.DEST_DEFAULT_ALL,[
            ('text/uri-list',0,0),
            ('text/plain',0,0),
            ('STRING',0,0)],
            gtk.gdk.ACTION_COPY|gtk.gdk.ACTION_MOVE)

        self.window.connect('drag_data_received', self.on_drag_data_received)
        self.window.show_all()

        global bitmap_data
        self.logo = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file('/tmp/cuecutter.svg')
        self.logo.set_from_pixbuf(pixbuf)

        vbox = gtk.VBox(homogeneous=False, spacing=12)

        vbox.add(self.logo)
        vbox.add(self.label)
        self.window.add(vbox)

        self.window.show_all()

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def on_drag_data_received(self, widget, drag_context, x, y, selection_data, info, timestamp):
        files = selection_data.data.split()
        drag_context.drop_finish(True, timestamp)
        for filename in files:
            filename = url2pathname(filename)
            url = urlparse(filename, 'file')
            if url.scheme != 'file':
                print 'cannot read:', filename
            cue = url.path

            self.process_cue(cue)
            
    @idle
    def process_cue(self, cue):
        media = extract_filename_from_cue(cue)
        if not media:
            print 'error parsing:', cue
            self.label.set_text('Error reading cue file!')
            return
        media = os.path.join(os.path.dirname(cue), media)
        self.label.set_text('Cutting %s' % os.path.basename(media))
        self.cut(cue, media)

    @idle
    def cut(self, cue, media):
        folder = os.path.splitext(cue)[0]
        success = split(cue=cue, mp3=media, folder=folder)
        if success:
            self.label.set_text('Done.')
        else:
            self.label.set_text('Error!')


bitmap_data = '''@BITMAP@'''

from bz2 import decompress
from base64 import decodestring

file('/tmp/cuecutter.svg', 'w').write(decompress(decodestring(bitmap_data)))

window = Window()
gtk.main()

