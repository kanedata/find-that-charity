import csv
import zipfile
import io
import argparse
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

INDEX_NAME = "postcode"

NAME_FILES = [
    {"file": "Documents/2011 Census Output Area Classification Names and Codes UK.txt", "type_field": "oac11", "code_field": "OAC11", "name_field": "Subgroup", "welsh_name_field": None },
    {"file": "Documents/BUASD_names and codes UK as at 12_13.txt", "type_field": "buasd11", "code_field": "BUASD13CD", "name_field": "BUASD13NM", "welsh_name_field": None },
    {"file": "Documents/BUA_names and codes UK as at 12_13.txt", "type_field": "bua11", "code_field": "BUA13CD", "name_field": "BUA13NM", "welsh_name_field": None },
    {"file": "Documents/CCG names and codes UK as at 07_15.txt", "type_field": "ccg", "code_field": "CCG15CD", "name_field": "CCG15NM", "welsh_name_field": "CCG15NMW" },
    {"file": "Documents/Country names and codes UK as at 08_12.txt", "type_field": "ctry", "code_field": "CTRY12CD", "name_field": "CTRY12NM", "welsh_name_field": "CTRY12NMW" },
    {"file": "Documents/County names and codes UK as at 12_10.txt", "type_field": "cty", "code_field": "CTY10CD", "name_field": "CTY10NM", "welsh_name_field": None },
    {"file": "Documents/EER names and codes UK as at 12_10.txt", "type_field": "eer", "code_field": "EER10CD", "name_field": "EER10NM", "welsh_name_field": None },
    {"file": "Documents/HLTHAU names and codes UK as at 12_16.txt", "type_field": "hlthau", "code_field": "HLTHAUCD", "name_field": "HLTHAUNM", "welsh_name_field": "HLTHAUNMW" },
    {"file": "Documents/LAU2 names and codes UK as at 12_16 (NUTS).txt", "type_field": "nuts", "code_field": "LAU216CD", "name_field": "LAU216NM", "welsh_name_field": None },
    {"file": "Documents/LA_UA names and codes UK as at 12_16.txt", "type_field": "laua", "code_field": "LAD16CD", "name_field": "LAD16NM", "welsh_name_field": None },
    {"file": "Documents/LEP names and codes EN as at 12_13.txt", "type_field": "lep", "code_field": "LEP13CD1", "name_field": "LEP13NM1", "welsh_name_field": None },
    {"file": "Documents/LSOA (2011) names and codes UK as at 12_12.txt", "type_field": "lsoa11", "code_field": "LSOA11CD", "name_field": "LSOA11NM", "welsh_name_field": None },
    {"file": "Documents/MSOA (2011) names and codes UK as at 12_12.txt", "type_field": "msoa11", "code_field": "MSOA11CD", "name_field": "MSOA11NM", "welsh_name_field": None },
    {"file": "Documents/National Park names and codes GB as at 08_16.txt", "type_field": "park", "code_field": "NPARK16CD", "name_field": "NPARK16NM", "welsh_name_field": None },
    {"file": "Documents/Pan SHA names and codes EN as at 12_10 (HRO).txt", "type_field": "hro", "code_field": "PSHA10CD", "name_field": "PSHA10NM", "welsh_name_field": None },
    {"file": "Documents/PCT names and codes UK as at 12_16.txt", "type_field": "pct", "code_field": "PCTCD", "name_field": "PCTNM", "welsh_name_field": "PCTNMW" },
    {"file": "Documents/PFA names and codes GB as at 12_15.txt", "type_field": "pfa", "code_field": "PFA15CD", "name_field": "PFA15NM", "welsh_name_field": None },
    {"file": "Documents/Region names and codes EN as at 12_10 (GOR).txt", "type_field": "gor", "code_field": "GOR10CD", "name_field": "GOR10NM", "welsh_name_field": "GOR10NMW" },
    {"file": "Documents/Rural Urban (2011) Indicator names and codes GB as at 12_16.txt", "type_field": "ru11ind", "code_field": "RU11IND", "name_field": "RU11NM", "welsh_name_field": None },
    {"file": "Documents/TECLEC names and codes UK as at 12_16.txt", "type_field": "teclec", "code_field": "TECLECCD", "name_field": "TECLECNM", "welsh_name_field": None },
    {"file": "Documents/TTWA names and codes UK as at 12_11 v5.txt", "type_field": "ttwa", "code_field": "TTWA11CD", "name_field": "TTWA11NM", "welsh_name_field": None },
    {"file": "Documents/Westminster Parliamentary Constituency names and codes UK as at 12_14.txt", "type_field": "pcon", "code_field": "PCON14CD", "name_field": "PCON14NM", "welsh_name_field": None },
    {"file": "Documents/Ward names and codes UK as at 12_16.txt", "type_field": "ward", "code_field": "WD16CD", "name_field": "WD16NM", "welsh_name_field": None },
    #{"file": "Documents/LAU216_LAU116_NUTS315_NUTS215_NUTS115_UK_LU.txt", "type_field": "", "name_field": "", "welsh_name_field": None },
]

