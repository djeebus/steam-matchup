import webapp2 
import logging

import cgi
import urlparse
import sys
import os
import steam

import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))


def quoteattr(s):
    qs = cgi.escape(s, 1)
    return '"%s"' % (qs,)

import gaesessions
from openid.store import gaestore
from openid.consumer import consumer
from openid.oidutil import appendArgs
from openid.cryptutil import randomString
from openid.extensions import pape, sreg

OPENID_PROVIDER_NAME = "Steam"

OPENID_PROVIDER_URL = "http://steamcommunity.com/openid"


steam_client = steam.ApiClient()
games = steam_client.get_all_games()


class OpenIDRequestHandler(webapp2.RequestHandler):
    """Request handler that knows how to verify an OpenID identity."""

    def getConsumer(self, stateless=False):
        if stateless:
            store = None
        else:
            store = gaestore.GAEStore()
        return consumer.Consumer(self.getSession(), store)

    def getSession(self):
        """Return the existing session or a new session"""
        session = gaesessions.get_current_session()
        if not session.has_key( 'id' ):
           # new session
           sid = randomString(16, '0123456789abcdef')
           session['id'] = sid
        
        return session

    def setSessionCookie(self):
        sid = self.getSession()['id']
        session_cookie = '%s=%s;' % (gaesessions.COOKIE_NAME_PREFIX, sid)
        self.response.headers['Set-Cookie'] = session_cookie

    def post(self):
        self.doVerify(OPENID_PROVIDER_URL)

    def get(self):
        self.doProcess()

    def doVerify(self, openid_url):
        """Initiating OpenID verification.
        """

        # First, make sure that the user entered something
        if not openid_url:
            self.render('Enter your OpenID Identifier',
                        css_class='error', form_contents=openid_url)
            return

        immediate = 'immediate' in self.request.GET
        use_sreg = 'use_sreg' in self.request.GET
        use_pape = 'use_pape' in self.request.GET
        use_stateless = 'use_stateless' in self.request.GET

        oidconsumer = self.getConsumer(stateless = use_stateless)
        try:
            request = oidconsumer.begin(openid_url)
        except consumer.DiscoveryFailure, exc:
            fetch_error_string = 'Error in discovery: %s' % (
                cgi.escape(str(exc[0])))
            self.render(fetch_error_string,
                        css_class='error',
                        form_contents=openid_url)
                        
            logging.error("Error in discovery on %s: %s" % (cgi.escape(openid_url), cgi.escape(str(exc[0]))) )

        else:
            if request is None:
                msg = 'No OpenID services found for <code>%s</code>' % (
                    cgi.escape(openid_url),)
                self.render(msg, css_class='error', form_contents=openid_url)
                
                logging.error("No OpenID services found for %s" % (cgi.escape(openid_url)) )
            else:
                # Then, ask the library to begin the authorization.
                # Here we find out the identity server that will verify the
                # user's identity, and get a token that allows us to
                # communicate securely with the identity server.
                if use_sreg:
                    self.requestRegistrationData(request)

                if use_pape:
                    self.requestPAPEDetails(request)

                trust_root = self.request.path_url
                return_to = self.buildURL("auth/")
                if request.shouldSendRedirect():
                    redirect_url = request.redirectURL(trust_root, return_to, immediate=immediate)
                    self.response.status = 302
                    self.response.headers['Location'] = redirect_url

                else:
                   #self.response.write("go back to %s" % (self.request.host_url + "/process") )
                    self.response.write(
                        request.htmlMarkup(
                            trust_root, return_to,
                            form_tag_attrs={'id':'openid_message'},
                            immediate=immediate)
                        )

    def requestRegistrationData(self, request):
        sreg_request = sreg.SRegRequest(
            required=['nickname'], optional=['fullname', 'email'])
        request.addExtension(sreg_request)

    def requestPAPEDetails(self, request):
        pape_request = pape.Request([pape.AUTH_PHISHING_RESISTANT])
        request.addExtension(pape_request)

    def doProcess(self):
        """Handle the redirect from the OpenID server.
        """
        oidconsumer = self.getConsumer()

        # Ask the library to check the response that the server sent
        # us.  Status is a code indicating the response type. info is
        # either None or a string containing more information about
        # the return type.
        url = "http://" + self.request.headers.get("Host") + self.request.path
        info = oidconsumer.complete(self.request.GET, url)
        
        css_class = 'error'
        sreg_resp = None
        pape_resp = None
        display_identifier = info.getDisplayIdentifier()

        if info.status == consumer.FAILURE and display_identifier:
            # In the case of failure, if info is non-None, it is the
            # URL that we were verifying. We include it in the error
            # message to help the user figure out what happened.
            fmt = "Verification of %s failed: %s"
            message = fmt % (cgi.escape(display_identifier), info.message)
            logging.error(message)
        elif info.status == consumer.SUCCESS:
            steam_id = info.message.getArg('http://specs.openid.net/auth/2.0', 'claimed_id')
            steam_id = steam_id[steam_id.rfind('/') + 1:]
            self.response.set_cookie('profile_id', steam_id)
            redirect_url = self.buildURL('/index.html')
            self.redirect(redirect_url)
            return
        elif info.status == consumer.CANCEL:
            message = 'Verification cancelled'
        elif info.status == consumer.SETUP_NEEDED:
            # This means auth didn't succeed, but you're welcome to try
            # non-immediate mode.
            if info.setup_url:
                message = '<a href=%s>Setup needed</a>' % (quoteattr(info.setup_url),)
            else:
                # This means auth didn't succeed, but you're welcome to try
                # non-immediate mode.
                message = 'Setup needed'

        else:
            # Either we don't understand the code or there is no
            # openid_url included with the error. Give a generic
            # failure message. The library should supply debug
            # information in a log.
            message = 'Verification failed.'

        logging.info(message)

        self.render(message, css_class, display_identifier,
                    sreg_data=sreg_resp, pape_data=pape_resp)

    def buildURL(self, action, **query):
        """Build a URL relative to the server base url, with the given
        query parameters added."""
        base = urlparse.urljoin(self.request.host_url, action)
        return appendArgs(base, query)

    def renderSREG(self, registration_data):
        if not registration_data:
            self.response.write(
                '<div class="alert">No registration data was returned</div>')
        else:
            sreg_list = registration_data.items()
            sreg_list.sort()
            self.response.write(
                '<h2>Registration Data</h2>'
                '<table class="sreg">'
                '<thead><tr><th>Field</th><th>Value</th></tr></thead>'
                '<tbody>')

            odd = ' class="odd"'
            for k, v in sreg_list:
                field_name = sreg.data_fields.get(k, k)
                value = cgi.escape(v.encode('UTF-8'))
                self.response.write(
                    '<tr%s><td>%s</td><td>%s</td></tr>' % (odd, field_name, value))
                if odd:
                    odd = ''
                else:
                    odd = ' class="odd"'

            self.response.write('</tbody></table>')

    def renderPAPE(self, pape_data):
        if not pape_data:
            self.response.write(
                '<div class="alert">No PAPE data was returned</div>')
        else:
            self.response.write('<div class="alert">Effective Auth Policies<ul>')

            for policy_uri in pape_data.auth_policies:
                self.response.write('<li><tt>%s</tt></li>' % (cgi.escape(policy_uri),))

            if not pape_data.auth_policies:
                self.response.write('<li>No policies were applied.</li>')

            self.response.write('</ul></div>')

    def render(self, message=None, css_class='alert', form_contents=None,
               status=200, title="Syndicate OpenID",
               sreg_data=None, pape_data=None):
        """Render a page."""
        self.response.status = status
        self.pageHeader(title)
        if message:
            self.response.write("<div class='%s'>" % (css_class,))
            self.response.write(message)
            self.response.write("</div>")

        if sreg_data is not None:
            self.renderSREG(sreg_data)

        if pape_data is not None:
            self.renderPAPE(pape_data)

        self.pageFooter(form_contents)

    def pageHeader(self, title):
        """Render the page header"""
        self.setSessionCookie()
        self.response.headers['Content-type'] = 'text/html; charset=UTF-8'
        self.response.write('''\
<html>
  <head><title>%s</title></head>
  <style type="text/css">
      * {
        font-family: verdana,sans-serif;
      }
      body {
        width: 50em;
        margin: 1em;
      }
      div {
        padding: .5em;
      }
      tr.odd td {
        background-color: #dddddd;
      }
      table.sreg {
        border: 1px solid black;
        border-collapse: collapse;
      }
      table.sreg th {
        border-bottom: 1px solid black;
      }
      table.sreg td, table.sreg th {
        padding: 0.5em;
        text-align: left;
      }
      table {
        margin: 0;
        padding: 0;
      }
      .alert {
        border: 1px solid #e7dc2b;
        background: #fff888;
      }
      .error {
        border: 1px solid #ff0000;
        background: #ffaaaa;
      }
      #verify-form {
        border: 1px solid #777777;
        background: #dddddd;
        margin-top: 1em;
        padding-bottom: 0em;
      }
  </style>
  <body>
    <h1>%s</h1>
    <p>
      This is the OpenID front-end to Syndicate.
    </p>
''' % (title, title))

    def pageFooter(self, form_contents):
        """Render the page footer"""
        if not form_contents:
            form_contents = ''

        if form_contents.startswith(OPENID_PROVIDER_URL):
            form_contents = form_contents[len(OPENID_PROVIDER_URL):]

        self.response.write('''\
    <div id="verify-form">
      <form method="get" accept-charset="UTF-8" action=%s>
        VICCI e-mail address:
        <input type="text" name="openid_username" value=%s />
        <input type="submit" value="Verify" /><br />
        <input type="checkbox" name="immediate" id="immediate" /><label for="immediate">Use immediate mode</label>
        <input type="checkbox" name="use_sreg" id="use_sreg" /><label for="use_sreg">Request registration data</label>
        <input type="checkbox" name="use_pape" id="use_pape" /><label for="use_pape">Request phishing-resistent auth policy (PAPE)</label>
        <input type="checkbox" name="use_stateless" id="use_stateless" /><label for="use_stateless">Use stateless mode</label>
      </form>
    </div>
  </body>
</html>
''' % (quoteattr(self.buildURL('verify')), quoteattr(form_contents)))

application = webapp2.WSGIApplication(
    [('/auth/', OpenIDRequestHandler)],
    debug=True, config={'webapp2_extras.sessions': {'secret_key': 'omgzwtfbbq'}})
