import logging
import sys
import re

class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO, terminal=sys.stdout):
      self.terminal = terminal
      self.logger = logging.getLogger(logger)
      self.log_level = log_level
      self.linebuf = ''
 
   def write(self, buf):
      self.terminal.write(buf)
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())

def setLogger():
   logging.basicConfig(
      level=logging.DEBUG,
      #format='%(asctime)s: %(levelname)s: %(name)s: %(message)s',
      format='%(asctime)s: %(levelname)s: %(message)s',
      filename="results.txt",
      filemode='w'
   )
   terminal = sys.stdout

   sys.stdout = StreamToLogger('STDOUT', logging.INFO)
   sys.stderr = StreamToLogger('STDERR', logging.ERROR)
    

if __name__ == "__main__":
   setLogger()
   print "Test to standard out"
   raise Exception('Test to standard error')