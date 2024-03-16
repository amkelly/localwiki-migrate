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
            self.alignment = 'right'
            #print(attrs_dict)
        elif tag == 'span' and 'class' in attrs_dict and attrs_dict['class'] == 'image_frame image_frame_border image_left':
            self.in_span_tag = True
            self.alignment = 'left'
            #print(attrs_dict)
        elif tag == 'img' and self.in_span_tag:
            self.image_src = attrs_dict.get('src')
            #print(attrs_dict)
            self.width = attrs_dict['style'][7:12]
        elif tag == 'span' and 'class' in attrs_dict and attrs_dict['class'] == 'image_caption' and self.in_span_tag:
            #print("handle data function output:")
            #self.image_caption = self.data
            self.result.append(f"[[File:{self.image_src}|{self.alignment}|frame|{self.width}")
        elif tag == 'span' and self.in_span_tag:
            self.in_span_tag = False
        elif tag == 'p':
            self.result.append('\n\n')
        elif tag == 'strong':
            self.result.append("'''")
        elif tag == 'ul':
            pass
        elif tag == 'li':
            self.result.append('\n* ')
        elif tag == 'h2':
            self.result.append('\n\n## ') 
        elif tag == 'hr':
            self.result.append('-----')
        elif tag == 'ol':
            self.result.append('# ')
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
            self.in_span_tag = False
        elif tag == 'span':
            pass
        elif tag == 'strong':
            self.result.append("'''")
        elif tag == 'li' or tag == 'ul' or tag == 'h2' or tag == 'p' or tag == 'hr' or tag == 'ol':
            pass
        else:
            self.result.append(f"</{tag}>")

    def handle_data(self, data):
        if self.in_anchor:
            self.link_text = data
        elif self.in_span_tag and self.image_caption is not None:
            self.result.append(f"|{data}]]")
            return 
        else:
            self.result.append(data)

    def get_wikimedia_syntax(self):
        return ''.join(self.result)
    

# Function to parse a string and run the parser on each anchor tag
def parse_and_convert(html_string):
    parser = LocalWikiHTMLToWikimediaParser()
    parser.feed(html_string)
    #mediawiki_image = parser.get_mediawiki_image()
    return parser.get_wikimedia_syntax()

# Example usage
html_string = """<p>\n\t<span class=\"image_frame image_frame_border image_right\"><img src=\"_files/Post%20Office%20Pharmacy.jpg\" style=\"width: 400px; height: 298px;\"><span style=\"width: 400px;\" class=\"image_caption\">The Post Office Pharmacy </span></span></p>\n<p>\n\tAs a health resort for tuberculosis, Saranac Lake required many pharmacies to supply necessities for the thousands of patients who lived in the village and in neighboring institutional sanatoria.</p>\n<p>\n\tThe <a href=\"Post%20Office%20Pharmacy\">Post Office Pharmacy</a>, the last independent pharmacy in Franklin County, got its name when it occupied a storefront on the other side of Main Street in (or near) the United States Post Office, in its previous location.</p>\n<p>\n\tOther pharmacies serving the T. B. \"industry\" included</p>\n<ul>\n\t<li>\n\t\t<a href=\"Adirondack%20Pharmacy\">Adirondack Pharmacy</a>, <a href=\"Broadway\">Broadway</a></li>\n\t<li>\n\t\t<a href=\"Baldwin%27s%20Drug%20Store\">Baldwin's Drug Store</a>, <a href=\"Bloomingdale\">Bloomingdale</a></li>\n\t<li>\n\t\t<a href=\"Bradford%20B.%20Flint\">Bradford B. Flint</a>, 36 Broadway</li>\n\t<li>\n\t\t<a href=\"F.M.%20Bull\">F.M. Bull</a>'s Drug Store, 18 Main Street</li>\n\t<li>\n\t\t<a href=\"Dwyer%27s%20Rexall%20Pharmacy\">Dwyer's Rexall Pharmacy</a>, 36 Broadway</li>\n\t<li>\n\t\t<a href=\"Hoffman%27s%20Pharmacy\">Hoffman Pharmacy</a>, on <a href=\"Church%20Street%20Extension\">Church Street Extension</a></li>\n\t<li>\n\t\t<a href=\"Hogan%27s%20Pharmacy\">Hogan's Pharmacy</a></li>\n\t<li>\n\t\t<a href=\"Kendall%27s%20Pharmacy\">Kendall's Pharmacy</a>, 18 <a href=\"Main%20Street\">Main Street</a></li>\n\t<li>\n\t\t<a href=\"Miller%27s%20Drugs\">Miller's Drugs</a>, at 4 <a href=\"Broadway\">Broadway</a></li>\n\t<li>\n\t\t<a href=\"Meyer%27s%20Drugs\">Meyer's Drugs</a>, <a href=\"69%20Main%20Street\">69 Main Street</a></li>\n\t<li>\n\t\t<a href=\"Post%20Office%20Pharmacy\">Post Office Pharmacy</a>, 52 Main Street</li>\n\t<li>\n\t\t<a href=\"Charles%20Reiss%20Pharmacy\">Charles Reiss Pharmacy</a>, 3 Bloomingdale Avenue</li>\n\t<li>\n\t\t<a href=\"Terminal%20Pharmacy\">Terminal Pharmacy</a>, at <a href=\"Bloomingdale%20Road\">Bloomingdale Road</a></li>\n</ul>\n<h2>\n\tComments</h2>\n"""
html_string = html_string.replace('\n', '')
html_string = html_string.replace('\t', '')

wikimedia_syntax = parse_and_convert(html_string)
print(wikimedia_syntax)