"""
Script for fetching data from charity regulators
"""
import urllib.request
import argparse
import zipfile
import re
import os

from bs4 import BeautifulSoup
import mechanicalsoup

import bcp

DUAL_CSV = 'https://raw.githubusercontent.com/drkane/charity-lookups/master/dual-registered-uk-charities.csv'
OSCR_URL = "https://www.oscr.org.uk/umbraco/Surface/FormsSurface/CharityRegDownload"
CCEW_URL = "http://data.charitycommission.gov.uk/"
CCNI_URL = "https://www.charitycommissionni.org.uk/umbraco/api/charityApi/ExportSearchResultsToCsv/?pageNumber=1&include=Linked&include=Removed"
CCNI_EXTRA = "https://gist.githubusercontent.com/BobHarper1/2687545c562b47bc755aef2e9e0de537/raw/ac052c33fd14a08dd4c2a0604b54c50bc1ecc0db/ccni_extra"

def main():


    def add_bool_arg(parser, name, default=False, help=None):
        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument('--' + name, dest=name, action='store_true', help=help)
        group.add_argument('--no-' + name, dest=name, action='store_false', help=help)
        parser.set_defaults(**{name:default})

    """
    Function to fetch data from Charity regulators
    """
    parser = argparse.ArgumentParser(description='Fetch needed data sources.')
    parser.add_argument('--dual', type=str,
                        default=DUAL_CSV,
                        help='CSV with dual registered charities in')
    parser.add_argument('--oscr-url', type=str,
                        default=OSCR_URL,
                        help="URL of page containing Scottish charity data")
    parser.add_argument('--ccew-url', type=str,
                        default=CCEW_URL,
                        help="URL of page containing Charity Commission data")
    parser.add_argument('--ccni-url', type=str,
                        default=CCNI_URL,
                        help="CSV of Northern Ireland Charity Commission data")
    parser.add_argument('--ccni-extra', type=str,
                        default=CCNI_EXTRA,
                        help='CSV for NI charities with other names')

    # add args to turn on or off the various data sources
    add_bool_arg(parser, 'oscr', default=True, help='Fetch data from Office of the Scottish Charity Regulator')
    add_bool_arg(parser, 'ccew', default=True, help='Fetch data from Charity Commission for England and Wales')
    add_bool_arg(parser, 'ccni', default=True, help='fetch data from Charity Commission for Northern Ireland')
    
    parser.add_argument('--folder', type=str, default='data',
                        help='Root path of the data folder.')
    args = parser.parse_args()

    # make folder if it's not already there
    if not os.path.exists(args.folder):
        os.makedirs(args.folder)

    # retrieve dual registered charities
    urllib.request.urlretrieve(
        args.dual,
        os.path.join(args.folder, "dual-registered-uk-charities.csv")
    )
    print("[Dual] Dual registered charities fetched")

    # get oscr data
    if args.oscr:
        oscr_out = os.path.join(args.folder, "oscr.zip")
        urllib.request.urlretrieve(args.oscr_url, oscr_out)
        print("[OSCR] ZIP downloaded")

        try:
            with zipfile.ZipFile(oscr_out) as oscrzip:
                files = oscrzip.infolist()
                if len(files) != 1:
                    raise ValueError("More than one file in OSCR zip")
                with open(os.path.join(args.folder, "oscr.csv"), "wb") as oscrcsv:
                    oscrcsv.write(oscrzip.read(files[0]))
                print("[OSCR] data extracted")
        except zipfile.BadZipFile:
            print("[OSCR] data could not be found")

    # get charity commission data
    if args.ccew:
        ccew_html = urllib.request.urlopen(args.ccew_url)
        ccew_out = os.path.join(args.folder, "ccew.zip")
        ccew_folder = os.path.join(args.folder, "ccew")
        if ccew_html.status != 200:
            raise ValueError("[CCEW] Could not find Charity Commission data page. Status %s %s" % (ccew_html.status, ccew_html.reason))
        ccew_soup = BeautifulSoup(ccew_html.read(), 'html.parser')
        zip_regex = re.compile(r"http://apps.charitycommission.gov.uk/data/.*?/RegPlusExtract.*?\.zip")
        ccew_data_url = ccew_soup.find("a", href=zip_regex)["href"]
        print("[CCEW] Using url: %s" % ccew_data_url)
        urllib.request.urlretrieve(ccew_data_url, ccew_out)
        print("[CCEW] ZIP downloaded")

        with zipfile.ZipFile(ccew_out) as ccew_zip:
            if not os.path.isdir(ccew_folder):
                os.makedirs(ccew_folder)
            for ccew_zip_file in ccew_zip.infolist():
                bcp_content = ccew_zip.read(ccew_zip_file)
                csv_content = bcp.convert(bcp_content.decode("latin1"))
                csv_filename = ccew_zip_file.filename.replace(".bcp", ".csv")
                with open(os.path.join(ccew_folder, csv_filename), "w", encoding="latin1") as ccew_zip_csv:
                    ccew_zip_csv.write(csv_content.replace('\x00', ''))
                    print("[CCEW] write %s" % csv_filename)

    # @TODO get charity commission register of mergers

    # download Northern Ireland register of charities
    if args.ccni:

        # retrieve ni charity extra names
        urllib.request.urlretrieve(args.ccni_extra, os.path.join(args.folder, "ccni_extra_names.csv"))
        print("[CCNI Extra] Extra Northern Ireland charity names fetched")

        print("[CCNI] Using url: %s" % args.ccni_url)
        urllib.request.urlretrieve(args.ccni_url, os.path.join(args.folder, 'ccni.csv'))
        print("[CCNI] CSV downloaded")

if __name__ == '__main__':
    main()
