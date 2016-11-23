# MIT License
# 
# Copyright (c) 2016 Alex Goodman
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import sys
import difflib
import argparse
import StringIO
import pygments
from pygments.lexers import guess_lexer_for_filename
from pygments.lexer import RegexLexer
from pygments.formatters import HtmlFormatter
from pygments.token import *


class DefaultLexer(RegexLexer):
   """
   Simply lex each line as a token.
   """

   name = 'Default'
   aliases = ['default']
   filenames = ['*']

   tokens = {
      'root': [
         (r'.*\n', Text),
      ]
   }


class DiffHtmlFormatter(HtmlFormatter):
   """
   Formats a single source file with pygments and adds diff highlights based on the 
   diff details given.
   """
   isLeft = False
   diffs = None

   def __init__(self, isLeft, diffs, *args, **kwargs):
      self.isLeft = isLeft
      self.diffs = diffs
      super(DiffHtmlFormatter, self).__init__(*args, **kwargs)

   def wrap(self, source, outfile):
      return self._wrap_code(source)

   def getDiffLineNos(self):
      retlinenos = []
      for idx, ((left_no, left_line),(right_no, right_line),change) in enumerate(self.diffs):  
         no = None
         if self.isLeft:
            if change:
               if isinstance(left_no, int) and isinstance(right_no, int):
                  no = '<span class="lineno_q lineno_leftchange">' + str(left_no) + "</span>"
               elif isinstance(left_no, int) and not isinstance(right_no, int):
                  no = '<span class="lineno_q lineno_leftdel">' + str(left_no) + "</span>"
               elif not isinstance(left_no, int) and isinstance(right_no, int):
                  no = '<span class="lineno_q lineno_leftadd">  </span>'
            else:
               no = '<span class="lineno_q">' + str(left_no) + "</span>"
         else:
            if change:
               if isinstance(left_no, int) and isinstance(right_no, int):
                  no = '<span class="lineno_q lineno_rightchange">' + str(right_no) + "</span>"
               elif isinstance(left_no, int) and not isinstance(right_no, int):
                  no = '<span class="lineno_q lineno_rightdel">  </span>'
               elif not isinstance(left_no, int) and isinstance(right_no, int):
                  no = '<span class="lineno_q lineno_rightadd">' + str(right_no) + "</span>"
            else:
               no = '<span class="lineno_q">' + str(right_no) + "</span>"

         retlinenos.append(no)

      return retlinenos

   def _wrap_code(self, source):

      source = list(source)
      yield 0, '<pre>'

      for idx, ((left_no, left_line),(right_no, right_line),change) in enumerate(self.diffs):
         #print idx, ((left_no, left_line),(right_no, right_line),change)
         try:
            if self.isLeft:
               if change:
                  if isinstance(left_no, int) and isinstance(right_no, int) and left_no <= len(source):
                     i,t = source[left_no-1]
                     t = '<span class="left_diff_change">' + t + "</span>"
                  elif isinstance(left_no, int) and not isinstance(right_no, int) and left_no <= len(source):
                     i,t = source[left_no-1]
                     t = '<span class="left_diff_del">' + t + "</span>"
                  elif not isinstance(left_no, int) and isinstance(right_no, int):
                     i,t = 1, left_line
                     t = '<span class="left_diff_add">' + t + "</span>"
                  else:
                     raise
               else:
                  if left_no <= len(source):
                     i,t = source[left_no-1]
                  else:
                     i = 1
                     t = left_line 
            else:
               if change:
                  if isinstance(left_no, int) and isinstance(right_no, int) and right_no <= len(source):
                     i,t = source[right_no-1]
                     t = '<span class="right_diff_change">' + t + "</span>"
                  elif isinstance(left_no, int) and not isinstance(right_no, int):
                     i,t = 1, right_line
                     t = '<span class="right_diff_del">' + t + "</span>"
                  elif not isinstance(left_no, int) and isinstance(right_no, int) and right_no <= len(source):
                     i,t = source[right_no-1]
                     t = '<span class="right_diff_add">' + t + "</span>"
                  else:
                     raise 
               else:
                  if right_no <= len(source):
                     i,t = source[right_no-1]
                  else:
                     i = 1
                     t = right_line 
            yield i, t
         except:
            #print "WARNING! failed to enumerate diffs fully!"
            pass # this is expected sometimes
      yield 0, '\n</pre>'


   def _wrap_tablelinenos(self, inner):
      dummyoutfile = StringIO.StringIO()
      lncount = 0
      for t, line in inner:
         if t:
            lncount += 1
         dummyoutfile.write(line)

      fl = self.linenostart
      mw = len(str(lncount + fl - 1))
      sp = self.linenospecial
      st = self.linenostep
      la = self.lineanchors
      aln = self.anchorlinenos
      nocls = self.noclasses

      lines = []
      for i in self.getDiffLineNos():
         lines.append('%s' % (i,))

      ls = ''.join(lines)

      # in case you wonder about the seemingly redundant <div> here: since the
      # content in the other cell also is wrapped in a div, some browsers in
      # some configurations seem to mess up the formatting...
      if nocls:
         yield 0, ('<table class="%stable">' % self.cssclass +
                 '<tr><td><div class="linenodiv" '
                 'style="background-color: #f0f0f0; padding-right: 10px">'
                 '<pre style="line-height: 125%">' +
                 ls + '</pre></div></td><td class="code">')
      else:
         yield 0, ('<table class="%stable">' % self.cssclass +
                 '<tr><td class="linenos"><div class="linenodiv"><pre>' +
                 ls + '</pre></div></td><td class="code">')
      yield 0, dummyoutfile.getvalue()
      yield 0, '</td></tr></table>'



