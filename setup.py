from distutils.core import setup

version = '0.0.1'

setup(name="arrumator",
      version=version,
      scripts=['arrumator.py'],
      description="HTML/XHML prettifier.",
      author="Dirley Rodrigues",
      author_email = "dirleyrls@gmail.com",
      long_description="""HTML/XML prettifier based on BeautifulSoup and Tidy (the latter being optional).""",
      classifiers=[#"Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: Python Software Foundation License",
                   "Programming Language :: Python",
                   "Topic :: Text Processing :: Markup :: HTML",
                   ],
      install_requires=['beautifulsoup4 == 4.00b10'],
      url="http://github.com/ravishi/arrumator",
      license="WTFPL",
      download_url="http://github.com/ravishi/arrumator/downloads"
      )
