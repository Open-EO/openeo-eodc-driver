''' Band Extractor ** Just needed as long band information not provided by the EODC CSW server ** '''

from nameko.extensions import DependencyProvider
from ..models import Band


class BandsExtractor:
    """BandsExtractor maps the product_id to the band information.
    ** Just needed as long band information not provided by the EODC CSW server **
    """

    def __init__(self):
        self.bands = {
            "default": [],
            "s2a_prd_msil1c": [
                Band("1", 443.9, 60, 0.0001, 0, "int16", "1"),
                Band("2", 496.6, 10, 0.0001, 0, "int16",
                    "1", name="blue"),
                Band("3", 560, 10, 0.0001, 0, "int16",
                    "1", name="green"),
                Band("4", 664.5, 10, 0.0001, 0, "int16",
                    "1", name="red"),
                Band("5", 703.9, 20, 0.0001, 0, "int16", "1"),
                Band("6", 740.2, 20, 0.0001, 0, "int16", "1"),
                Band("7", 782.5, 20, 0.0001, 0, "int16", "1"),
                Band("8", 835.1, 10, 0.0001, 0, "int16",
                    "1", name="nir"),
                Band("8a", 864.8, 20, 0.0001, 0, "int16", "1"),
                Band("9", 945, 60, 0.0001, 0, "int16", "1"),
                Band("10", 1373.5, 60, 0.0001, 0, "int16", "1"),
                Band("11",  1613.7, 20, 0.0001, 0, "int16", "1"),
                Band("12", 2202.4, 20, 0.0001, 0, "int16", "1")
            ]
        }

    def get_bands(self, product_id: str) -> list:
        """Returns the band infoamtion of a specific product.

        Arguments:
            product_id {str} -- The identifier of the product

        Returns:
            list -- A list containing all bands of the product
        """

        return self.bands.get(product_id, self.bands["default"])
