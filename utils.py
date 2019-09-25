import os

def ensureDirectory(dirname):
  """Make directory if it does not exist."""
  if not os.path.exists(dirname):
    os.makedirs(dirname)
    print '>>> made directory "%s"'%(dirname)
    if not os.path.exists(dirname):
      print '>>> failed to make directory "%s"'%(dirname)
  return dirname
  

def ensureFile(*paths,**kwargs):
  """Ensure file exists."""
  filepath = os.path.join(*paths)
  stop     = kwargs.get('stop',True)
  if '*' in filepath or '?' in filepath:
    exists = len(glob.glob(filepath))>0
  else:
    exists = os.path.isfile(filepath)
  if not exists and stop:
      raise OSError('File "%s" does not exist'%(filepath))
  return filepath
  

def warning(string,**kwargs):
  """Print warning with color."""
  pre    = kwargs.get('pre',  "") + "\033[1m\033[93mWarning!\033[0m \033[93m"
  title  = kwargs.get('title',"")
  if title: pre = "%s%s: "%(pre,title)
  string = "%s%s\033[0m"%(pre,string)
  print string.replace('\n','\n'+' '*(len(pre)-18))
  

def checkGUIMode(batchmode):
  """Check if GUI is possible."""
  if batchmode:
    return False
  if 'DISPLAY' not in os.environ:
    print "Warning! Cannot open plot (no 'DISPLAY' environmental variable found). Running in batch mode..."
    return False
  return True