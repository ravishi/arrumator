arrumator.py
============

It's beautifulsoup4 with four spaces as tabs and empty tags kept in one line.
Oh, and an optional `--tidy` parameter.

It's not on pypi, so ::

    $ pip install git+git://github.com/ravishi/arrumator.git
    $ arrumator.py dirtydocument.html > cleandocument.html

If you're dealing with really dirty HTML you may want to try tidy. ::

    $ sudo apt-get install tidy
    $ arrumator.py --tidy reallydirtydocument.html


Development
===========

Yes, we use unecessary temporary files. Yes, we don't support all the arguments
that we could. And yes, solved my problems so far.
