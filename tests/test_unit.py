from nose.tools import raises

from basetestcase import BaseTestCase
from robotpageobjects import exceptions
from robotpageobjects.page import Page


class ResolveUrlTestCase(BaseTestCase):

    def setUp(self):
        super(ResolveUrlTestCase, self).setUp()

        class PO(Page):
            pass

        self.PO = PO

    ### Exceptions ###
    @raises(exceptions.NoBaseUrlException)
    def test_no_baseurl_set_no_uri_attr_set_should_raise_NoBaseUrlException(self):
        self.PO()._resolve_url()

    @raises(exceptions.NoBaseUrlException)
    def test_no_baseurl_set_no_uri_attr_set_uri_vars_set_should_raise_NoBaseUrlExeption(self):
        self.PO()._resolve_url("bar")

    @raises(exceptions.NoBaseUrlException)
    def test_no_baseurl_set_uri_attr_set_uri_vars_set_should_raise_NoBaseUrlExeption(self):
        self.PO.uri = "/foo"
        self.PO()._resolve_url("bar")

    @raises(exceptions.NoUriAttributeException)
    def test_baseurl_set_no_uri_attr_set_should_raise_NoUriAttributeException(self):
        self.set_baseurl_env()
        self.PO()._resolve_url()

    @raises(exceptions.AbsoluteUriAttributeException)
    def test_baseurl_set_abs_uri_attr_should_raise_AbsoulteUrlAttributeException(self):
        self.set_baseurl_env()
        self.PO.uri = "http://www.example.com"
        self.PO()._resolve_url()

    @raises(exceptions.AbsoluteUriTemplateException)
    def test_baseurl_set_abs_uri_template_should_raise_AbsoluteUriTemplateException(self):
        self.set_baseurl_env()
        self.PO.uri_template = "http://www.ncbi.nlm.nih.gov/pubmed/{pid}"
        print self.PO()._resolve_url({"pid": "123"})

    @raises(exceptions.InvalidUriTemplateVariable)
    def test_baseurl_set_bad_vars_passed_to_uri_template(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        self.PO.uri_template = "/pubmed/{pid}"
        self.PO()._resolve_url({"foo": "bar"})

    ### Normative Cases ###
    def test_rel_uri_attr_set(self):
        self.set_baseurl_env()
        self.PO.uri = "/foo"
        po_inst = self.PO()
        url = po_inst._resolve_url()
        self.assertEquals(url, po_inst.baseurl + po_inst.uri)
        self.assertRegexpMatches(url, "file:///.+/foo$")

    def test_uri_vars_set(self):
        self.set_baseurl_env(base_file=False, arbitrary_base="http://www.ncbi.nlm.nih.gov")
        self.PO.uri_template = "/pubmed/{pid}"
        url = self.PO()._resolve_url({"pid": "123"})
        self.assertEquals("http://www.ncbi.nlm.nih.gov/pubmed/123", url)
