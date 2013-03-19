import logging
import sys
import re
import redis

class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO, terminal=sys.stdout, debug=False, avname="channel"):
      self.terminal = terminal
      #self.formatter = logging.Formatter(fmt='%(asctime)s',datefmt='%Y-%m-%d %H:%M:%S')
      self.logger = logging.getLogger(logger)
      
      self.debug = debug
      self.log_level = log_level
      self.linebuf = ''
      self.r = redis.Redis("10.0.20.1")

      if not self.r.ping():
         self.r = None

      self.avname = avname
 
   def flush(self):
      pass

   def write(self, buf):
      
      if buf.startswith("DBG"):
         if self.debug:
            self.terminal.write("#DEBUG# - %s" % buf[3:].strip())
         self.logger.log(logging.DEBUG, buf[3:].strip())

      else:
         self.terminal.write( str(buf).strip() + "\n" ) 
         
         for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
            if line.startswith("+") and self.r:
               self.r.publish(self.avname, line)

def setLogger( debug=True, filelog="results.txt", avname="channel"):
   logging.basicConfig(
      
      level=logging.DEBUG if debug else logging.INFO,
      #format='%(asctime)s: %(levelname)s: %(name)s: %(message)s',
      format='%(asctime)s, %(levelname)s: %(message)s',
      datefmt='%Y-%m-%d %H:%M:%S',
      filename=filelog,
      filemode='w'
   )
   terminal = sys.stdout

   sys.stdout = StreamToLogger('STDOUT', logging.INFO, terminal, debug, avname = avname)
   sys.stderr = StreamToLogger('STDERR', logging.ERROR, terminal, avname = avname)
    

if __name__ == "__main__":
   setLogger(False, avname="Test")
   print "+ STATT"
   print "Test to standard out"
   print "DBG   test debug "
   raise Exception('Test to standard error')
