from html.parser import HTMLParser

class MediaWikiConverter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.mediawiki_content = ""
        self.in_image_tag = False
        self.in_span_tag = False
        self.image_attributes = {}
        self.span_attributes = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            # Find the href attribute
            href = None
            for attr in attrs:
                if attr[0] == 'href':
                    href = attr[1]
                    break
            if href:
                # Convert to MediaWiki link syntax
                self.mediawiki_content += f"[[{href}|"
        elif tag == 'p':
            self.handle_data
        elif tag == 'span':
            if self.in_span_tag == False:
                self.handle_data(self)
            else:
                print("span tag is in a previous span tag")
        elif tag == 'img':
            self.in_image_tag = True
            self.image_attributes = dict(attrs)
        elif tag == 'strong':
            self.mediawiki_content += f"'''"
        else:
            # Handle other tags as needed
            #self.mediawiki_content += 
            #print(attrs)
            pass

    def handle_endtag(self, tag):
        if tag == 'a':
            self.mediawiki_content += "]]"
        if tag == 'p':
            self.mediawiki_content += "/n"
        elif tag == 'img':
            self.in_span_tag = True

            # Extract alignment from span class
            alignment = self.span_attributes.get('class', '').split()[-1]
            # Extract caption from span content
            caption = self.span_attributes.get('content', alt)
            self.mediawiki_content += f"|{width}px|{alignment}|{caption}]]"
        elif tag == 'span':
            self.in_span_tag = False 
        elif tag == 'strong':
            self.mediawiki_content += f"'''"
        else:
            # Handle other tags as needed
            pass

    def handle_data(self, data):
        #function takes as its input a parent span tag with following formatting:
        '''
        <p>this is a paragraph<\p>
        <span class=\"image_frame image_frame_border image_right\">
        <img src=\"_files/Post%20Office%20Pharmacy.jpg\" style=\"width: 400px; height: 298px;\">
        <span style=\"width: 400px;\" class=\"image_caption\">The Post Office Pharmacy </span>
        </span>
        '''
        if self.in_image_tag:
            # Handle icontents of img tag
            self.image_attributes.get('src', )
            pass
        elif self.in_span_tag:
            # Extract caption from span content
            caption = self.span_attributes['content']
        else:
            pass
            self.mediawiki_content += str(data)

    def convert(self, html_content):
        self.feed(html_content)
        return self.mediawiki_content

# Example usage
html_content = """
<p>This is a <a href="https://example.com">link</a> to an external site.</p>
This is <strong>bold</strong> text.
<p>This is an <a href="/internal/link">internal link</a>.</p>
<span class="image_frame image_frame_border image_right">
    <img src="_files/Post%20Office%20Pharmacy.jpg" style="width: 400px; height: 298px;">
    <span style="width: 400px;" class="image_caption">The Post Office Pharmacy </span>
</span>
"""

converter = MediaWikiConverter()
mediawiki_content = converter.convert(html_content)
print(mediawiki_content)
