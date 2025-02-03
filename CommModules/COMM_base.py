#!/usr/bin/env python

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def try_parse_float(s):
    try:
        return float(s)
    except ValueError:
        return None

class COMM_base():
    def __init__(self, dev=None, writeCallback=None, readCallback=None):
        self.dev = dev
        self.writeCallback = writeCallback
        self.readCallback = readCallback

    def _write(self, s):
        if self.dev:
            self.dev.write(s)
            if self.writeCallback:
                self.writeCallback(s)

    def _readline(self):
        if self.dev:
            res = self.dev.readline().strip()
            if self.readCallback:
                self.readCallback(res)
        return res

    def _queryString(self, command, retry=4):
        self._write(command)
        return self._readline()

    def _queryFloat(self, command, retry=4):
        self._write(command)
        res = self._readline()
        return try_parse_float(res)

    def _queryArray(self, command, retry=4):
        self._write(command)
        res = self._readline()
        #print(res)
        res = res.split(',')
        a = []
        for s in res:
            a.append( try_parse_float(s) )
        return a

    def open(self, dev=False):
        return

    def disconnect(self):
        return

    def isConnected(self):
        return False
