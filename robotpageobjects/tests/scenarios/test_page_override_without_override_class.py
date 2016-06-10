import os
from robotpageobjects.tests.scenarios import po
class TwoComponentsSubPageWithoutOverride(po.result_component.TwoComponentsPage):
    components = {po.ParaComponent: "css=p:last-child"}
