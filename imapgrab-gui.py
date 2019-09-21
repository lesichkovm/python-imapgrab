#!/usr/bin/env python

# IMAP Grab Graphical User Interface (GUI)

# This program is a gui frontend to ImapGrab.
# It must be run in the same directory as
# imapgrap.py. Also, the following files must
# must also be in the same directory:
#    1) imapgrab-gui.glade
#    2) imapgrab-gui-about.glade
#    3) imapgrab_logo_plain.svg

# Dependencies:
#   1) python-gtk2 2.0+ (i.e. pygtk 2.0+)

import gtk
import gtk.glade
import gobject
import subprocess

class imapgrab_gui:

  #Initial gui loader
  def __init__(self):
    #Load glade gui file
    self.gui = gtk.glade.XML("imapgrab-gui.glade")
    #Define functions for button clicks
    dic = { "on_list_clicked" : self.show_list,
            "on_select_all_clicked" : self.select_all,
            "on_select_none_clicked" : self.select_none,
            "on_download_clicked" : self.download_mail,
            "on_menu_gmail_activate" : self.gmail_preset,
            "on_menu_about_activate" : self.about,
            "on_menu_quit_clicked" : self.destroy,
            "on_close_clicked" : self.destroy,
            "on_imapgrab-gui_destroy" : self.destroy }
    #Connect functions to gui
    self.gui.signal_autoconnect(dic)

    #Set details display to a text buffer
    self.details = self.gui.get_widget("details")
    self.txtbuffer = gtk.TextBuffer(None)
    self.details.set_buffer(self.txtbuffer)
    return

  #Listing mailboxes function
  def show_list(self,widget):
    #Get login info
    self.username = self.gui.get_widget("username").get_text()
    self.password = self.gui.get_widget("password").get_text()
    self.server = self.gui.get_widget("server").get_text()
    self.port = self.gui.get_widget("port").get_text()
    self.ssl = self.gui.get_widget("ssl").get_active()

    #Use default ports if no port specified
    if self.port == "":
      if self.ssl is True:
        self.port = "993"
      else:
        self.port = "143"

    #Create arguments for cli
    self.cmd = ["python", "imapgrab.py", "--quiet", "-l",
                "-u", self.username, "-p", self.password,
                "-s", self.server, "-P", self.port]
    if self.ssl is True:
      self.cmd.append("-S")

    #Check to see if subprocess already exists
    if hasattr(self, "list_command") is True and self.list_command.poll() is None:
      self.txtbuffer.insert_at_cursor("Waiting for current list process to finish...\n")
      self.details.scroll_to_mark(self.txtbuffer.get_insert(), 0)
    else:
      #Start command
      self.list_command = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      self.txtbuffer.insert_at_cursor("Retrieving mailbox list...\n")
      self.details.scroll_to_mark(self.txtbuffer.get_insert(), 0)

      #Create checkbox list when output is done
      gobject.io_add_watch(self.list_command.stdout, gobject.IO_HUP, self.grab_list)

    return

  #Wait until list subprocess it done
  def grab_list(self, output, condition):
    #Checks if subproces is done
    if condition == gobject.IO_HUP:
      #Creates list of mailboxes from command output
      output = output.read()
      self.ig_list = output.split("\n")
      if self.ig_list[-1] == "":
        self.ig_list = self.ig_list[0:-1]

      #Clears mailbox list of previous entries
      self.gui.get_widget("list_vbox").foreach(lambda \
        widget:self.gui.get_widget("list_vbox").remove(widget))

      #Creates checkbox for each mailbox
      self.button = []
      for i in range(len(self.ig_list)):
        self.button.append(gtk.CheckButton(self.ig_list[i]))
        self.gui.get_widget("list_vbox").pack_start(self.button[i])
      self.gui.get_widget("list_vbox").show_all()

      #Prints success in details section
      error = self.list_command.stderr.read()
      if error == "":
        self.txtbuffer.insert_at_cursor("List download: Sucess\n")
        self.details.scroll_to_mark(self.txtbuffer.get_insert(), 0)
      else:
        error = error.split("\n")
        self.txtbuffer.insert_at_cursor("List download: Failed\n" + error[-2] + "\n")
        self.details.scroll_to_mark(self.txtbuffer.get_insert(), 0)
      return False

    return True

  def select_all(self,widget):
    #Activates all of the checkboxes in the mailbox list
    for i in range(len(self.button)):
      self.button[i].set_active(True)
    return

  def select_none(self,widget):
    #Deactivates all of the checkboxes in the mailbox list
    for i in range(len(self.button)):
      self.button[i].set_active(False)
    return

  def download_mail(self,widget):
    #Creates list of mailboxes to download
    self.mailboxes = []
    for i in range(len(self.button)):
      if self.button[i].get_active() is True:
        self.mailboxes.append(self.button[i].get_label())

    #Creates string of mailboxes to downoload
    mailbox_string = ""
    #Replace commas with special character
    for i in self.mailboxes:
      i.replace(",","{,}")
      mailbox_string += i + ", "
    #Removes last comma
    if mailbox_string[-2:] == ", ":
      mailbox_string = mailbox_string[:-2]
    #Adds to command arguments
    self.cmd.append("-m")
    self.cmd.append(mailbox_string);

    #Gets format
    if self.gui.get_widget("maildir").get_active() is True:
      self.cmd.append("-M")

    #Gets location to save
    folder = self.gui.get_widget("folder").get_filename()
    self.cmd.append("-f")
    self.cmd.append(folder)

    #Changes -l to -d
    if "-l" in self.cmd:
      self.cmd[self.cmd.index("-l")] = "-d"

    #Remove --quiet
    if "--quiet" in self.cmd:
      self.cmd.remove("--quiet")

    #Check to see if subprocess already exists
    if hasattr(self, "download_command") is True and self.download_command.poll() is None:
      self.txtbuffer.insert_at_cursor("Waiting for current download process to finish...\n")
      self.details.scroll_to_mark(self.txtbuffer.get_insert(), 0)
    else:
      #Send login info to imapgrab cli
      self.download_command = subprocess.Popen(self.cmd, stdout=subprocess.PIPE)
      gobject.io_add_watch(self.download_command.stdout, gobject.IO_IN | gobject.IO_HUP, self.display_details)
      self.txtbuffer.insert_at_cursor("Beginning downloads...\n")
      self.details.scroll_to_mark(self.txtbuffer.get_insert(), 0)

    return

  #Update stdout to textbuffer function
  def display_details(self, source, condition):
    #Checks if subprocess has stdout, sends output to textbuffer
    if condition == gobject.IO_IN:
      line = source.readline()
      self.txtbuffer.insert_at_cursor(line)
      self.details.scroll_to_mark(self.txtbuffer.get_insert(), 0)
    if condition == gobject.IO_IN | gobject.IO_HUP:
      line = source.read()
      self.txtbuffer.insert_at_cursor(line)
      self.details.scroll_to_mark(self.txtbuffer.get_insert(), 0)
      return False
    if condition == gobject.IO_HUP:
      return False

    return True

  #Display's about screen
  def gmail_preset(self,widget):
    self.server = self.gui.get_widget("server").set_text("imap.gmail.com")
    self.port = self.gui.get_widget("port").set_text("993")
    self.ssl = self.gui.get_widget("ssl").set_active(True)

  #Display about window
  def about(self,widget):
    #Load glade aboutgui file
    self.about_gui = gtk.glade.XML("imapgrab-gui-about.glade")
    dic = { "gtk_widget_destroy" : self.about_close }
    #Connect functions to gui
    self.about_gui.signal_autoconnect(dic)
    self.about_gui.get_widget("about_imapgrab").show()

  #Close about window
  def about_close(self,response_id,user_param):
    self.about_gui.get_widget("about_imapgrab").destroy()

  #Destroy window/gtk function
  def destroy(self,widget):
    #Kill subprocesses if they exist
    if hasattr(self, "list_command") is True and self.list_command.poll() is None:
      print "Waiting for list process to finish..."
      self.list_command.wait()
    if hasattr(self, "download_command") is True and self.download_command.poll() is None:
      print "Waiting for download process to finish..."
      self.download_command.wait()
    #Kills gui
    gtk.main_quit()

#Starts gtk and loads gui
app=imapgrab_gui()
gtk.main()
