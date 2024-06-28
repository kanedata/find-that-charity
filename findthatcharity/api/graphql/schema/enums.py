import graphene


class DistanceUnit(graphene.Enum):
    mi = "mi"
    yd = "yd"
    km = "km"
    m = "m"


class GeoRegion(graphene.Enum):
    E12000001 = "E12000001"
    E12000002 = "E12000002"
    E12000003 = "E12000003"
    E12000004 = "E12000004"
    E12000005 = "E12000005"
    E12000006 = "E12000006"
    E12000007 = "E12000007"
    E12000008 = "E12000008"
    E12000009 = "E12000009"
    W99999999 = "W99999999"


class GeoCountry(graphene.Enum):
    E92000001 = "E92000001"  # England
    N92000002 = "N92000002"  # Northern Ireland
    S92000003 = "S92000003"  # Scotland
    W92000004 = "W92000004"  # Wales


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