class CodeDiff(object):
   """
   Manages a pair of source files and generates a single html diff page comparing
   the contents.
   """
   pygmentsStyleOpt = "vs"
   pygmentsCssFile="./deps/codeformats/%s.css" % pygmentsStyleOpt
   diffCssFile="./deps/diff.css"
   diffJsFile="./deps/diff.js"
   resetCssFile="./deps/reset.css"
   jqueryJsFile="./deps/jquery.min.js"
   

   def __init__(self, fromfile, tofile, fromtxt=None, totxt=None, name=None):
      
      self.filename = name
      self.fromfile = fromfile
      if fromtxt == None:
         try:
            with open(fromfile) as f:
               self.fromlines = f.readlines()
         except Exception as e:
            print "Problem reading file %s" % fromfile
            print e
            sys.exit(1)
      else:
         self.fromlines = [n + "\n" for n in fromtxt.split("\n")]
      self.leftcode = "".join(self.fromlines)
      
      self.tofile = tofile
      if totxt == None:
         try:
            with open(tofile) as f:
               self.tolines = f.readlines()
         except Exception as e:
            print "Problem reading file %s" % tofile
            print e
            sys.exit(1)
      else:
         self.tolines = [n + "\n" for n in totxt.split("\n")]
      self.rightcode = "".join(self.tolines)


   def getDiffDetails(self, fromdesc='', todesc='', context=False, numlines=5, tabSize=8):

      # change tabs to spaces before it gets more difficult after we insert
      # markkup
      def expand_tabs(line):
         # hide real spaces
         line = line.replace(' ','\0')
         # expand tabs into spaces
         line = line.expandtabs(tabSize)
         # replace spaces from expanded tabs back into tab characters
         # (we'll replace them with markup after we do differencing)
         line = line.replace(' ','\t')
         return line.replace('\0',' ').rstrip('\n')

      self.fromlines = [expand_tabs(line) for line in self.fromlines]
      self.tolines = [expand_tabs(line) for line in self.tolines]

      # create diffs iterator which generates side by side from/to data
      if context:
         context_lines = numlines
      else:
         context_lines = None

      diffs = difflib._mdiff(self.fromlines, self.tolines, context_lines, linejunk=None, charjunk=difflib.IS_CHARACTER_JUNK)
      return list(diffs)


   def format(self, verbose=False):
      self.diffs = self.getDiffDetails(self.fromfile, self.tofile)

      if verbose:
         for diff in self.diffs:
            print "%-6s %-80s %-80s" % ( diff[2], diff[0], diff[1] )

      fields = ( (self.leftcode, True, self.fromfile) , (self.rightcode, False, self.tofile) )

      codeContents = []
      for (code, isLeft, filename) in fields:

         inst = DiffHtmlFormatter(isLeft,
                            self.diffs,
                            nobackground=False, 
                            linenos=True, 
                            style=self.pygmentsStyleOpt)

         try:
            self.lexer = guess_lexer_for_filename(self.filename, code)
            
         except pygments.util.ClassNotFound:
            if verbose:
               print "No Lexer Found! Using default..."

            self.lexer = DefaultLexer()
         
         formatted = pygments.highlight(code, self.lexer, inst)
         
         codeContents.append(formatted)

      diffTemplate = open("./templates/diff_template.html",'r').read()

      answers = {
        "html_title":     self.filename,
        "reset_css":      self.resetCssFile,
        "pygments_css":   self.pygmentsCssFile,
        "diff_css":       self.diffCssFile,
        "page_title":     self.filename,
        "original_code":  codeContents[0],
        "modified_code":  codeContents[1],
        "jquery_js":      self.jqueryJsFile,
        "diff_js":        self.diffJsFile,
      }

      self.htmlContents = diffTemplate % answers 
      

   def write(self, path="index.html"):
      fh = open(path,'w')
      fh.write(self.htmlContents.encode('utf8'))
      fh.close()


def main(fromfile, tofile, verbose=False):
   codeDiff = CodeDiff(fromfile, tofile, name=tofile)
   codeDiff.format(verbose)
   codeDiff.write()


if __name__ == "__main__":
   description = """Given two source files this application\
creates an html page which highlights the differences between the two. """

   parser = argparse.ArgumentParser(description=description)
   parser.add_argument('-v', action='store_true', help='show verbose output.')
   parser.add_argument('file1', help='source file to compare ("before" file).')
   parser.add_argument('file2', help='source file to compare ("after" file).')

   args = parser.parse_args()

   main(args.file1, args.file2, args.v)
