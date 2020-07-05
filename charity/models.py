from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.text import slugify

from ftc.models import Scrape


class Charity(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200, db_index=True)
    constitution = models.TextField(null=True, blank=True)
    geographical_spread = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    postcode = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    active = models.BooleanField(db_index=True)
    date_registered = models.DateField(null=True, blank=True, db_index=True)
    date_removed = models.DateField(null=True, blank=True, db_index=True)
    removal_reason = models.CharField(max_length=200, null=True, blank=True)
    web = models.URLField(null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    company_number = models.CharField(max_length=200, null=True, blank=True)
    activities = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    first_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    income = models.BigIntegerField(null=True, blank=True, db_index=True)
    spending = models.BigIntegerField(null=True, blank=True)
    latest_fye = models.DateField(null=True, blank=True)
    dual_registered = models.BooleanField(null=True, blank=True)
    
    areas_of_operation = models.ManyToManyField('AreaOfOperation')
    classification = models.ManyToManyField('VocabularyEntries')

    class Meta:
        verbose_name_plural = 'Charities'

    def __str__(self):
        return "{} [{}]".format(self.name, self.id)


class CharityName(models.Model):
    charity = models.ForeignKey(
        'Charity',
        on_delete=models.CASCADE,
        related_name='other_names'
    )
    name = models.CharField(max_length=200, db_index=True)
    normalisedName = models.CharField(max_length=200, db_index=True, blank=True, null=True)
    name_type = models.CharField(max_length=200, db_index=True)

    class Meta:
        unique_together = ('charity', 'name',)

    def __str__(self):
        return "{} [{}]".format(self.name, self.charity.id)


class CharityFinancial(models.Model):

    class AccountType(models.TextChoices):
        BASIC = 'basic', 'Basic'
        CONSOLIDATED = 'consolidated', 'Consolidated'
        CHARITY = 'charity', 'Charity'

    charity = models.ForeignKey(
        'Charity',
        on_delete=models.CASCADE,
        related_name='financial'
    )
    fyend = models.DateField(db_index=True)
    fystart = models.DateField(null=True, blank=True)
    income = models.BigIntegerField(null=True, blank=True)
    spending = models.BigIntegerField(null=True, blank=True)
    inc_leg = models.BigIntegerField(null=True, blank=True)
    inc_end = models.BigIntegerField(null=True, blank=True)
    inc_vol = models.BigIntegerField(null=True, blank=True)
    inc_fr = models.BigIntegerField(null=True, blank=True)
    inc_char = models.BigIntegerField(null=True, blank=True)
    inc_invest = models.BigIntegerField(null=True, blank=True)
    inc_other = models.BigIntegerField(null=True, blank=True)
    inc_total = models.BigIntegerField(null=True, blank=True)
    invest_gain = models.BigIntegerField(null=True, blank=True)
    asset_gain = models.BigIntegerField(null=True, blank=True)
    pension_gain = models.BigIntegerField(null=True, blank=True)
    exp_vol = models.BigIntegerField(null=True, blank=True)
    exp_trade = models.BigIntegerField(null=True, blank=True)
    exp_invest = models.BigIntegerField(null=True, blank=True)
    exp_grant = models.BigIntegerField(null=True, blank=True)
    exp_charble = models.BigIntegerField(null=True, blank=True)
    exp_gov = models.BigIntegerField(null=True, blank=True)
    exp_other = models.BigIntegerField(null=True, blank=True)
    exp_total = models.BigIntegerField(null=True, blank=True)
    exp_support = models.BigIntegerField(null=True, blank=True)
    exp_dep = models.BigIntegerField(null=True, blank=True)
    reserves = models.BigIntegerField(null=True, blank=True)
    asset_open = models.BigIntegerField(null=True, blank=True)
    asset_close = models.BigIntegerField(null=True, blank=True)
    fixed_assets = models.BigIntegerField(null=True, blank=True)
    open_assets = models.BigIntegerField(null=True, blank=True)
    invest_assets = models.BigIntegerField(null=True, blank=True)
    cash_assets = models.BigIntegerField(null=True, blank=True)
    current_assets = models.BigIntegerField(null=True, blank=True)
    credit_1 = models.BigIntegerField(null=True, blank=True)
    credit_long = models.BigIntegerField(null=True, blank=True)
    pension_assets = models.BigIntegerField(null=True, blank=True)
    total_assets = models.BigIntegerField(null=True, blank=True)
    funds_end = models.BigIntegerField(null=True, blank=True)
    funds_restrict = models.BigIntegerField(null=True, blank=True)
    funds_unrestrict = models.BigIntegerField(null=True, blank=True)
    funds_total = models.BigIntegerField(null=True, blank=True)
    employees = models.BigIntegerField(null=True, blank=True)
    volunteers = models.BigIntegerField(null=True, blank=True)
    account_type = models.CharField(
        max_length=50, default=AccountType.BASIC, choices=AccountType.choices)

    class Meta:
        unique_together = ('charity', 'fyend',)

    def __str__(self):
        return "{} {}".format(self.charity.name, self.fyend)

class CharityRaw(models.Model):
    org_id = models.CharField(max_length=200, db_index=True)
    spider = models.CharField(max_length=200, db_index=True)
    scrape = models.ForeignKey(
        'ftc.Scrape',
        on_delete=models.CASCADE,
    )
    data = JSONField(
        encoder=DjangoJSONEncoder
    )

    class Meta:
        verbose_name = 'Raw charity data'
        verbose_name_plural = 'Raw charity data'

    def __str__(self):
        return "{} {}".format(self.spider, self.org_id)

class AreaOfOperation(models.Model):
    aootype = models.CharField(max_length=1)
    aookey = models.IntegerField()
    aooname = models.CharField(max_length=200, db_index=True)
    aoosort = models.CharField(max_length=200, db_index=True)
    welsh = models.BooleanField(verbose_name="In Wales")
    master = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name="Parent area", null=True, blank=True)
    GSS = models.CharField(verbose_name="ONS Geocode for Local Authority", max_length=10, null=True, blank=True, db_index=True)
    ISO3166_1 = models.CharField(verbose_name="ISO3166-1 country code (2 character)", max_length=2, null=True, blank=True, db_index=True)
    ISO3166_1_3 = models.CharField(verbose_name="ISO3166-1 country code (3 character)", max_length=3, null=True, blank=True, db_index=True)
    ISO3166_2_GB = models.CharField(verbose_name="ISO3166-2 region code (GB only)", max_length=6, null=True, blank=True, db_index=True)
    ContinentCode = models.CharField(verbose_name="Continent", max_length=2, null=True, blank=True, db_index=True)
    
    class Meta:
        unique_together = ('aootype', 'aookey',)
        verbose_name = 'Area of operation'
        verbose_name_plural = 'Areas of operation'

    def __str__(self):
        return "{}-{} {}".format(self.aootype, self.aookey, self.aooname)


