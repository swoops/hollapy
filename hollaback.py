#!/usr/bin/env python
import requests
import json
import time
from os.path import expanduser
import time

class hollaback(object):
    """
    Used to interact with the hollaback callback server
    """

    cred_file = expanduser("~") + "/.config/hollaback.json"
    color = True # color terminal

    def __init__(self, nick="default"):
        self.ses = requests.Session()
        self.nick = nick
        self.parse_cred_file()
        if not self.login():
            raise Exception("Login failed")

    def __del__(self):
        # I know __del__ is not ALWAYS called, and this does not always need to
        # be called. It is just freeing up resources on the server.
        url = "%s%s" % (self.serv, "/holla/logout.php")
        self.ses.get(url)

    def getvisit(self, token, num):
        url = "%s%s" % (self.serv, "/holla/getvisit.php")
        res = self.ses.get(url, params={"token":token, "num": num})
        try:
            return res.json()
        except:
            return res.content

    def block(self, token, visits=1, sleep=1, p=True, ppcheck=False, ppvisit=False, forever=False):
        """
        Block and wait until the callback url has reached `visits` number of
        vists. Check the Dict returned for "Success" == True. The returned dict
        is the result of the check() call, NOT it does not contain the last
        visit information. Use the "visisted" attribute to get the last visit
        index and request it again

        p=True will print the results as they are recieved
        sleep: seconds to sleep between checks
        """
        d = holla.check(token)
        if d["Success"] != True:
            return d;
        if p:
            if not ppcheck:
                ppcheck = self.ppcheck
            if not ppvisit:
                ppvisit = self.ppvisit

        prev = start = d[ "visited" ]
        last = start+visits
        while forever or d["visited"] < last:
            time.sleep(sleep)
            d = holla.check(token)
            if d["Success"] != True:
                return d
            if p and prev < d["visited"]:
                prev = d["visited"]
                ppcheck(d)
                ppvisit( self.getvisit(token, d["visited"]-1) )
        return d

    def _str_escape(self, s):
        """
        Attempts to replace bad characters with hex equivalent
        """
        return repr(s).replace("\\n", "\n").replace("'","")[1:]

    def ppcheck(self, check):
        """
        pretty prints the results of a check
        """
        msg = "[**] check: "
        if self.color:
            print("\033[92m%s%s\033[0m" % ( msg, check["token"] ))
            print("%-15s \033[94m%d\033[0m" % ("visited", check["visited"]))
        else:
            print("%s%s" % (msg, check["token"]))
            print("%-15s %d" % ("visited", check["visited"]))

        for key, value in check.iteritems():
            if value and key not in ["Success", "comment", "token", ]:
                print("%-15s %s" % (key, self._str_escape( value )))
        if check["comment"]:
            print("-- comment --\n%s\n---------" % self._str_escape( check["comment"] ))

    def ppvisit(self, visit):
        """
        pretty prints the visit information
        """
        msg = "[**] visit:"
        if self.color:
            print("\033[92m%s\033[0m" % msg)
        else:
            print(msg)
        for key, value in visit.iteritems():
            if value and key not in ["Success", "req"]:
                print("%-15s %s" % (key, self._str_escape( value )))
        print("-- req --")
        if self.color:
            print("\033[94m%s\033[0m" % self._str_escape( visit["req"] ))
        else:
            print(self._str_escape( visit["req"] ))
        print("---------")

    def login(self):
        """
        Log into the api server
        """
        url = "%s%s" % (self.serv, "/holla/login.php")
        res = self.ses.post(url, data=self.creds)

        if res.ok and res.json()["Success"]:
            return True
        else:
            return False

    def clean(self, token):
        """
        Tells the server it can clean up data associated to a token
        """
        url = "%s%s" % (self.serv, "/holla/clean_token.php")
        res = self.ses.get(url, params={"token":token})
        if res.status_code == 200:
            return True
        else:
            return False

    def check(self, token):
        url = "%s%s" % (self.serv, "/holla/check.php")
        res = self.ses.get(url, params={"token":token})
        try:
            return res.json()
        except:
            return res.content

    def enque(self, comment="", test_name="", cust_name="", reply_method="", ttl=0, consume=0):
        """
        Add a new callback URL to the server
        """
        url = "%s%s" % (self.serv, "/holla/save.php")
        res = self.ses.post(url, data=locals())
        return res.json()

    def parse_cred_file(self):
        with open(self.cred_file, "r") as fp:
            data = json.load(fp)[self.nick];
        self.creds = data["creds"]
        self.serv  = data["serv"]

def _holla_fail(msg):
    print(msg)
    exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Interact with a Hollaback Server")
    parser.add_argument('-q','--quick', action="store_true", help='Like tailing the logs for a single URL, ctrl+c to stop')
    parser.add_argument('-g','--get', action="store_true", help='Get a callback url')
    parser.add_argument('-c','--check', action="store_true", help='Check on a callback token (-t required)')
    parser.add_argument('-b','--block', action="store_true", help='Check every second until callback is used (-t required)')
    parser.add_argument('-t','--token', help='Token value')
    parser.add_argument('-v', '--visit',  help='Get details of visit for visit numer')
    parser.add_argument('--comment', help='Comment to save on server')
    parser.add_argument('--test_name', help='Test name to save on server')
    parser.add_argument('--cust_name', help='Customer name to save on server')
    parser.add_argument('--ttl', help='TTL of callback URL')
    parser.add_argument('--reply_method', help='How it should respond') # does not work on server yet
    parser.add_argument('--consume', help='Int number of times used before consumed')
    parser.add_argument('--clean', action="store_true", help='Remove token info from the server when you are done')
    parser.add_argument('--nc', action="store_true", help='Remove color display')

    args = parser.parse_args()
    if args.get and args.check:
       _holla_fail("To check and get at the same time is kinda foolish")


    holla = hollaback()
    if args.nc:
        holla.color = False
    if args.token:
        token = args.token
    else:
        token = ""
    if args.get or args.quick:
        if token: _holla_fail("Can't use token here, exiting")
        a = vars(args)
        a = {
            "comment"       :  args.comment,
            "test_name"     :  args.test_name,
            "cust_name"     :  args.cust_name,
            "reply_method"  :  args.reply_method,
            "ttl"           :  args.ttl,
            "consume"       :  args.consume
        }
        a = holla.enque(**a)
        print("token: %s" % a["token"])
        print("url: %s" % a["url"])
        token = a["token"]

    if args.visit:
        if not token:
            _holla_fail("Need token for visit info")
        num = args.visit
        d = holla.getvisit(token, num)
        if d["Success"] != True:
            _holla_fail("Could not get info for token %s\nmsg: %s" % ( token, d["msg"]))
        else:
            holla.ppvisit(d)
    elif args.check:
        if not token:
            _holla_fail("Need token to check")
        d = holla.check(token)
        if d["Success"] != True:
            _holla_fail("Could not get info for token %s\nmsg: %s" % ( token, d["msg"]))
        holla.ppcheck(d)
    elif args.block or args.quick:
        if not token and not token:
            _holla_fail("Need token to check")
        try:
            d = holla.block(token, forever=True)
            if d["Success"] != True:
                _holla_fail("Failed: %s " % d["msg"])
        except KeyboardInterrupt:
            print("cleaning up")

    if args.clean or args.quick:
        if not token:
            _holla_fail("Need a token to clean up")
        if holla.clean(token):
            print("Token cleaned up")
        else:
            _holla_fail("Failed to clean up token")
