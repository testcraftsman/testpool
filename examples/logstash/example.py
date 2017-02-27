"""
push structured content to logstash.
"""
import socket
import json
import sys

HOST = '127.0.0.1'
PORT = 9563

try:
    SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
    sys.stderr.write("[ERROR] %s\n" % msg[1])
    sys.exit(1)

try:
    SOCK.connect((HOST, PORT))
except socket.error, msg:
    sys.stderr.write("[ERROR] %s\n" % msg[1])
    sys.exit(2)

MSG = {'@message': 'python test message', '@tags': ['python', 'test']}

SOCK.send(json.dumps(MSG))
SOCK.close()
sys.exit(0)
