import datetime
import io

from openpyxl import load_workbook

from ftc.management.commands._base_scraper import HTMLScraper, AREA_TYPES
from ftc.models import Organisation


class Command(HTMLScraper):
    """
    Spider for scraping details of Registered Social Landlords in England
    """
    name = 'rsl'
    allowed_domains = ['gov.uk', 'githubusercontent.com']
    start_urls = [
        "https://www.gov.uk/government/publications/current-registered-providers-of-social-housing",
    ]
    org_id_prefix = "GB-SHPE"
    id_field = "Registration Number"
    source = {
        "title": "Current registered providers of social housing",
        "description": "Current registered providers of social housing and new registrations and deregistrations. Covers England",
        "identifier": "rsl",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Regulator of Social Housing",
            "website": "https://www.gov.uk/government/organisations/regulator-of-social-housing",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "",
                "title": "Current registered providers of social housing"
            }
        ],
    }
    orgtypes = ["Registered Provider of Social Housing"]

    def parse_file(self, response, source_url):
        link = [l for l in response.html.links if l.endswith(".xlsx")][0]
        # self.source["distribution"][0]["downloadURL"] = link
        # self.source["distribution"][0]["accessURL"] = self.start_urls[0]
        # self.source["modified"] = datetime.datetime.now().isoformat()
        r = self.session.get(link)
        
        wb = load_workbook(io.BytesIO(r.content), read_only=True)
        ws = wb['Organisation Advanced Find View']
        
        # self.source["issued"] = wb.properties.modified.isoformat()[0:10]
        
        headers = None
        for k, row in enumerate(ws.rows):
            if not headers:
                headers = [c.value for c in row]
            else:
                record = dict(zip(headers, [c.value for c in row]))
                self.parse_row(record)

    def parse_row(self, record):

        record = self.clean_fields(record)

        org_types = [
            self.add_org_type("Registered Provider of Social Housing"),
        ]
        if record.get("Corporate Form"):
            if record["Corporate Form"] == "Company":
                org_types.append(self.add_org_type("Registered Company"))
                org_types.append(self.add_org_type("{} {}".format(record["Designation"], record["Corporate Form"])))
            elif record["Corporate Form"] == "CIO-Charitable Incorporated Organisation":
                org_types.append(self.add_org_type("Charitable Incorporated Organisation"))
                org_types.append(self.add_org_type("Registered Charity"))
            elif record["Corporate Form"] == "Charitable Company":
                org_types.append(self.add_org_type("Registered Company"))
                org_types.append(self.add_org_type("Incorporated Charity"))
                org_types.append(self.add_org_type("Registered Charity"))
            elif record["Corporate Form"] == "Unincorporated Charity":
                org_types.append(self.add_org_type("Registered Charity"))
            else:
                org_types.append(self.add_org_type(record["Corporate Form"]))
        elif record.get("Designation"):
            org_types.append(self.add_org_type(record["Designation"]))

        org_ids = [self.get_org_id(record)]
        locations = []
        if record.get("Designation") == "Local Authority":
            la_codes = LA_LOOKUP.get(record.get(self.id_field))
            if la_codes:
                org_ids.append("GB-LAE-{}".format(
                    la_codes.get("register-code")
                ))
                locations.append({
                    "id": la_codes.get("GSS"),
                    "name": la_codes.get("name"),
                    "geoCode": la_codes.get("GSS"),
                    "geoCodeType": AREA_TYPES.get(la_codes.get("GSS")[0:3], "Local Authority"),
                })

        self.records.append(
            Organisation(**{
                "org_id": self.get_org_id(record),
                "name": record.get("Organisation Name"),
                "charityNumber": None,
                "companyNumber": None,
                "streetAddress": None,
                "addressLocality": None,
                "addressRegion": None,
                "addressCountry": "England",
                "postalCode": None,
                "telephone": None,
                "alternateName": [],
                "email": None,
                "description": None,
                "organisationType": [o.slug for o in org_types],
                "organisationTypePrimary": org_types[0],
                "url": None,
                "location": locations,
                "latestIncome": None,
                "dateModified": datetime.datetime.now(),
                "dateRegistered": record.get("Registration Date"),
                "dateRemoved": None,
                "active": True,
                "parent": None,
                "orgIDs": org_ids,
                "scrape": self.scrape,
                "source": self.source,
                "spider": self.name,
            })
        )


