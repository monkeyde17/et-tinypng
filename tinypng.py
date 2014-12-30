from os.path import dirname
from urllib2 import Request, urlopen
from base64 import b64encode

import json
import threading
import os

key = "tyaaLBrU4fNVgiUT0b-HBWijI6AqWzuY"
outputdir = "ettinypng"

class shrink_thread(threading.Thread):
    def __init__(self, path, filename):
        threading.Thread.__init__(self)
        self.filename = filename
        self.path = path

    def run(self):
        tmppath = self.path + os.sep + outputdir
        if not os.path.isdir(tmppath):
            os.mkdir(tmppath)

        inputfile = self.path + os.sep + self.filename
        outputfile = tmppath + os.sep + self.filename
        
        request = Request("https://api.tinypng.com/shrink", open(inputfile, "rb").read())

        # add the auth
        auth = b64encode(bytes("api:" + key)).decode("ascii")
        request.add_header("Authorization", "Basic %s" % auth)

        # http post request
        response = urlopen(request)

        if response.getcode() == 201:
            # get the json result
            rejson = json.loads(response.read())

            # get the url
            result = urlopen(rejson["output"]["url"]).read()

            print "The output file : " + outputfile
            open(outputfile, "wb").write(result)

        else:
            # Something went wrong! You can parse the JSON body for details.
            print "Error Code : " + response.getcode()
            print "Compression failed"

        # end the thread
        self.thread_stop = True
           
    def stop(self):
        self.thread_stop = True

def shrink_png_by_path(path):
    if os.path.isdir(path):
        for curfile in os.listdir(path):
            if curfile.find(".png") != -1:
                print "the input file : " + path + os.sep + curfile
                shrink_thread(path, curfile).start()
    else:
        print "The path is invalid"

if __name__ == "__main__":
    shrink_png_by_path("testdir")

