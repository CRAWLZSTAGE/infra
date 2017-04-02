import sys
import signal

def handler(signum, frame):
    sys.exit(1)

signal.signal(signal.SIGTERM, handler)


import SimpleHTTPServer
import SocketServer

PORT = 80

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()