LA_LOOKUP = {
    '45UB': {'GSS': 'E07000223', 'register-code': 'ADU', 'name': 'Adur'},
    '45UC': {'GSS': 'E07000224', 'register-code': 'ARU', 'name': 'Arun'},
    '37UB': {'GSS': 'E07000170', 'register-code': 'ASH', 'name': 'Ashfield'},
    '29UB': {'GSS': 'E07000105', 'register-code': 'ASF', 'name': 'Ashford'},
    '42UB': {'GSS': 'E07000200', 'register-code': 'BAB', 'name': 'Babergh'},
    '00CC': {'GSS': 'E08000016', 'register-code': 'BNS', 'name': 'Barnsley'},
    '16UC': {'GSS': 'E07000027', 'register-code': 'BAR', 'name': 'Barrow-in-Furness'},
    '22UB': {'GSS': 'E07000066', 'register-code': 'BAI', 'name': 'Basildon'},
    '37UC': {'GSS': 'E07000171', 'register-code': 'BAE', 'name': 'Bassetlaw'},
    '00CN': {'GSS': 'E08000025', 'register-code': 'BIR', 'name': 'Birmingham'},
    '00EY': {'GSS': 'E06000009', 'register-code': 'BPL', 'name': 'Blackpool'},
    '17UC': {'GSS': 'E07000033', 'register-code': 'BOS', 'name': 'Bolsover'},
    '00BL': {'GSS': 'E08000001', 'register-code': 'BOL', 'name': 'Bolton'},
    '00HP': {'GSS': 'E06000029', 'register-code': 'POL', 'name': 'Poole'},
    '00HN': {'GSS': 'E06000028', 'register-code': 'BMH', 'name': 'Bournemouth'},
    '5069': {'GSS': 'E06000058', 'register-code': 'BPC', 'name': 'Bournemouth, Christchurch and Poole'},
    '00MA': {'GSS': 'E06000036', 'register-code': 'BRC', 'name': 'Bracknell Forest'},
    '22UD': {'GSS': 'E07000068', 'register-code': 'BRW', 'name': 'Brentwood'},
    '00ML': {'GSS': 'E06000043', 'register-code': 'BNH', 'name': 'Brighton and Hove'},
    '00HB': {'GSS': 'E06000023', 'register-code': 'BST', 'name': 'Bristol, City of'},
    '37UD': {'GSS': 'E07000172', 'register-code': 'BRT', 'name': 'Broxtowe'},
    '00BM': {'GSS': 'E08000002', 'register-code': 'BUR', 'name': 'Bury'},
    '12UB': {'GSS': 'E07000008', 'register-code': 'CAB', 'name': 'Cambridge'},
    '41UB': {'GSS': 'E07000192', 'register-code': 'CAN', 'name': 'Cannock Chase'},
    '29UC': {'GSS': 'E07000106', 'register-code': 'CAT', 'name': 'Canterbury'},
    '22UE': {'GSS': 'E07000069', 'register-code': 'CAS', 'name': 'Castle Point'},
    '00KC': {'GSS': 'E06000056', 'register-code': 'CBF', 'name': 'Central Bedfordshire'},
    '31UC': {'GSS': 'E07000130', 'register-code': 'CHA', 'name': 'Charnwood'},
    '23UB': {'GSS': 'E07000078', 'register-code': 'CHT', 'name': 'Cheltenham'},
    '38UB': {'GSS': 'E07000177', 'register-code': 'CHR', 'name': 'Cherwell'},
    '00EW': {'GSS': 'E06000050', 'register-code': 'CHW', 'name': 'Cheshire West and Chester'},
    '17UD': {'GSS': 'E07000034', 'register-code': 'CHS', 'name': 'Chesterfield'},
    '30UE': {'GSS': 'E07000118', 'register-code': 'CHO', 'name': 'Chorley'},
    '00CX': {'GSS': 'E08000032', 'register-code': 'BRD', 'name': 'Bradford'},
    '32UD': {'GSS': 'E07000138', 'register-code': 'LIC', 'name': 'Lincoln'},
    '00AA': {'GSS': 'E09000001', 'register-code': 'LND', 'name': 'City of London'},
    '00DB': {'GSS': 'E08000036', 'register-code': 'WKF', 'name': 'Wakefield'},
    '00BK': {'GSS': 'E09000033', 'register-code': 'WSM', 'name': 'Westminster'},
    '00FF': {'GSS': 'E06000014', 'register-code': 'YOR', 'name': 'York'},
    '22UG': {'GSS': 'E07000071', 'register-code': 'COL', 'name': 'Colchester'},
    '34UB': {'GSS': 'E07000150', 'register-code': 'COR', 'name': 'Corby'},
    '00HE': {'GSS': 'E06000052', 'register-code': 'CON', 'name': 'Cornwall'},
    '00HF': {'GSS': 'E06000053', 'register-code': 'IOS', 'name': 'Isles of Scilly'},
    '36UB': {'GSS': 'E07000163', 'register-code': 'CRA', 'name': 'Craven'},
    '45UE': {'GSS': 'E07000226', 'register-code': 'CRW', 'name': 'Crawley'},
    '26UC': {'GSS': 'E07000096', 'register-code': 'DAC', 'name': 'Dacorum'},
    '00EH': {'GSS': 'E06000005', 'register-code': 'DAL', 'name': 'Darlington'},
    '29UD': {'GSS': 'E07000107', 'register-code': 'DAR', 'name': 'Dartford'},
    '5076': {'GSS': 'E07000151', 'register-code': 'DAV', 'name': 'Daventry'},
    '00FK': {'GSS': 'E06000015', 'register-code': 'DER', 'name': 'Derby'},
    '00CE': {'GSS': 'E08000017', 'register-code': 'DNC', 'name': 'Doncaster'},
    '29UE': {'GSS': 'E07000108', 'register-code': 'DOV', 'name': 'Dover'},
    '00CR': {'GSS': 'E08000027', 'register-code': 'DUD', 'name': 'Dudley'},
    '00EJ': {'GSS': 'E06000047', 'register-code': 'DUR', 'name': 'County Durham'},
    '18UB': {'GSS': 'E07000040', 'register-code': 'EDE', 'name': 'East Devon'},
    '5070': {'GSS': 'E07000244', 'register-code': 'ESK', 'name': 'East Suffolk'},
    '26UD': {'GSS': 'E07000097', 'register-code': 'EHE', 'name': 'East Hertfordshire'},
    '00FB': {'GSS': 'E06000011', 'register-code': 'ERY', 'name': 'East Riding of Yorkshire'},
    '21UC': {'GSS': 'E07000061', 'register-code': 'EAS', 'name': 'Eastbourne'},
    '22UH': {'GSS': 'E07000072', 'register-code': 'EPP', 'name': 'Epping Forest'},
    '18UC': {'GSS': 'E07000041', 'register-code': 'EXE', 'name': 'Exeter'},
    '24UE': {'GSS': 'E07000087', 'register-code': 'FAR', 'name': 'Fareham'},
    '42UC': {'GSS': 'E07000201', 'register-code': 'FOR', 'name': 'Forest Heath'},
    '00CH': {'GSS': 'E08000037', 'register-code': 'GAT', 'name': 'Gateshead'},
    '23UE': {'GSS': 'E07000081', 'register-code': 'GLO', 'name': 'Gloucester'},
    '24UF': {'GSS': 'E07000088', 'register-code': 'GOS', 'name': 'Gosport'},
    '29UG': {'GSS': 'E07000109', 'register-code': 'GRA', 'name': 'Gravesham'},
    '33UD': {'GSS': 'E07000145', 'register-code': 'GRY', 'name': 'Great Yarmouth'},
    '43UD': {'GSS': 'E07000209', 'register-code': 'GRT', 'name': 'Guildford'},
    '00AP': {'GSS': 'E09000014', 'register-code': 'HRY', 'name': 'Haringey'},
    '22UJ': {'GSS': 'E07000073', 'register-code': 'HAR', 'name': 'Harlow'},
    '36UD': {'GSS': 'E07000165', 'register-code': 'HAG', 'name': 'Harrogate'},
    '00EB': {'GSS': 'E06000001', 'register-code': 'HPL', 'name': 'Hartlepool'},
    '17UH': {'GSS': 'E07000037', 'register-code': 'HIG', 'name': 'High Peak'},
    '31UE': {'GSS': 'E07000132', 'register-code': 'HIN', 'name': 'Hinckley and Bosworth'},
    '42UD': {'GSS': 'E07000202', 'register-code': 'IPS', 'name': 'Ipswich'},
    '34UE': {'GSS': 'E07000153', 'register-code': 'KET', 'name': 'Kettering'},
    '00FA': {'GSS': 'E06000010', 'register-code': 'KHL', 'name': 'Kingston upon Hull, City of'},
    '00CZ': {'GSS': 'E08000034', 'register-code': 'KIR', 'name': 'Kirklees'},
    '30UH': {'GSS': 'E07000121', 'register-code': 'LAC', 'name': 'Lancaster'},
    '00DA': {'GSS': 'E08000035', 'register-code': 'LDS', 'name': 'Leeds'},
    '00FN': {'GSS': 'E06000016', 'register-code': 'LCE', 'name': 'Leicester'},
    '21UF': {'GSS': 'E07000063', 'register-code': 'LEE', 'name': 'Lewes'},
    '00AB': {'GSS': 'E09000002', 'register-code': 'BDG', 'name': 'Barking and Dagenham'},
    '00AC': {'GSS': 'E09000003', 'register-code': 'BNE', 'name': 'Barnet'},
    '00AD': {'GSS': 'E09000004', 'register-code': 'BEX', 'name': 'Bexley'},
    '00AE': {'GSS': 'E09000005', 'register-code': 'BEN', 'name': 'Brent'},
    '00AG': {'GSS': 'E09000007', 'register-code': 'CMD', 'name': 'Camden'},
    '00AH': {'GSS': 'E09000008', 'register-code': 'CRY', 'name': 'Croydon'},
    '00AJ': {'GSS': 'E09000009', 'register-code': 'EAL', 'name': 'Ealing'},
    '00AK': {'GSS': 'E09000010', 'register-code': 'ENF', 'name': 'Enfield'},
    '00AL': {'GSS': 'E09000011', 'register-code': 'GRE', 'name': 'Greenwich'},
    '00AM': {'GSS': 'E09000012', 'register-code': 'HCK', 'name': 'Hackney'},
    '00AN': {'GSS': 'E09000013', 'register-code': 'HMF', 'name': 'Hammersmith and Fulham'},
    '00AQ': {'GSS': 'E09000015', 'register-code': 'HRW', 'name': 'Harrow'},
    '00AR': {'GSS': 'E09000016', 'register-code': 'HAV', 'name': 'Havering'},
    '00AS': {'GSS': 'E09000017', 'register-code': 'HIL', 'name': 'Hillingdon'},
    '00AT': {'GSS': 'E09000018', 'register-code': 'HNS', 'name': 'Hounslow'},
    '00AU': {'GSS': 'E09000019', 'register-code': 'ISL', 'name': 'Islington'},
    '00AY': {'GSS': 'E09000022', 'register-code': 'LBH', 'name': 'Lambeth'},
    '00AZ': {'GSS': 'E09000023', 'register-code': 'LEW', 'name': 'Lewisham'},
    '00BA': {'GSS': 'E09000024', 'register-code': 'MRT', 'name': 'Merton'},
    '00BB': {'GSS': 'E09000025', 'register-code': 'NWM', 'name': 'Newham'},
    '00BC': {'GSS': 'E09000026', 'register-code': 'RDB', 'name': 'Redbridge'},
    '00BF': {'GSS': 'E09000029', 'register-code': 'STN', 'name': 'Sutton'},
    '00BG': {'GSS': 'E09000030', 'register-code': 'TWH', 'name': 'Tower Hamlets'},
    '00BH': {'GSS': 'E09000031', 'register-code': 'WFT', 'name': 'Waltham Forest'},
    '00BJ': {'GSS': 'E09000032', 'register-code': 'WND', 'name': 'Wandsworth'},
    '00KA': {'GSS': 'E06000032', 'register-code': 'LUT', 'name': 'Luton'},
    '5074': {'GSS': 'E08000012', 'register-code': 'LIV', 'name': 'Liverpool'},
    '29UH': {'GSS': 'E07000110', 'register-code': 'MAI', 'name': 'Maidstone'},
    '00BN': {'GSS': 'E08000003', 'register-code': 'MAN', 'name': 'Manchester'},
    '37UF': {'GSS': 'E07000174', 'register-code': 'MAS', 'name': 'Mansfield'},
    '00LC': {'GSS': 'E06000035', 'register-code': 'MDW', 'name': 'Medway'},
    '31UG': {'GSS': 'E07000133', 'register-code': 'MEL', 'name': 'Melton'},
    '18UD': {'GSS': 'E07000042', 'register-code': 'MDE', 'name': 'Mid Devon'},
    '42UE': {'GSS': 'E07000203', 'register-code': 'MSU', 'name': 'Mid Suffolk'},
    '00EC': {'GSS': 'E06000002', 'register-code': 'MDB', 'name': 'Middlesbrough'},
    '00MG': {'GSS': 'E06000042', 'register-code': 'MIK', 'name': 'Milton Keynes'},
    '43UE': {'GSS': 'E07000210', 'register-code': 'MOL', 'name': 'Mole Valley'},
    '24UJ': {'GSS': 'E07000091', 'register-code': 'NEW', 'name': 'New Forest'},
    '37UG': {'GSS': 'E07000175', 'register-code': 'NEA', 'name': 'Newark and Sherwood'},
    '00CJ': {'GSS': 'E08000021', 'register-code': 'NET', 'name': 'Newcastle upon Tyne'},
    '17UJ': {'GSS': 'E07000038', 'register-code': 'NED', 'name': 'North East Derbyshire'},
    '32UE': {'GSS': 'E07000139', 'register-code': 'NKE', 'name': 'North Kesteven'},
    '00HC': {'GSS': 'E06000024', 'register-code': 'NSM', 'name': 'North Somerset'},
    '00CK': {'GSS': 'E08000022', 'register-code': 'NTY', 'name': 'North Tyneside'},
    '44UB': {'GSS': 'E07000218', 'register-code': 'NWA', 'name': 'North Warwickshire'},
    '31UH': {'GSS': 'E07000134', 'register-code': 'NWL', 'name': 'North West Leicestershire'},
    '34UF': {'GSS': 'E07000154', 'register-code': 'NOR', 'name': 'Northampton'},
    '00EM': {'GSS': 'E06000057', 'register-code': 'NBL', 'name': 'Northumberland'},
    '33UG': {'GSS': 'E07000148', 'register-code': 'NOW', 'name': 'Norwich'},
    '00FY': {'GSS': 'E06000018', 'register-code': 'NGM', 'name': 'Nottingham'},
    '44UC': {'GSS': 'E07000219', 'register-code': 'NUN', 'name': 'Nuneaton and Bedworth'},
    '31UJ': {'GSS': 'E07000135', 'register-code': 'OAD', 'name': 'Oadby and Wigston'},
    '00BP': {'GSS': 'E08000004', 'register-code': 'OLD', 'name': 'Oldham'},
    '38UC': {'GSS': 'E07000178', 'register-code': 'OXO', 'name': 'Oxford'},
    '00MR': {'GSS': 'E06000044', 'register-code': 'POR', 'name': 'Portsmouth'},
    '00MC': {'GSS': 'E06000038', 'register-code': 'RDG', 'name': 'Reading'},
    '47UD': {'GSS': 'E07000236', 'register-code': 'RED', 'name': 'Redditch'},
    '30UL': {'GSS': 'E07000124', 'register-code': 'RIB', 'name': 'Ribble Valley'},
    '36UE': {'GSS': 'E07000166', 'register-code': 'RIH', 'name': 'Richmondshire'},
    '00BQ': {'GSS': 'E08000005', 'register-code': 'RCH', 'name': 'Rochdale'},
    '30UM': {'GSS': 'E07000125', 'register-code': 'ROS', 'name': 'Rossendale'},
    '00CF': {'GSS': 'E08000018', 'register-code': 'ROT', 'name': 'Rotherham'},
    '00AW': {'GSS': 'E09000020', 'register-code': 'KEC', 'name': 'Kensington and Chelsea'},
    '00AX': {'GSS': 'E09000021', 'register-code': 'KTT', 'name': 'Kingston upon Thames'},
    '44UD': {'GSS': 'E07000220', 'register-code': 'RUG', 'name': 'Rugby'},
    '43UG': {'GSS': 'E07000212', 'register-code': 'RUN', 'name': 'Runnymede'},
    '36UF': {'GSS': 'E07000167', 'register-code': 'RYE', 'name': 'Ryedale'},
    '00BR': {'GSS': 'E08000006', 'register-code': 'SLF', 'name': 'Salford'},
    '00CS': {'GSS': 'E08000028', 'register-code': 'SAW', 'name': 'Sandwell'},
    '40UC': {'GSS': 'E07000188', 'register-code': 'SEG', 'name': 'Sedgemoor'},
    '36UH': {'GSS': 'E07000169', 'register-code': 'SEL', 'name': 'Selby'},
    '00CG': {'GSS': 'E08000019', 'register-code': 'SHF', 'name': 'Sheffield'},
    '29UL': {'GSS': 'E07000112', 'register-code': 'SHE', 'name': 'Shepway'},
    '00GG': {'GSS': 'E06000051', 'register-code': 'SHR', 'name': 'Shropshire'},
    '00MD': {'GSS': 'E06000039', 'register-code': 'SLG', 'name': 'Slough'},
    '00CT': {'GSS': 'E08000029', 'register-code': 'SOL', 'name': 'Solihull'},
    '5067': {'GSS': 'E07000246', 'register-code': 'SWT', 'name': 'Somerset West and Taunton'},
    '12UG': {'GSS': 'E07000012', 'register-code': 'SCA', 'name': 'South Cambridgeshire'},
    '17UK': {'GSS': 'E07000039', 'register-code': 'SDE', 'name': 'South Derbyshire'},
    '5078': {'GSS': 'E07000044', 'register-code': 'SHA', 'name': 'South Hams'},
    '32UF': {'GSS': 'E07000140', 'register-code': 'SHO', 'name': 'South Holland'},
    '32UG': {'GSS': 'E07000141', 'register-code': 'SKE', 'name': 'South Kesteven'},
    '16UG': {'GSS': 'E07000031', 'register-code': 'SLA', 'name': 'South Lakeland'},
    '5085': {'GSS': 'E07000126', 'register-code': 'SRI', 'name': 'South Ribble'},
    '00CL': {'GSS': 'E08000023', 'register-code': 'STY', 'name': 'South Tyneside'},
    '00MS': {'GSS': 'E06000045', 'register-code': 'STH', 'name': 'Southampton'},
    '00KF': {'GSS': 'E06000033', 'register-code': 'SOS', 'name': 'Southend-on-Sea'},
    '00BE': {'GSS': 'E09000028', 'register-code': 'SWK', 'name': 'Southwark'},
    '5091': {'GSS': 'E07000213', 'register-code': 'SPE', 'name': 'Spelthorne'},
    '26UG': {'GSS': 'E07000100', 'register-code': 'SAL', 'name': 'St Albans'},
    '26UH': {'GSS': 'E07000101', 'register-code': 'STV', 'name': 'Stevenage'},
    '00BS': {'GSS': 'E08000007', 'register-code': 'SKP', 'name': 'Stockport'},
    '00EF': {'GSS': 'E06000004', 'register-code': 'STT', 'name': 'Stockton-on-Tees'},
    '00GL': {'GSS': 'E06000021', 'register-code': 'STE', 'name': 'Stoke-on-Trent'},
    '23UF': {'GSS': 'E07000082', 'register-code': 'STO', 'name': 'Stroud'},
    '5080': {'GSS': 'E08000024', 'register-code': 'SND', 'name': 'Sunderland'},
    '42UG': {'GSS': 'E07000205', 'register-code': 'SUF', 'name': 'Suffolk Coastal'},
    '00HX': {'GSS': 'E06000030', 'register-code': 'SWD', 'name': 'Swindon'},
    '41UK': {'GSS': 'E07000199', 'register-code': 'TAW', 'name': 'Tamworth'},
    '43UK': {'GSS': 'E07000215', 'register-code': 'TAN', 'name': 'Tandridge'},
    '40UE': {'GSS': 'E07000190', 'register-code': 'TAU', 'name': 'Taunton Deane'},
    '18UH': {'GSS': 'E07000045', 'register-code': 'TEI', 'name': 'Teignbridge'},
    '22UN': {'GSS': 'E07000076', 'register-code': 'TEN', 'name': 'Tendring'},
    '29UN': {'GSS': 'E07000114', 'register-code': 'THA', 'name': 'Thanet'},
    '00KG': {'GSS': 'E06000034', 'register-code': 'THR', 'name': 'Thurrock'},
    '29UP': {'GSS': 'E07000115', 'register-code': 'TON', 'name': 'Tonbridge and Malling'},
    '22UQ': {'GSS': 'E07000077', 'register-code': 'UTT', 'name': 'Uttlesford'},
    '00EU': {'GSS': 'E06000007', 'register-code': 'WRT', 'name': 'Warrington'},
    '44UF': {'GSS': 'E07000222', 'register-code': 'WAW', 'name': 'Warwick'},
    '26UK': {'GSS': 'E07000103', 'register-code': 'WAT', 'name': 'Watford'},
    '42UH': {'GSS': 'E07000206', 'register-code': 'WAV', 'name': 'Waveney'},
    '43UL': {'GSS': 'E07000216', 'register-code': 'WAE', 'name': 'Waverley'},
    '21UH': {'GSS': 'E07000065', 'register-code': 'WEA', 'name': 'Wealden'},
    '26UL': {'GSS': 'E07000104', 'register-code': 'WEW', 'name': 'Welwyn Hatfield'},
    '00MB': {'GSS': 'E06000037', 'register-code': 'WBK', 'name': 'West Berkshire'},
    '5077': {'GSS': 'E07000047', 'register-code': 'WDE', 'name': 'West Devon'},
    '30UP': {'GSS': 'E07000127', 'register-code': 'WLA', 'name': 'West Lancashire'},
    '5068': {'GSS': 'E07000245', 'register-code': 'WSK', 'name': 'West Suffolk'},
    '00BW': {'GSS': 'E08000010', 'register-code': 'WGN', 'name': 'Wigan'},
    '00HY': {'GSS': 'E06000054', 'register-code': 'WIL', 'name': 'Wiltshire'},
    '24UP': {'GSS': 'E07000094', 'register-code': 'WIN', 'name': 'Winchester'},
    '00CB': {'GSS': 'E08000015', 'register-code': 'WRL', 'name': 'Wirral'},
    '43UM': {'GSS': 'E07000217', 'register-code': 'WOI', 'name': 'Woking'},
    '00MF': {'GSS': 'E06000041', 'register-code': 'WOK', 'name': 'Wokingham'},
    '00CW': {'GSS': 'E08000031', 'register-code': 'WLV', 'name': 'Wolverhampton'},
    '11UF': {'GSS': 'E07000007', 'register-code': 'WYO', 'name': 'Wycombe'},
}
