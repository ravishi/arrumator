#!/usr/bin/env python
import tempfile
import subprocess

from bs4.element import DEFAULT_OUTPUT_ENCODING
from bs4.element import EntitySubstitution
from bs4.element import NavigableString
from bs4.element import Tag
from bs4 import BeautifulSoup


def prettify(self, tabsize=4):
    """
    A custom prettify function. It work mostly like BS's version, but

      - it has configurable tab size: `prettify(tabsize=4)`
      - it keep the opening and the closing tags of a empty tag in
        the same line. ex.::

            <script></script> instead of <script>\\n[indent]</script>
    """
    return decode(self, True, tabsize=tabsize)


def decode(self, indent_level=None,
            eventual_encoding=DEFAULT_OUTPUT_ENCODING,
            substitute_html_entities=False,
            tabsize=1):
    """Returns a Unicode representation of this tag and its contents.

    :param eventual_encoding: The tag is destined to be
        encoded into this encoding. This method is _not_
        responsible for performing that encoding. This information
        is passed in so that it can be substituted in if the
        document contains a <META> tag that mentions the document's
        encoding.
    """
    attrs = []
    if self.attrs:
        for key, val in sorted(self.attrs.items()):
            if val is None:
                decoded = key
            else:
                if isinstance(val, list) or isinstance(val, tuple):
                    val = ' '.join(val)
                elif not isinstance(val, basestring):
                    val = str(val)
                if (self.contains_substitutions
                    and eventual_encoding is not None
                    and '%SOUP-ENCODING%' in val):
                    val = self.substitute_encoding(val, eventual_encoding)

                decoded = (str(key) + '='
                            + EntitySubstitution.substitute_xml(val, True))
            attrs.append(decoded)
    close = ''
    closeTag = ''
    if self.is_empty_element:
        close = '/'
    else:
        closeTag = '</%s>' % self.name

    prefix = ''
    if self.prefix:
        prefix = self.prefix + ":"

    pretty_print = (indent_level is not None)
    if pretty_print:
        space = (' ' * tabsize * (indent_level - 1))
        indent_contents = indent_level + 1
    else:
        space = ''
        indent_contents = None

    contents = decode_contents(self, indent_contents,
            eventual_encoding, substitute_html_entities, tabsize)

    if self.hidden:
        # This is the 'document root' object.
        s = contents
    else:
        s = []
        attribute_string = ''
        if attrs:
            attribute_string = ' ' + ' '.join(attrs)
        if pretty_print:
            s.append(space)
        s.append('<%s%s%s%s>' % (
                prefix, self.name, attribute_string, close))
        if pretty_print and (contents or not closeTag):
            s.append("\n")
        s.append(contents)
        if pretty_print and contents and contents[-1] != "\n":
            s.append("\n")
        if pretty_print and contents and closeTag:
            s.append(space)
        s.append(closeTag)
        if pretty_print and closeTag and self.next_sibling:
            s.append("\n")
        s = ''.join(s)
    return s


def decode_contents(self, indent_level=None,
                    eventual_encoding=DEFAULT_OUTPUT_ENCODING,
                    substitute_html_entities=False,
                    tabsize=1):
    """Renders the contents of this tag as a Unicode string.

    :param eventual_encoding: The tag is destined to be
        encoded into this encoding. This method is _not_
        responsible for performing that encoding. This information
        is passed in so that it can be substituted in if the
        document contains a <META> tag that mentions the document's
        encoding.
    """
    pretty_print = (indent_level is not None)
    s = []
    for c in self:
        text = None
        if isinstance(c, NavigableString):
            text = c.output_ready(substitute_html_entities)
        elif isinstance(c, Tag):
            s.append(decode(c, indent_level, eventual_encoding,
                                substitute_html_entities, tabsize=tabsize))
        if text and indent_level:
            text = text.strip()
        if text:
            if pretty_print:
                s.append(" " * tabsize * (indent_level - 1))
            s.append(text)
            if pretty_print:
                s.append("\n")
    return ''.join(s)


def mktidyconfig():
    config = """
bare: yes
doctype: auto
drop-empty-paras: true
hide-endtags: true
logical-emphasis: true
output-xhtml: true
indent: true
indent-spaces: 4
sort-attributes: alpha
tab-size: 4
wrap: 0
char-encoding: utf8
input-encoding: utf-8
newline: LF
output-encoding: utf-8
break-before-br: true
"""
    fp = tempfile.NamedTemporaryFile()
    fp.write(config)
    fp.flush()
    return fp


def tidyhtml(html):
    with mktidyconfig() as config:
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(html.encode('utf-8'))
            fp.flush()
            args = ['tidy', '-config', config.name, fp.name]
            proc = subprocess.Popen(args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            out, err = proc.communicate()
            return out


def _main():
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--tidy', action='store_true', default=False)
    parser.add_argument('file', nargs='?')

    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, 'r') as fp:
                html = fp.read()
        except IOError:
            print >> sys.stderr, ("Failed to read content from `%s'" % args.file)
    else:
        html = sys.stdin.read()

    html = html.decode('utf-8')

    if args.tidy:
        try:
            html = tidyhtml(html).decode('utf-8')
        except OSError:
            print >> sys.stderr, ("Failed to run tidy. Please make sure tidy is installed"
                    "in your system.")
            sys.exit(1)

    print prettify(BeautifulSoup(html), tabsize=4).encode('utf-8')

if __name__ == '__main__':
    _main()
