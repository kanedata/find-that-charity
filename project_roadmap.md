# About findthatcharity

[Website](https://findthatcharity.uk/) | 
[Github](https://github.com/drkane/find-that-charity) |
[David Kane](https://drkane.co.uk/) |
[360Giving](https://www.threesixtygiving.org/)

_Last updated: 2018-10-12 16:23:16_

## 1. What problem are we trying to solve?

Find that charity is a database and website that aims to solve a particular problem: how do you find an identifier for a UK non-profit organisation when you only know the name?

### Identifying organisations

Identifying an organisation is tricky, especially when you have lots of them. Names are often recorded inconsistently - a computer won't know that `Alzhiemer's Society` and `Alzhiemers Society` and `Alzhiemer's Soc` all refer to the same entity. The same organisation might go by different names, such as trading names - the charity that trades as `Comic Relief` and `Sport Relief` actually has the registered name `Charity Projects`. And even if the names are identical the charity might be different - there are 171 active registered charities called `Village Hall`, how do you tell them apart.

### Identifiers

The solution is to use organisation "identifiers". These are unique pieces of text that unambiguously identify an organisation, unconnected to the name. An example of an identifier outside of this context is National Insurance numbers. Everyone working in the UK has a National Insurance number, and using it means that your employer, the government, etc can be sure they are talking about the same person, no matter if the name is mispelled, or a common name shared with other people.

### Consistency

An additional problem is that one organisation might have different identifiers depending on the context. A registered charity, for example, will often also be a registered company and thus have a company number and a charity number. 


Find that charity aims to solve the problem of matching organisations to their identifiers, and finding a consistent identifier for one organisation.

## 2. Who is findthatcharity aimed at?

The intended audience for findthatcharity is people in the UK who want to solve the problem above. Examples of this include:

- People working at grant-making organisations who are intending to publish to the [360Giving data standard](http://standard.threesixtygiving.org/en/latest/#). A requirement of the standard is that published data will contain identifiers for the recipient and funder organisations included in the data. If the publisher does not have existing identifiers they can use findthatcharity to add them to their data. This will help to avoid duplications in the data. 

- Data analysts hoping to use data about non-profit organisations. With a list of charities/non-profit organisations, an analyst could use findthatcharity to add organisation identifiers to the list, and then use the identifiers to add data about the organisations (for example show the type of organisation, their latest income, their postcode, etc). 

## 3. What does findthatcharity do?

Findthatcharity consists of four parts:

- A **database** - currently powered by [elasticsearch](https://www.elastic.co/products/elasticsearch). The database aims to bring together registers of non-profit organisations in one place, and crucially link between them, so you can tell when a record for a charity refers to the same organisations as a company. It's important to note that this database doesn't aim to *be* the register of these organisations - those are still held by the regulators of these organisations. But it does aim to bring together a single copy (or *cache*) of these registers, a snapshot at a particular point in time.

- A set of **web scrapers** designed to find data on non-profit organisations from publicly available registers and transform these organisations records into a common format so they can be cached in the database. The common format is based on the `Organization` element of the [360Giving data standard](http://standard.threesixtygiving.org/en/latest/#). [The web scrapers are maintained in a separate repository](https://github.com/drkane/find-that-charity-scrapers).

- An **API** for programmatically accessing data about these organisations, either individually or in bulk. A crucial part of this is an implementation of the [OpenRefine reconciliation API](https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API), which allows users of OpenRefine (an open source data toolkit), to "reconcile" a list of organisation names to their identifiers. 

- A set of **web tools** for using the data. These tools are hosted on <https://findthatcharity.uk/>, and currently include:

   - A search engine available on the [front page of findthatcharity](https://findthatcharity.uk/)
   - A page for every organisation stored in the database, exposing details about that organisation
   - A tool to add data to a CSV containing charity/organisation identifiers: <https://findthatcharity.uk/adddata>
   - A link that redirects to a random charity: <https://findthatcharity.uk/random?active=true>

A crucial part of findthatcharity is the identifiers, which are constructed according to the [org-id scheme](http://org-id.guide/), maintained by [Open Data Services Co-operative](http://opendataservices.coop/). The idea behind org-id is to construct an identifier for an organisation using the identifiers from existing registers of organisations, matched with a prefix unique to that register. A charity with the charity registration number `123456` would have a prefix `GB-CHC-`, to create an org-id of `GB-CHC-123456`. This would enable this organisation to be distinguished from a company with company registration number `123456`, which would instead be shown as `GB-COH-123456`.

## 4. How does it fit with 360Giving?

Findthatcharity started as a personal project of [David Kane](https://drkane.co.uk/), whilst he worked at [Cast](https://wearecast.org.uk/).

The project is very relevant to the 360Giving initiative, and has hopefully proven useful for 360Giving users, such as publishers trying to find organisation identifiers. 360Giving currently pay for the hosting of the site, and some development time for the site through a contract with David Kane.

## 5. What are the alternative products? Why use findthatcharity?

There are competing/complimentary products operating in this space:

- **government registers of organisations** - these are the primary data sources for findthatcharity, and should be treated as the source of truth for these organisations. Findthatcharity merely collates and builds on top of this information (under the licensing terms used by the other registers, normally the [Open Government Licence](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)). An example might be the [Charity Commission register of charities](http://beta.charitycommission.gov.uk/) ([data download](http://data.charitycommission.gov.uk/)).
- **[OpenCorporates](https://opencorporates.com/)** - aims to provide a record for every company in the world. Does include charities and other organisations covered by findthatcharity.
- **[CharityBase](https://charitybase.uk/)** - focussing on registered charities, producing an API and front-end based on the Charity Commission register of charities.
- **[CharityData](https://olib.uk/charity/html/)** - another site using the Charity Commission register of charities.
- **[Org-ID register](http://org-id.guide/)** - a directory of possible org-id prefixes and registers of organisations to use.

Findthatcharity's unique place in this ecosystem is based on a number of factors:

- Focus on UK non-profit organisations (wider than charities)
- Focus on doing one thing well - matching a name to an organisation
- Building tools around the data to help with specific problems/tasks

## 6. Roadmap

The [current alpha version](https://github.com/drkane/find-that-charity/releases/tag/v0.1) of findthatcharity focuses on organisations registered with the UK's three main charity regulators - the Charity Commission for England and Wales, the Scottish Charity Regulator and the Charity Commission for Northern Ireland. It produces a search engine for these organisations, with a reconciliation API for use with OpenRefine, and a proof-of-concept tool for adding data to a CSV. The alpha version was launched in 2017. 

### 5.1 Beta version

The next stage is to move the tool to a beta version. This builds on the concept of the alpha version to improve the usefulness and reliability of the tools. Improvements targeted for [this release](https://github.com/drkane/find-that-charity/milestone/1) include:

- Moving from only looking at charities to include a range of non-profit organisation types, based on the [org-id register](http://org-id.guide/results?structure=all&coverage=GB&sector=all).
- Move data scrapers to a separate repository, to improve maintainability. The new [find-that-charity-scrapers repository](https://github.com/drkane/find-that-charity-scrapers) has been created, and the scrapers have been rewritten to use the [scrapy](https://scrapy.org/) library.
- Improve branding, licencing and look and feel of the site.
- Ensure tools and API are robust enough for public use.

### 5.2 Future expansion

After the beta version is completed, the roadmap for the future of findthatcharity includes plans for the following:

- Increasing the number of data sources. A [list of potential data sources](https://github.com/drkane/find-that-charity-scrapers/issues?q=is%3Aissue+is%3Aopen+label%3A%22data+source%22) is maintained in the find-that-charity-scrapers repository.
- Adding a tool to allow users to reconcile a list of organisations on the site, without needing to install OpenRefine.
- Allowing user input to improve the data. For example, the reconciliation process could result in additional alternative names that could be saved against an organisation record, allowing better matching of those records in the future.

[Potential site enhancements are stored as github issues](https://github.com/drkane/find-that-charity/issues?q=is%3Aopen+is%3Aissue+no%3Amilestone).
