from os.path import join

import requests


def get_data(url: str, identifier: str, output_folder: str) -> None:
    response = requests.get(f"{url}/{identifier}.zip")
    with open(join(output_folder, f"{identifier}.zip"), "wb") as file:
        file.write(response.content)


def main():
    url = "https://openeo.eodc.eu/test-files"
    output_folder = "/home/sherrmann/data"
    identifier_list = [
        "S2A_MSIL1C_20180608T101021_N0206_R022_T32TPS_20180608T135059",
        "S2A_MSIL1C_20180611T102021_N0206_R065_T32TPS_20180611T123241",
        "S2A_MSIL1C_20180618T101021_N0206_R022_T32TPS_20180618T135619",
        "S2A_MSIL1C_20180621T102021_N0206_R065_T32TPS_20180621T140615",
        "S2B_MSIL1C_20180606T102019_N0206_R065_T32TPS_20180606T172808",
        "S2B_MSIL1C_20180613T101019_N0206_R022_T32TPS_20180613T122213",
        "S2B_MSIL1C_20180616T102019_N0206_R065_T32TPS_20180616T154713",
    ]
    for identifier in identifier_list:
        get_data(url, identifier, output_folder)


if __name__ == '__main__':
    main()
