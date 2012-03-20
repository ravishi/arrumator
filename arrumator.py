#!/usr/bin/env python
import subprocess
from itertools import chain

from bs4.element import DEFAULT_OUTPUT_ENCODING
from bs4.element import EntitySubstitution
from bs4.element import NavigableString
from bs4.element import Tag
from bs4 import BeautifulSoup


PRESERVE_CONTENTS = ['script']


def prettify(self,
        eventual_encoding=DEFAULT_OUTPUT_ENCODING,
        tabsize=1):
    """
    A custom prettify function. It work mostly like BS's version, but

      - it has configurable tab size: `prettify(tabsize=4)`
      - it keep the opening and the closing tags of a empty tag in
        the same line. ex.::

            <script></script> instead of <script>\\n[indent]</script>
    """
    if self.is_xml:
        # Print the XML declaration
        encoding_part = ''
        if eventual_encoding != None:
            encoding_part = ' encoding="%s"' % eventual_encoding
        prefix = u'<?xml version="1.0"%s?>\n' % encoding_part
    else:
        prefix = u''
    return prefix + decode(self, 0, eventual_encoding, tabsize=tabsize)


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

    if self.name in PRESERVE_CONTENTS:
        contents = self.text
    else:
        contents = decode_contents(self, indent_contents,
                eventual_encoding, substitute_html_entities, tabsize)

    isempty = not contents.strip('\n').strip()

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
        if pretty_print and (not isempty or not closeTag):
            s.append("\n")
        if not isempty:
            s.append(contents)
        if pretty_print and not isempty and contents[-1] != "\n":
            s.append("\n")
        if pretty_print and not isempty and closeTag:
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


def _tidy_option_value(value):
    if isinstance(value, bool):
        return str(value).lower()
    else:
        return str(value)


def tidy(html, extra_options=None):
    options = {
        'bare': True,
        'doctype': 'strict',
        'drop-empty-paras': True,
        'hide-endtags': True,
        'logical-emphasis': True,
        'output-xhtml': True,
        'indent': True,
        'indent-spaces': 4,
        'sort-attributes': 'alpha',
        'tab-size': 4,
        'wrap': 0,
        #'char-encoding': 'utf-8',
        'newline': 'LF',
        'break-before-br': True,
    }

    if extra_options is not None:
        options.update(extra_options)

    tidyopts = (('--%s' % k, _tidy_option_value(v)) for k, v in options.iteritems())
    args = ('tidy', '-utf8') + tuple(chain(*tidyopts))

    proc = subprocess.Popen(args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    out, err = proc.communicate(html.encode('utf-8'))
    return out.decode('utf-8')


def arruma(html, options):
    return prettify(BeautifulSoup(html, options.parser), tabsize=options.tabsize)


def _main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--tidy', action='store_true', default=False,
            help=('Parse the document with htmltidy. This option requires htmltidy installed.'))
    parser.add_argument('--tabsize', type=int, default=4)

    # FIXME wouldn't it be better to set a default parser instead of
    # letting bs4 decide that? I think that that would be more clear
    # for people who are not familiar with bs4
    parser.add_argument('--parser', default=None,
            choices=('html.parser', 'lxml', 'lxml.xml', 'html5lib'))

    parser.add_argument('file', nargs='?')

    args = parser.parse_args()

    # fix the parser: bs4 expects `['lxml', 'xml']` but `lxml.xml`
    if args.parser == 'lxml.xml':
        args.parser = args.parser.split('.')

    if args.file:
        try:
            with open(args.file, 'r') as fp:
                html = fp.read()
        except IOError:
            print >> sys.stderr, ("Failed to read content from `%s'" % args.file)
            return 1
    else:
        html = sys.stdin.read()

    html = html.decode('utf-8')

    if args.tidy:
        try:
            html = tidy(html)
        except OSError:
            print >> sys.stderr, ("Failed to run tidy. Please make sure tidy is installed"
                    "in your system.")
            return 1

    print arruma(html, args).encode('utf-8')

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(_main())