class Vocabulary(models.Model):
    title = models.CharField(max_length=200, db_index=True, unique=True)
    single = models.BooleanField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Vocabulary'
        verbose_name_plural = 'Vocabularies'


class VocabularyEntries(models.Model):
    vocabulary = models.ForeignKey(
        'Vocabulary',
        on_delete=models.CASCADE,
        related_name='entries'
    )
    code = models.CharField(max_length=500, db_index=True)
    title = models.CharField(max_length=500, db_index=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ('vocabulary', 'code',)
        verbose_name = 'Vocabulary Entry'
        verbose_name_plural = 'Vocabulary Entries'

    def __str__(self):
        if slugify(self.title) == slugify(self.code):
            return self.title
        return "[{}] {}".format(self.code, self.title)

class CcewDataFile(models.Model):
    title = models.CharField(max_length=500, db_index=True, unique=True)
    url = models.URLField()
    description = models.CharField(max_length=500, db_index=True)
    first_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Charity Commission data file: {}".format(self.title)

    def get_absolute_url(self):
        return self.url

    class Meta:
        verbose_name = 'Charity Commission data file'
        verbose_name_plural = 'Charity Commission data files'
        

class CCEWCharity(models.Model):
    regno = models.CharField(db_index=True, max_length=255)  #	     integer 	    registered number of a charity
    # integer 	    subsidiary number of a charity (may be 0 for main/group charity)
    subno = models.IntegerField(db_index=True)
    # varchar(150) 	main name of the charity
    name = models.CharField(max_length=255, null=True, blank=True)
    # varchar(2) 	R (registered) or RM (removed)
    orgtype = models.CharField(max_length=255, null=True, blank=True)
    # varchar(250) 	Description of Governing Document
    gd = models.TextField(null=True, blank=True)
    # varchar(175) 	area of benefit - may not be defined
    aob = models.TextField(null=True, blank=True)
    # char(1) 	    area of benefit defined by Governing Document (T/F)
    aob_defined = models.CharField(max_length=255, null=True, blank=True)
    # char(1) 	    NHS charity (T/F)
    nhs = models.CharField(max_length=255, null=True, blank=True)
    # varchar(20) 	Housing Association number
    ha_no = models.CharField(max_length=255, null=True, blank=True)
    corr = models.CharField(max_length=255, null=True, blank=True)  #	     varchar(70) 	Charity correspondent name
    add1 = models.CharField(max_length=255, null=True, blank=True)  #	     varchar(35) 	address line of charity's correspondent
    add2 = models.CharField(max_length=255, null=True, blank=True)  #	     varchar(35) 	address line of charity's correspondent
    add3 = models.CharField(max_length=255, null=True, blank=True)  #	     varchar(35) 	address line of charity's correspondent
    add4 = models.CharField(max_length=255, null=True, blank=True)  #	     varchar(35) 	address line of charity's correspondent
    add5 = models.CharField(max_length=255, null=True, blank=True)  #	     varchar(35) 	address line of charity's correspondent
    # varchar(8) 	postcode of charity's correspondent
    postcode = models.CharField(max_length=255, null=True, blank=True)
    # varchar(23) 	telephone of charity's correspondent
    phone = models.CharField(max_length=255, null=True, blank=True)
    # varchar(23) 	fax of charity's correspondent
    fax = models.CharField(max_length=255, null=True, blank=True)


class CCEWMainCharity(models.Model):
    # integer 	    registered number of a charity
    regno = models.CharField(db_index=True, max_length=255)
    # integer 	    company registration number
    coyno = models.CharField(max_length=255, null=True, blank=True)
    # char(1) 	    trustees incorporated (T/F)
    trustees = models.CharField(max_length=255, null=True, blank=True)
    # char(4) 	    Financial year end
    fyend = models.CharField(max_length=255, null=True, blank=True)
    # char(1) 	    requires correspondence in both Welsh & English (T/F)
    welsh = models.CharField(max_length=255, null=True, blank=True)
    # datetime 	    date for latest gross income (blank if income is an estimate)
    incomedate = models.DateField(null=True, blank=True)
    income = models.BigIntegerField(null=True, blank=True)  # integer
    # varchar(4) 	    may be blank
    grouptype = models.CharField(max_length=255, null=True, blank=True)
    # varchar(255) 	email address
    email = models.CharField(max_length=255, null=True, blank=True)
    # varchar(255) 	website address
    web = models.CharField(max_length=255, null=True, blank=True)


class CCEWName(models.Model):
    # integer 	    registered number of a charity
    regno = models.CharField(db_index=True, max_length=255)
    # integer 	    subsidiary number of a charity (may be 0 for main/group charity)
    subno = models.IntegerField(db_index=True)
    nameno = models.IntegerField()  # integer 	    number identifying a charity name
    name = models.CharField(max_length=255)   #     varchar(150) 	name of a charity (multiple occurrences possible)


class CCEWRegistration(models.Model):
    # integer 	    registered number of a charity
    regno = models.CharField(db_index=True, max_length=255)
    # integer 	    subsidiary number of a charity (may be 0 for main/group charity)
    subno = models.IntegerField(db_index=True)
    regdate = models.DateField() #    datetime 	    date of registration for a charity
    # datetime 	    Removal date of a charity - Blank for Registered Charities
    remdate = models.DateField(null=True, blank=True)
    # varchar(3) 	    Register removal reason code
    remcode = models.CharField(max_length=255, null=True, blank=True)


class CCEWCharityAOO(models.Model):
    # integer 	    registered number of a charity
    regno = models.CharField(db_index=True, max_length=255)
    aootype = models.CharField(max_length=255) # 	    char(1) 	    A B or D
    aookey = models.IntegerField() # 	    integer 	    up to three digits
    # char(1) 	    Flag: Y or blank
    welsh = models.CharField(max_length=255, null=True, blank=True)
    # integer 	    may be blank. If aootype=D then holds continent; if aootype=B then holds GLA/met county
    master = models.IntegerField(null=True, blank=True)


class CCEWObjects(models.Model):
    # integer 	    registered number of a charity
    regno = models.CharField(db_index=True, max_length=255)
    # integer 	    subsidiary number of a charity (may be 0 for main/group charity)
    subno = models.IntegerField(db_index=True)
    # char(4) 	    sequence number (in practice 0-20)
    seqno = models.CharField(db_index=True, max_length=255)
    # varchar(255) 	Description of objects of a charity
    object_text = models.TextField(db_column='object')


class CCEWFinancial(models.Model):
    # integer 	registered number of a charity
    regno = models.CharField(db_index=True, max_length=255)
    fystart = models.DateField() # 	datetime 	Charity's financial year start date
    # datetime 	Charity's financial year end date
    fyend = models.DateField(db_index=True)
    income = models.BigIntegerField(null=True, blank=True) # 	integer 	
    expend = models.BigIntegerField(null=True, blank=True)  # integer


class CCEWClass(models.Model):
    # integer 	registered number of a charity
    regno = models.CharField(db_index=True, max_length=255)
    # integer 	classification code for a charity(multiple occurrences possible)
    classification = models.CharField(db_column='class', max_length=255)


class CCEWPartB(models.Model):
    regno = models.CharField(db_index=True, max_length=255)
    artype = models.CharField(max_length=255)
    fystart = models.DateField()
    fyend = models.DateField(db_index=True)
    inc_leg = models.BigIntegerField(null=True, blank=True)
    inc_end = models.BigIntegerField(null=True, blank=True)
    inc_vol = models.BigIntegerField(null=True, blank=True)
    inc_fr = models.BigIntegerField(null=True, blank=True)
    inc_char = models.BigIntegerField(null=True, blank=True)
    inc_invest = models.BigIntegerField(null=True, blank=True)
    inc_other = models.BigIntegerField(null=True, blank=True)
    inc_total = models.BigIntegerField(null=True, blank=True)
    invest_gain = models.BigIntegerField(null=True, blank=True)
    asset_gain = models.BigIntegerField(null=True, blank=True)
    pension_gain = models.BigIntegerField(null=True, blank=True)
    exp_vol = models.BigIntegerField(null=True, blank=True)
    exp_trade = models.BigIntegerField(null=True, blank=True)
    exp_invest = models.BigIntegerField(null=True, blank=True)
    exp_grant = models.BigIntegerField(null=True, blank=True)
    exp_charble = models.BigIntegerField(null=True, blank=True)
    exp_gov = models.BigIntegerField(null=True, blank=True)
    exp_other = models.BigIntegerField(null=True, blank=True)
    exp_total = models.BigIntegerField(null=True, blank=True)
    exp_support = models.BigIntegerField(null=True, blank=True)
    exp_dep = models.BigIntegerField(null=True, blank=True)
    reserves = models.BigIntegerField(null=True, blank=True)
    asset_open = models.BigIntegerField(null=True, blank=True)
    asset_close = models.BigIntegerField(null=True, blank=True)
    fixed_assets = models.BigIntegerField(null=True, blank=True)
    open_assets = models.BigIntegerField(null=True, blank=True)
    invest_assets = models.BigIntegerField(null=True, blank=True)
    cash_assets = models.BigIntegerField(null=True, blank=True)
    current_assets = models.BigIntegerField(null=True, blank=True)
    credit_1 = models.BigIntegerField(null=True, blank=True)
    credit_long = models.BigIntegerField(null=True, blank=True)
    pension_assets = models.BigIntegerField(null=True, blank=True)
    total_assets = models.BigIntegerField(null=True, blank=True)
    funds_end = models.BigIntegerField(null=True, blank=True)
    funds_restrict = models.BigIntegerField(null=True, blank=True)
    funds_unrestrict = models.BigIntegerField(null=True, blank=True)
    funds_total = models.BigIntegerField(null=True, blank=True)
    employees = models.BigIntegerField(null=True, blank=True)
    volunteers = models.BigIntegerField(null=True, blank=True)
    cons_acc = models.CharField(max_length=255, null=True, blank=True)
    charity_acc = models.CharField(max_length=255, null=True, blank=True)
