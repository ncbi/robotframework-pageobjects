from pageobjects.base.PageObjectLibrary import PageObjectLibrary, robot_alias
import time

class AnnotationReportPageLibrary(PageObjectLibrary):
    homepage = "/genome/annotation_euk"

    def open(self, species, build):
        url = self.homepage + "/" + species + "/" + build + "/"
        self.species = species
        self.build = build
        return super(AnnotationReportPageLibrary, self).open(url)

    def wait(self, time):
        time.sleep(int(time))
    
