from robotpageobjects import Component, ComponentManager


class GoogleResultComponent(Component):

    # The 'Reference element` is the locator, which is
    # the li element. Selectors are relative to this element.
    selectors = {
        "result title link": "css=div h3 a",
    }

    def utf8(self, txt):
        return txt.encode("utf-8").strip()

    @property
    def text(self):
        return self.reference_webelement.text

    @property
    def title(self):
        ret = self.utf8(self.get_text("result title link"))
        return ret

    def go(self):
        """Goes to the this result"""
        self.click_link("result title link")


class GoogleResultComponentManager(ComponentManager):

    locator = "xpath=//li[@class='g']"

    @property
    def results(self):
        return self.get_instances(GoogleResultComponent)
