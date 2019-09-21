# Python ImapGrab #

ImapGrab is a cli and gui program (written in Python) that allows you to log into an IMAP server, list mailboxes, and download selected mailboxes to mbox or maildir files. It requires getmail 4.8.2 or higher. The gui requires PyGtk 2.0 or higher.

Original: https://sourceforge.net/projects/imapgrab/ (now abandoned)

## Install Requirements ##

Requires getmail: http://pyropus.ca/software/getmail/documentation.html

```
apt install getmail
```

## Usage ##

```
imapgrab.py [-ldaSvMB] [-s] SERVER [-P] PORT [-u] USERNAME [-p] PASSWORD [-m] "BOX1,BOX2,..." [-f] DIRECTORY
```

### Possible arguments: ###
-    --list, -l        List the mailboxes available for download
-    --download, -d    Download mailboxes to separate files/folders
-    --mbox, -B        Download into Mbox format (optional, default)
-    --maildir, -M     Download into Maildir format (optional)
-    --all, -a         Force download all mail in a mailbox (optional)
-    --ssl, -S         Use SSL connection (optional)
-    --server, -s      IP or domain of server (required)
-    --port, -P        Port of server (optional)
-    --username, -u    Username for account (required)
-    --password, -p    Password for account (required)
-    --mailboxes, -m   Comma separated list of mailboxes to download 
                       (i.e. "Box1, Box2, Box3")
                       ("{,}" for non-separating commas)
                       ("_ALL_" for all mailboxes)
                       ("_ALL_, -Box1" to except Box1 from _ALL_)
                       ("_ALL_, -_Gmail_" to except [Gmail]* and [Google Mail]* folders)
                       ("_Gmail_" for all [Gmail]/* or [Google Mail]/* folders)
                       (required for -d)
-    --folder, -f      Path to folder
                       (optional, creates imapgrab folder in current directory as default)
-    --localuser, -L   User that writes to the mailboxes
                       (use only when involking imapgrab as root)
-    --quiet, -q       Don't display any output
-    --verbose, -v     Verbose output
-    --debug           Print debug output
-    --version         Print version
-    --about           Display detailed info
-    --help, -h        Print help with command options

## Examples: ##
1) List available mailboxes
```
imapgrab.py -l -s imap.example.com -u username -p password
```
2) Download "box1" and "box2" from server imap.example.com (save "box1.mbox" and "box2.mbox")
```
imapgrab.py -d -s imap.example.com -u username -p password -m "box1, box2"
```
3) Download all mailboxes except "box3"
```
imapgrab.py -d -s imap.example.com -u username -p password -m "_ALL_, -box3"
```
4) Download all Gmail custom labels and INBOX (none of the [Gmail]* mailboxes)
```
imapgrab.py -d -S -s imap.gmail.com -u username -p password -m "_ALL_, -_Gmail_"
```
5) Download Gmail label "receipts"
imapgrab.py -d -S -s imap.gmail.com -u username -p password -m "receipts"
