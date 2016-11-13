import subprocess
import string
import pickle

wmctrl_columns = {'id': 0, 'desktop': 1, 'wm_class': 2, 'host': 3, 'title': 4}
tmp_last_active_window_file = "/home/lkrcal/wmctrl-cycle/wmctrl-cycle.pickle"

in_pattern = "Sublime".lower()
if (len(in_pattern) < 1):
    print "Missing in_pattern parameter."
    exit(1);
# in_wmclass = "sublime_text".lower()

proc = subprocess.Popen(["wmctrl", "-l", "-x"], stdout=subprocess.PIPE, shell=False)
(out, err) = proc.communicate()
xwindows = string.split(out, '\n')

# Get active windows from xprop
proc = subprocess.Popen(["xprop", "-root", "_NET_ACTIVE_WINDOW"], stdout=subprocess.PIPE, shell=False)
(out, err) = proc.communicate()
active_xid = string.split(out)[4][2:]

# Load information about last open windows for in_patterns
with open(tmp_last_active_window_file, 'rb') as handle:
    app_last_active_window_of_apps = pickle.loads(handle.read())
    print "app_last_active_window_of_apps", app_last_active_window_of_apps

# Filter all xwindows to find active window and all matched windows
app_matched_xwindows = list()
app_curr_active_window = False
active_window_matched = -1
for i,xwin in enumerate(xwindows):
    if not xwin:
        continue
    print "xwindow", xwin

    # Get the X id, WM_CLASS and title of the X window
    xdata = string.split(xwin, maxsplit=4)
    xid = xdata[wmctrl_columns['id']]
    wmclass = xdata[wmctrl_columns['wm_class']]
    title = xdata[wmctrl_columns['title']].lower()
    print "xid", xid
    print "wmclass", wmclass
    print "title", title
    
    # Matched window by title or by wmclass
    matched = False
    if (title.find(in_pattern) >= 0 or wmclass.find(in_pattern) >= 0):
        print "MATCH"
        app_matched_xwindows.append(xid)
        matched = True

    # Check if this is the active window
    # Note we make sure the match is at the rightmost position, since the hexa string returned by xprop (active_xid)
    # is not 0-padded, unlike the string from wmctrl
    if (xid.rfind(active_xid) + len(active_xid) == len(xid)):
        print "ACTIVE", xid.rfind(active_xid), len(active_xid), len(xid)
        app_curr_active_window = xid
        app_last_active_window_of_apps[in_pattern] = xid
        if (matched):
            active_window_matched = i


print "---------"
print "app_matched_xwindows", app_matched_xwindows
print "app_curr_active_window", app_curr_active_window
print "app_last_active_window_of_apps", app_last_active_window_of_apps
print "active_window_matched", active_window_matched


if (not len(app_matched_xwindows)):
    print "No xwindow matched the query."
    to_activate = False


# If the active window is in the list of matched windows, activate the next one in the list
if (active_window_matched):
    if (len(app_matched_xwindows) == 1):
        print "The only matched window is active."
        to_activate = False
    to_activate = app_matched_xwindows[(i+1)%len(app_matched_xwindows)]
# Otherwise active the last window active for given in_pattern
else:
    if (app_last_active_window_of_apps[in_pattern]):
        to_activate = app_last_active_window_of_apps[in_pattern]
        if (app_matched_xwindows.find(to_activate) < 0):
            print "Last window that was active for pattern:",in_pattern,"not open anymore."
            del(app_last_active_window_of_apps[in_pattern])
            print "Activating first window of all the matched windows."
            to_activate = app_matched_xwindows[0]
        else:
            print "Activating last window that was active for pattern:",in_pattern
    else:
        print "Activating first window of all the matched windows."
        to_activate = app_matched_xwindows[0]
        exit(0);


# Save information about last open windows for in_patterns
with open(tmp_last_active_window_file, 'wb') as handle:
  pickle.dump(app_last_active_window_of_apps, handle)

# Switch focus to appropriate window
if (to_activate):
    proc = subprocess.Popen(["wmctrl", "-i", "-a", to_activate], stdout=subprocess.PIPE, shell=False)
    (out, err) = proc.communicate()



# a = {
#   'a': 1,
#   'b': 2
# }

# with open('file.txt', 'wb') as handle:
#   pickle.dump(a, handle)

# with open('file.txt', 'rb') as handle:
#   b = pickle.loads(handle.read())

# print a == b # True