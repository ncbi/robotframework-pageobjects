from nose.tools import raises

from basetestcase import BaseTestCase
from pageobjects.base import exceptions
from pageobjects.base.PageObjectLibrary import PageObjectLibrary


class ResolveUrlTestCase(BaseTestCase):

    def setUp(self):
        super(ResolveUrlTestCase, self).setUp()

        class PO(PageObjectLibrary):
            pass

        self.PO = PO


    ### Exceptions ###
    @raises(exceptions.NoBaseUrlException)
    def test_no_baseurl_set_no_url_attr_set_should_raise_NoBaseUrlException(self):
        self.PO().resolve_url(uri_vars=None)

    @raises(exceptions.NoBaseUrlException)
    def test_no_baseurl_set_no_url_attr_set_uri_vars_set_should_raise_NoBaseUrlExeption(self):
        self.PO().resolve_url("bar")

    @raises(exceptions.NoBaseUrlException)
    def test_no_baseurl_set_url_attr_set_uri_vars_set_should_raise_NoBaseUrlExeption(self):
        self.PO.url = "/foo"
        self.PO().resolve_url("bar")

    @raises(exceptions.NoUrlAttributeException)
    def test_baseurl_set_no_url_attr_set_should_raise_NoUrlAttributeException(self):
        self.set_baseurl_env()
        self.PO().resolve_url(uri_vars=None)

    @raises(exceptions.AbsoluteUrlAttributeException)
    def test_baseurl_set_abs_url_attr_should_raise_AbsoulteUrlAttributeException(self):
        self.set_baseurl_env()
        self.PO.url = "http://www.example.com"
        self.PO().resolve_url(uri_vars=None)

    @raises(exceptions.AbsoluteUriTemplateException)
    def test_baseurl_set_abs_uri_template_should_raise_AbsoluteUriTemplateException(self):
        self.set_baseurl_env()
        self.PO.uri_template = "http://www.ncbi.nlm.nih.gov/pubmed/{pid}"
        print self.PO().resolve_url({"pid": "123"})

    ### Normative Cases ###
    def test_rel_url_attr_set(self):
        self.set_baseurl_env()
        self.PO.url = "/foo"
        po_inst = self.PO()
        url = po_inst.resolve_url(uri_vars=None)
        self.assertEquals(url, po_inst.baseurl + po_inst.url)
        self.assertRegexpMatches(url, "file:///.+/foo$")

    def test_uri_vars_set(self):
        self.set_baseurl_env()




    """
    def test_robot_no_uri_vars_no_url_should_raise_exception(self):
        run = self.run_scenario("test_no_url.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=1, search_output='must have a "url" attribute')

    #def test_abs






    def test_unittest_no_uri_vars_rel_url_attr_set_baseurl_set_should_pass(self):
        os.environ["PO_BASEURL"] = self.base_file_url
        run = self.run_scenario("test_relative_url.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_robot_no_uri_vars_rel_url_attr_set_baseurl_set_should_pass(self):
        run = self.run_scenario("test_relative_url.robot",
                                variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_absolute_url_attr_set_should_raise_exception(self):
        run = self.run_scenario("test_abs_url_set.py")
        self.assert_run(run, expected_returncode=1, search_output="foo")


    # Need to start here tomorrow.
    def test_unittest_abs_url_passed_no_baseurl_set_homepage_set_should_pass(self):
        run = self.run_scenario("test_abs_url_passed.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_robot_abs_url_passed_no_baseurl_set_homepage_set_should_pass(self):
        # Pass the absolute file URL to the site under test to the robot test.
        run = self.run_scenario("test_abs_url_passed.robot", variable="ABS_URL:%s" % self.site_under_test_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_unittest_rel_url_passed_baseurl_set_no_homepage_set_should_pass(self):
        os.environ["PO_BASEURL"] = self.base_file_url
        run = self.run_scenario("test_rel_url_passed.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")

    def test_robot_rel_url_passed_baseurl_set_no_homepage_set_should_pass(self):
        run = self.run_scenario("test_rel_url_passed.robot", variable="baseurl:%s" % self.base_file_url)
        self.assert_run(run, expected_returncode=0, search_output="PASS")

    def test_unittest_template_passed_baseurl_set(self):
        os.environ["PO_BASEURL"] = self.base_file_url
        run = self.run_scenario("test_template_passed.py")
        self.assert_run(run, expected_returncode=0, search_output="OK")
    """
