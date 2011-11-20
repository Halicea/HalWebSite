__author__ = 'KMihajlov'
# Adapted from http://pub.mowser.com/wiki/Main/CodeExamples
# With a few additions by Moof
# The latest version of this file is always available from:
# http://minidetector.googlecode.com/svn/trunk/minidetector/search_strings.txt
#
# This list is public domain, please feel free to use it for your own projects
# If HTTP_USER_AGENT.lower() contains any of these strings, it's a mobile
# Also include some games consoles, see below
search_strings = [
'sony',
'symbian',
'nokia',
'samsung',
'mobile',
'windows ce',
'epoc',
'opera mini',
'nitro',
'j2me',
'midp-',
'cldc-',
'netfront',
'mot',
'up.browser',
'up.link',
'audiovox',
'blackberry',
'ericsson,',
'panasonic',
'philips',
'sanyo',
'sharp',
'sie-',
'portalmmm',
'blazer',
'avantgo',
'danger',
'palm',
'series60',
'palmsource',
'pocketpc',
'smartphone',
'rover',
'ipaq',
'au-mic,',
'alcatel',
'ericy',
'up.link',
'docomo',
'vodafone/',
'wap1.',
'wap2.',
'plucker',
'480x640',
'sec',
'fennec',
'android',
'google wireless transcoder',
'nintendo',
'webtv',
'playstation',
]
def detect_mobile(request):
    """Adds a "mobile" attribute to the request which is True or False
       depending on whether the request should be considered to come from a
       small-screen device such as a phone or a PDA"""

    if request.headers.environ.has_key("HTTP_X_OPERAMINI_FEATURES"):
        #Then it's running opera mini. 'Nuff said.
        #Reference from:
        # http://dev.opera.com/articles/view/opera-mini-request-headers/
        return True

    if request.headers.environ.has_key("HTTP_ACCEPT"):
        s = request.headers.environ["HTTP_ACCEPT"].lower()
        if 'application/vnd.wap.xhtml+xml' in s:
            # Then it's a wap browser
            return True

    if request.headers.environ.has_key("HTTP_USER_AGENT"):
        # This takes the most processing. Surprisingly enough, when I
        # Experimented on my own machine, this was the most efficient
        # algorithm. Certainly more so than regexes.
        # Also, Caching didn't help much, with real-world caches.
        s = request.headers.environ["HTTP_USER_AGENT"].lower()
        for ua in search_strings:
            if ua in s:
                return True


    #Otherwise it's not a mobile
    return False