def main():
    parser = argparse.ArgumentParser(description='Import postcodes into elasticsearch.')
    parser.add_argument('--nspl', type=str,
                        default='data/NSPL.zip',
                        help='ZIP file for National Statistics Postcode Lookup')
    args = parser.parse_args()

    postcodes = []

    es = Elasticsearch()

    with zipfile.ZipFile(args.nspl) as pczip:
        for f in pczip.filelist:
            if f.filename.endswith(".csv") and f.filename.startswith("Data/multi_csv/NSPL_"):
                print ("[postcodes] Opening %s" % f.filename)
                pcount = 0
                with pczip.open(f, 'rU') as pccsv:
                    pccsv  = io.TextIOWrapper(pccsv)
                    reader = csv.DictReader(pccsv)
                    for i in reader:
                        i["_index"] = INDEX_NAME
                        i["_type"] = "postcode"
                        i["_op_type"] = "index"
                        i["_id"] = i["pcds"]

                        # null any blank fields
                        for k in i:
                            if i[k]=="":
                                i[k] = None

                        # date fields
                        for j in ["dointr", "doterm"]:
                            if i[j]:
                                i[j] = datetime.strptime(i[j], "%Y%m")

                        # latitude and longitude
                        for j in ["lat", "long"]:
                            if i[j]:
                                i[j] = float(i[j])
                                if i[j]==99.999999:
                                    i[j] = None
                        if i["lat"] and i["long"]:
                            i["location"] = {"lat": i["lat"], "lon": i["long"]}

                        # integer fields
                        for j in ["oseast1m", "osnrth1m", "usertype", "osgrdind", "imd"]:
                            if i[j]:
                                i[j] = int(i[j])
                        postcodes.append(i)
                        pcount += 1

                        if pcount % 100000 == 0:
                            print("[postcodes] Processed %s postcodes" % pcount)
                            print("[elasticsearch] %s postcodes to save" % len(postcodes))
                            results = bulk(es, postcodes)
                            print("[elasticsearch] saved %s postcodes to %s index" % (results[0], INDEX_NAME))
                            print("[elasticsearch] %s errors reported" % len(results[1]) )
                            postcodes = []
                    print("[postcodes] Processed %s postcodes" % pcount)
                    print("[elasticsearch] %s postcodes to save" % len(postcodes))
                    results = bulk(es, postcodes)
                    print("[elasticsearch] saved %s postcodes to %s index" % (results[0], INDEX_NAME))
                    print("[elasticsearch] %s errors reported" % len(results[1]) )
                    postcodes = []

            # add names and codes
            if f.filename in [i["file"] for i in NAME_FILES]:
                codes = [i for i in NAME_FILES if i["file"]==f.filename][0]
                names_and_codes = []
                print("[codes] adding codes for '%s' field" % codes["type_field"])
                with pczip.open(codes["file"], 'rU') as nccsv:
                    nccsv  = io.TextIOWrapper(nccsv)
                    reader = csv.DictReader(nccsv, delimiter='\t')
                    for i in reader:
                        i["_id"] = i[codes["code_field"]]
                        i["_index"] = INDEX_NAME
                        i["_type"] = "code"
                        i["_op_type"] = "index"
                        i["type"] = codes["type_field"]
                        if codes["name_field"]:
                            i["name"] = i[codes["name_field"]]
                            i["name_welsh"] = i["name"]
                            if codes["welsh_name_field"]:
                                i["name_welsh"] = i[codes["welsh_name_field"]]

                        if '' in i:
                            del i['']
                        names_and_codes.append(i)
                    print("[elasticsearch] %s codes to save" % len(names_and_codes))
                    if codes["type_field"]=="cty":
                        print(names_and_codes)
                    results = bulk(es, names_and_codes)
                    print("[elasticsearch] saved %s codes to %s index" % (results[0], INDEX_NAME))
                    print("[elasticsearch] %s errors reported" % len(results[1]) )


if __name__ == '__main__':
    main()
