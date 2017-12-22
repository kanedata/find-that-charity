import urllib.request
import argparse
import zipfile
from bs4 import BeautifulSoup
import re
import bcp
import os
import mechanicalsoup


def main():
    parser = argparse.ArgumentParser(description='Fetch needed data sources.')
    parser.add_argument('--dual', type=str,
                        default='https://gist.github.com/drkane/22d62e07346084fafdcc7d9f5e1cd661/raw/bec666d1bc5c6efb8503a90f76ac0c6236ebc183/dual-registered-uk-charities.csv',
                        help='CSV with dual registered charities in')
    parser.add_argument('--oscr', type=str,
                        default="https://www.oscr.org.uk/charities/search-scottish-charity-register/charity-register-download", 
                        help="URL of page containing Scottish charity data")
    parser.add_argument('--ccew', type=str,
                        default="http://data.charitycommission.gov.uk/", help="URL of page containing Charity Commission data")
    parser.add_argument('--ccni', type=str,
                        default="http://www.charitycommissionni.org.uk/charity-search/?q=&include=Linked&include=Removed&exportCSV=1", help="CSV of Northern Ireland Charity Commission data")
    parser.add_argument('--ccni_extra', type=str,
                        default="https://gist.githubusercontent.com/BobHarper1/2687545c562b47bc755aef2e9e0de537/raw/ac052c33fd14a08dd4c2a0604b54c50bc1ecc0db/ccni_extra",
                        help='CSV for NI charities with other names')
    parser.add_argument('--skip-oscr', action='store_true',
                        help='Don\'t fetch data from Office of the Scottish Charity Regulator.')
    parser.add_argument('--skip-ccew', action='store_true',
                        help='Don\'t fetch data from Charity Commission for England and Wales.')
    parser.add_argument('--folder', type='str', default='data',
                        help='Root path of the data folder.')
    args = parser.parse_args()

    # make folder if it's not already there
    if not os.path.exists(args.folder):
        os.makedirs(args.folder)

    # retrieve dual registered charities
    urllib.request.urlretrieve(args.dual, os.path.join(args.folder, "dual-registered-uk-charities.csv"))
    print("[Dual] Dual registered charities fetched")

    # retrieve ni charity extra names
    urllib.request.urlretrieve(args.ccni_extra, os.path.join(args.folder, "ccni_extra_names.csv"))
    print("[CCNI Extra] Extra Northern Ireland charity names fetched")

    # get oscr data
    if not args.skip_oscr:

        FORM_ID = "#uxSiteForm"
        TERMS_AND_CONDITIONS_CHECKBOX = "ctl00$ctl00$ctl00$ContentPlaceHolderDefault$WebsiteContent$ctl05$CharityRegDownload_10$cbTermsConditions"

        browser = mechanicalsoup.StatefulBrowser()
        print("[OSCR] Using url: %s" % args.oscr)
        browser.open(args.oscr)

        browser.select_form(FORM_ID)
        browser[TERMS_AND_CONDITIONS_CHECKBOX] = True
        resp = browser.submit_selected()
        print("[OSCR] Form submitted")
        try:
            resp.raise_for_status()
        except:
            raise ValueError("[OSCR] Could not download OSCR data. Status %s %s" % (
                resp.status, resp.reason))

        oscr_out = os.path.join(args.folder, "oscr.zip")
        with open(oscr_out, "wb") as oscrfile:
            oscrfile.write(resp.content)
        print("[OSCR] ZIP downloaded")

        with zipfile.ZipFile(oscr_out) as oscrzip:
            files = oscrzip.infolist()
            if len(files) != 1:
                raise ValueError("More than one file in OSCR zip")
            with open(os.path.join(args.folder, "oscr.csv"), "wb") as oscrcsv:
                oscrcsv.write(oscrzip.read(files[0]))
            print("[OSCR] data extracted")

    # get charity commission data
    if not args.skip_ccew:
        ccew_html = urllib.request.urlopen(args.ccew)
        ccew_out = os.path.join(args.folder, "ccew.zip")
        ccew_folder = os.path.join(args.folder, "ccew")
        if ccew_html.status != 200:
            raise ValueError("[CCEW] Could not find Charity Commission data page. Status %s %s" % (ccew_data.status, ccew_data.reason))
        ccew_html = ccew_html.read()
        ccew_soup = BeautifulSoup(ccew_html, 'html.parser')
        zip_regex = re.compile("http://apps.charitycommission.gov.uk/data/.*?/RegPlusExtract.*?\.zip")
        ccew_data_url = ccew_soup.find("a", href=zip_regex)["href"]
        print("[CCEW] Using url: %s" % ccew_data_url)
        urllib.request.urlretrieve(ccew_data_url, ccew_out)
        print("[CCEW] ZIP downloaded")

        with zipfile.ZipFile(ccew_out) as ccew_zip:
            if not os.path.isdir(ccew_folder):
                os.makedirs(ccew_folder)
            for f in ccew_zip.infolist():
                bcp_content = ccew_zip.read(f)
                csv_content = bcp.convert(bcp_content.decode("latin1"))
                csv_filename = f.filename.replace(".bcp", ".csv")
                with open(os.path.join(ccew_folder, csv_filename), "w", encoding="latin1") as a:
                    a.write(csv_content.replace('\x00', ''))
                    print("[CCEW] write %s" % csv_filename)

    # @TODO get charity commission register of mergers

    # download Northern Ireland register of charities
    if args.ccni:
        print("[CCNI] Using url: %s" % args.ccni)
        urllib.request.urlretrieve(args.ccni, os.path.join('data', 'ccni.csv'))
        print("[CCNI] CSV downloaded")

if __name__ == '__main__':
    main()
