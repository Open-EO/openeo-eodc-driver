class Band:
    def __init__(self, band_id, wavelength_nm, res_m, scale, offset, type, unit, name=""):
        self.band_id = band_id
        self.name = name
        self.wavelength_nm = wavelength_nm
        self.res_m = res_m
        self.scale = scale
        self.offset = offset
        self.type = type
        self.unit = unit

    def serialize(self):
        dump = {}
        if self.name:
            dump["name"] = self.name
        dump["band_id"] = self.band_id
        dump["wavelength_nm"] = self.wavelength_nm
        dump["res_m"] = self.res_m
        dump["scale"] = self.scale
        dump["offset"] = self.offset
        dump["type"] = self.type
        dump["unit"] = self.unit
        return dump


class BandsExtractor:
    BANDS = {
        "default": [],
        "s2a_prd_msil1c": [
            Band("1", 443.9, 60, 0.0001, 0, "int16", "1").serialize(),
            Band("2", 496.6, 10, 0.0001, 0, "int16",
                 "1", name="blue").serialize(),
            Band("3", 560, 10, 0.0001, 0, "int16",
                 "1", name="green").serialize(),
            Band("4", 664.5, 10, 0.0001, 0, "int16",
                 "1", name="red").serialize(),
            Band("5", 703.9, 20, 0.0001, 0, "int16", "1").serialize(),
            Band("6", 740.2, 20, 0.0001, 0, "int16", "1").serialize(),
            Band("7", 782.5, 20, 0.0001, 0, "int16", "1").serialize(),
            Band("8", 835.1, 10, 0.0001, 0, "int16",
                 "1", name="nir").serialize(),
            Band("8a", 864.8, 20, 0.0001, 0, "int16", "1").serialize(),
            Band("9", 945, 60, 0.0001, 0, "int16", "1").serialize(),
            Band("10", 1373.5, 60, 0.0001, 0, "int16", "1").serialize(),
            Band("11",  1613.7, 20, 0.0001, 0, "int16", "1").serialize(),
            Band("12", 2202.4, 20, 0.0001, 0, "int16", "1").serialize()
        ]
    }

    def get_bands(self, product_id):
        return self.BANDS.get(product_id, "default")
