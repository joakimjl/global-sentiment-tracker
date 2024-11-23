from GDELT import fetch_gdelt_headline
from os import walk



if __name__ == "__main__":
    #siterelevancecsvs\ranks.semrushranks-af-20241121-2024-11-22T01_13_26Z.csv

    
    f = []
    for (dirpath, dirnames, filenames) in walk("siterelevancecsvs/"):
        f.extend(filenames)
        break

    print(f)

    fetch_gdelt_headline()