import subprocess
import string

wmctrl_columns = {'id': 0, 'desktop': 1, 'wm_class': 2, 'host': 3, 'title': 4}

in_pattern = "Sublime".lower()

proc = subprocess.Popen(["wmctrl", "-l", "-x"], stdout=subprocess.PIPE, shell=False)
(out, err) = proc.communicate()
xwindows = string.split(out, '\n')

proc = subprocess.Popen(["xprop", "-root", "_NET_ACTIVE_WINDOW"], stdout=subprocess.PIPE, shell=False)
(out, err) = proc.communicate()
active_xwindow_id = string.split(out)[4]
print "x_active_window", active_xwindow_id

# Filter all xwindows of a given app
app_xwindows = list()
for xwin in xwindows:
    if not xwin:
        continue
    print "xwindow", xwin
    xdata = string.split(xwin, maxsplit=4)
    print "xdata", xdata
    title = xdata[wmctrl_columns['title']].lower()
    print "title", title
    if (title.find(in_pattern) >= 0):
        print "MATCH"
        app_xwindows.append(xdata)

to_activate = "0x04a00003"

# proc = subprocess.Popen(["wmctrl", "-i", "-a", to_activate], stdout=subprocess.PIPE, shell=False)
# (out, err) = proc.communicate()