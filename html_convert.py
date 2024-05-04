import html.parser

class LocalWikiHTMLToWikimediaParser(html.parser.HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = []
        self.in_anchor = False
        self.href = None
        self.link_text = None
        self.in_span_tag = False
        self.image_attributes = {}
        self.image_caption = ''
        self.span_attributes = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'a':
            self.in_anchor = True
            for name, value in attrs:
                if name == 'href':
                    self.href = value
        elif tag == 'span' and 'class' in attrs_dict and attrs_dict['class'] == 'image_frame image_frame_border image_right':
            self.in_span_tag = True
            self.alignment = 'right|'
            #print(attrs_dict)
        elif tag == 'span' and 'class' in attrs_dict and attrs_dict['class'] == 'image_frame image_frame_border image_left':
            self.in_span_tag = True
            self.alignment = 'left|'
            #print(attrs_dict)
        elif tag == 'span' and 'class' in attrs_dict and attrs_dict['class'] == 'image_frame image_frame_border':
            self.in_span_tag = True
            self.alignment = ''
        elif tag == 'img' and self.in_span_tag:
            self.image_src = attrs_dict.get('src')
            #print(attrs_dict)
            self.width = attrs_dict['style'][7:12]
        elif tag == 'span' and 'class' in attrs_dict and attrs_dict['class'] == 'image_caption' and self.in_span_tag:
            #print("handle data function output:")
            #self.image_caption = self.data
            self.result.append(f"[[File:{self.image_src}|{self.alignment}thumb|{self.width}")
        elif tag == 'span' and self.in_span_tag:
            self.in_span_tag = False
        elif tag == 'p':
            self.result.append('\n\n')
        elif tag == 'strong':
            self.result.append("'''")
        elif tag == 'em':
            self.result.append("''")
        elif tag == 'ul':
            pass
        elif tag == 'li':
            self.result.append('\n* ')
        elif tag == 'h2':
            self.result.append('\n\n## ') 
        elif tag == 'hr':
            self.result.append('\n-----')
        elif tag == 'ol':
            self.result.append('# ')
        elif tag == 'table':
            self.result.append('{|\n')
        elif tag == 'tr':
            self.result.append('|-/n')
        elif tag == 'td':
            self.result.append('|')        
        else:
            Warning(tag)
            self.result.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag == 'a':
            self.in_anchor = False
            # Convert to Wikimedia syntax
            wikimedia_link = f"[[{self.href}|{self.link_text}]]"
            self.result.append(wikimedia_link)
            self.href = None
            self.link_text = None
        elif tag == 'span' and self.in_span_tag:
            self.result.append(f"]]")
            self.in_span_tag = False
        elif tag == 'span':
            pass
        elif tag == 'strong':
            self.result.append("'''")
        elif tag == 'em':
            self.result.append("''")
        elif tag == 'table':
            self.result.append('\n|}')
        elif tag == 'tr':
            self.result.append('/n')
        elif tag == 'td':
            self.result.append('|')
        elif tag == 'li' or tag == 'ul' or tag == 'h2' or tag == 'p' or tag == 'hr' or tag == 'ol':
            pass
        else:
            self.result.append(f"</{tag}>")

    def handle_data(self, data):
        if self.in_anchor:
            self.link_text = data
        elif self.in_span_tag and self.image_caption is not None:
            self.result.append(f"|{data}")
            return 
        else:
            self.result.append(data)

    def get_wikimedia_syntax(self):
        return ''.join(self.result)
    

# Function to parse a string and run the parser on each anchor tag
def parse_and_convert(html_content):
    html_content = html_content.replace('\n', '')
    html_content = html_content.replace('\t', '')
    html_content = html_content.replace('_files/', '')
    parser = LocalWikiHTMLToWikimediaParser()
    parser.feed(html_content)
    return parser.get_wikimedia_syntax()