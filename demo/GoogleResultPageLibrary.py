from GooglePageLibrary import GooglePageLibrary, robot_alias


class GoogleResultPageLibrary(GooglePageLibrary):
    name = "Google Result Page"

    @robot_alias("on__name__click_result")
    def click_result(self, i):
        els = self.se._element_find("xpath=//h3[@class='r']/a[not(ancestor::table)]", False, False, tag="a")
        try:
            els[int(i)].click()
        except IndexError:
            raise Exception("No result found")