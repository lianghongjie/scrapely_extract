import json

from w3lib.util import str_to_unicode

from scrapely.htmlpage import HtmlPage, page_to_dict, url_to_page
from scrapely.template import TemplateMaker, best_match
from scrapely.extraction import InstanceBasedLearningExtractor
from scrapely.version import __version__


class Scraper(object):

    def __init__(self, templates=None):
        """Initialize an empty scraper."""
        # core template --> scraper
        self._templates = templates or []
        self._ex = None

    @classmethod
    def fromfile(cls, file):
        """Initialize a scraper from a file previously stored by tofile()
        method.
        """
        templates = [HtmlPage(**x) for x in json.load(file)['templates']]
        return cls(templates)

    def tofile(self, file):
        """Store the scraper into the given file-like object"""
        tpls = [page_to_dict(x) for x in self._templates]
        print tpls, '##################'
        json.dump({'templates': tpls}, file)

    def add_template(self, template):
        self._templates.append(template)
        self._ex = None

    def train_from_htmlpage(self, htmlpage, data):
        assert data, "Cannot train with empty data"
        # copy htmlpage --> tm
        tm = TemplateMaker(htmlpage)
        for field, values in data.items():
            if (isinstance(values, (bytes, str)) or
                    not hasattr(values, '__iter__')):
                values = [values]
            for value in values:
                value = str_to_unicode(value, htmlpage.encoding)
                tm.annotate(field, best_match(value))
        # test = tm.get_template().subregion(221, 222)
        # print tm.get_template().__class__
        # print 'tttt:', tm.get_template().parsed_body[1]
        # print test
        # print 123, tm.get_template().fragment_data(tm.get_template().parsed_body[1])
        self.add_template(tm.get_template())

    def train(self, url, data, encoding=None):
        page = url_to_page(url, encoding)
        # print url, page
        self.train_from_htmlpage(page, data)

    def scrape(self, url, template_id=None, encoding=None):
        page = url_to_page(url, encoding)
        # print url, page
        return self.scrape_page(page, template_id=template_id)

    def scrape_page(self, page, template_id=None):
        if self._ex is None:
            print 'fffffffffff', self._templates
            self._ex = InstanceBasedLearningExtractor((t, None) for t in
                    self._templates)
        return self._ex.extract(page, pref_template_id=template_id)[0]
