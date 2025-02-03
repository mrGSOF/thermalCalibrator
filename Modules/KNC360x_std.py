class KNC3604U_std_base():
    def __init__(self, visa=False, dev='socket://localhost:7274', baudrate=None, writeCallback=None, readCallback=None):
        self.visa = visa
        self.DEV = dev
        self.writeCallback = writeCallback
        self.readCallback = readCallback
