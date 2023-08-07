import graphene


class DistanceUnit(graphene.Enum):
    mi = "mi"
    yd = "yd"
    km = "km"
    m = "m"


class GeoRegion(graphene.Enum):
    # North East
    E12000001 = "E12000001"
    # North West
    E12000002 = "E12000002"
    # Yorkshire and The Humber
    E12000003 = "E12000003"
    # East Midlands
    E12000004 = "E12000004"
    # West Midlands
    E12000005 = "E12000005"
    # East of England
    E12000006 = "E12000006"
    # London
    E12000007 = "E12000007"
    # South East
    E12000008 = "E12000008"
    # South West
    E12000009 = "E12000009"
    # Wales (Pseudo)
    W99999999 = "W99999999"


class GeoCountry(graphene.Enum):
    # England
    E92000001 = "E92000001"
    # Northern Ireland
    N92000002 = "N92000002"
    # Scotland
    S92000003 = "S92000003"
    # Wales
    W92000004 = "W92000004"


class SortCHC(graphene.Enum):
    age_asc = "age_asc"
    age_desc = "age_desc"
    default = "default"
    income_asc = "income_asc"
    income_desc = "income_desc"
    random = "random"
    spending_asc = "spending_asc"
    spending_desc = "spending_desc"


class SocialPlatform(graphene.Enum):
    facebook = "facebook"
    instagram = "instagram"
    twitter = "twitter"


class PageLimit(graphene.Int):
    pass
