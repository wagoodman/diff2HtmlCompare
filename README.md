# diff2HtmlCompare

A python script that takes two files and compares the differences between them (side-by-side) in an HTML format. Supports both python2 and python3.

### Installation
```
pip install -r requirements.txt
```

### Usage
```
diff2HtmlCompare.py [-h] [-s] [-v] file1 file2

positional arguments:
  file1       file to compare ("before" file).
  file2       file to compare ("after" file).

optional arguments:
  -h, --help  show this help message and exit
  -s, --show  show html in a browser.
  -v          show verbose output.
```
### Example Output

![ScreenShot](/screenshots/latest.png)
