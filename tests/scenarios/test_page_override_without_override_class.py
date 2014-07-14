import os
print os.environ.get("PYTHONPATH", "NOPE")
from result_component import ParaComponent, TwoComponentsPage
class TwoComponentsSubPageWithoutOverride(TwoComponentsPage):
    components = {ParaComponent: "css=p:last-child"}
