from pageobjects.base.PageObjectLibrary import PageObjectLibrary, robot_alias
import time

class AnnotationReportPageLibrary(PageObjectLibrary):
    homepage = "http://www.ncbi.nlm.nih.gov/genome/annotation_euk"

    @robot_alias("open__name__")
    def open(self, species, build):
        url = self.homepage + "/" + species + "/" + build + "/"
        self.species = species
        self.build = build
        return super(AnnotationReportPageLibrary, self).open(url)

#    def check_header(self):
#        self.se.element_should_contain("css=#BuildInfo", species)

    def wait(self, time):
        time.sleep(int(time))
    
