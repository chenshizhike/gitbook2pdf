import re
from urllib.parse import urljoin

class HtmlGenerator():
    def __init__(self, base_url):
        self.html_start = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">      
"""

        self.title_ele = ""
        self.body_begin = """
</head>
<body>
        """
        self.body = ""
        self.html_end = """
</body>
</html>
"""
        self.base_url = base_url
    
    def add_body(self, body):
        self.body = body

    def srcrepl(self, match):
        "Return the file contents with paths replaced"
        absolutePath = self.base_url
        pathStr = match.group(3)
        if pathStr.startswith(".."):
            pathStr = pathStr[3:]
        return "<" + match.group(1) + match.group(2) + "=" + "\"" + urljoin(absolutePath, pathStr) + "\"" + match.group(4)  + ">"

    def relative_to_absolute_path(self, origin_text):
        p = re.compile(r"<(.*?)(src|href)=\"(?!http)(.*?)\"(.*?)>")
        updated_text = p.sub(self.srcrepl, origin_text)
        return updated_text

    def output(self):
        full_html = self.html_start + self.title_ele + self.body_begin + self.body + self.html_end
        return self.relative_to_absolute_path(full_html)