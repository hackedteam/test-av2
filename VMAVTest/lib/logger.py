import logging
import sys
import re

class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO, terminal=sys.stdout, debug=False):
      self.terminal = terminal
      self.logger = logging.getLogger(logger)
      self.debug = debug
      self.log_level = log_level
      self.linebuf = ''
 
   def flush(self):
      pass

   def write(self, buf):
      
      if buf.startswith("DBG"):
         if self.debug:
            self.terminal.write("#DEBUG# - %s" % buf[3:].strip())
         self.logger.log(logging.DEBUG, buf[3:].strip())

      else:
         self.terminal.write(buf)
         
         for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

def setLogger( debug=True, filelog="results.txt"):
   logging.basicConfig(
      
      level=logging.DEBUG if debug else logging.INFO,
      #format='%(asctime)s: %(levelname)s: %(name)s: %(message)s',
      format='%(asctime)s: %(levelname)s: %(message)s',
      filename=filelog,
      filemode='w'
   )
   terminal = sys.stdout

   sys.stdout = StreamToLogger('STDOUT', logging.INFO, terminal, debug)
   sys.stderr = StreamToLogger('STDERR', logging.ERROR, terminal)
    

if __name__ == "__main__":
   setLogger(False)
   print "Test to standard out"
   print "DBG   test debug "
   raise Exception('Test to standard error')
