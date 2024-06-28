WITH name_base AS (
    SELECT
        organisation_number,
        jsonb_build_object('value', charity_name, 'primary', TRUE) AS "name"
    FROM
        charity_ccewcharity
    UNION
    ALL
    SELECT
        organisation_number,
        jsonb_build_object('value', charity_name, 'primary', FALSE) AS "name"
    FROM
        charity_ccewcharityothernames
),
names AS (
    SELECT
        name_base.organisation_number,
        jsonb_agg(name_base."name") AS "names"
    FROM
        name_base
    GROUP BY
        1
),
finances AS (
    SELECT
        ar.organisation_number,
        jsonb_agg(
            jsonb_build_object(
                'income',
                ar.total_gross_income,
                'spending',
                ar.total_gross_expenditure,
                'financial_year',
                jsonb_build_object(
                    'begin',
                    ar.fin_period_start_date,
                    'end',
                    ar.fin_period_end_date
                )
            )
            ORDER BY
                fin_period_end_date DESC
        ) AS finances
    FROM
        charity_ccewcharityannualreturnhistory ar
    GROUP BY
        1
),
cl AS (
    SELECT
        organisation_number,
        jsonb_agg(classification_code::text) FILTER (
            WHERE
                classification_type = 'What'
        ) AS causes,
        jsonb_agg(classification_code:: text) FILTER (
            WHERE
                classification_type = 'Who'
        ) AS beneficiaries,
        jsonb_agg(classification_code:: text) FILTER (
            WHERE
                classification_type = 'How'
        ) AS operations
    FROM
        charity_ccewcharityclassification cc
    GROUP BY
        1
),
social_base AS (
    SELECT
        replace(org_id, 'GB-CHC-', '') :: int AS registered_charity_number,
        jsonb_array_elements(
            jsonb_build_array(
                CASE
                    WHEN twitter IS NOT NULL THEN jsonb_build_object('platform', 'twitter', 'handle', twitter)
                    ELSE jsonb_build_object('platform', NULL, 'handle', NULL)
                END,
                CASE
                    WHEN facebook IS NOT NULL THEN jsonb_build_object('platform', 'facebook', 'handle', facebook)
                    ELSE jsonb_build_object('platform', NULL, 'handle', NULL)
                END
            )
        ) AS social
    FROM
        other_data_wikidataitem odw
    WHERE
        org_id ~* 'GB-CHC-[0-9]{6,7}'
        AND (
            twitter IS NOT NULL
            OR facebook IS NOT NULL
        )
),
social AS (
    SELECT
        registered_charity_number,
        jsonb_agg(social_base.social) AS social
    FROM
        social_base
    WHERE
        social_base.social ->> 'platform' IS NOT NULL
    GROUP BY
        1
),
trustee_base AS (
    SELECT
        t1.organisation_number,
        t1.trustee_id AS id,
        t1.trustee_name AS name,
        count(t2.id) AS trusteeships,
        CASE
            WHEN count(t2.id) > 0 THEN array_agg(
                jsonb_build_object(
                    'id',
                    t2.registered_charity_number,
                    'name',
                    cc.charity_name
                )
            )
            ELSE ARRAY [] :: jsonb []
        END AS other_charities
    FROM
        charity_ccewcharitytrustee t1
        LEFT OUTER JOIN charity_ccewcharitytrustee t2 ON t1.trustee_id = t2.trustee_id
        AND t1.organisation_number != t2.organisation_number
        LEFT OUTER JOIN charity_ccewcharity cc ON t2.organisation_number = cc.organisation_number
    GROUP BY
        1,
        2,
        3
),
trustees AS (
    SELECT
        organisation_number,
        array_agg(
            jsonb_build_object(
                'id',
                trustee_base.id,
                'name',
                trustee_base.name,
                'trusteeships',
                trustee_base.trusteeships,
                'other_charities',
                trustee_base.other_charities
            )
        ) AS trustees,
        count(*) AS trustee_count
    FROM
        trustee_base
    GROUP BY
        1
),
people AS (
    SELECT
        pa.organisation_number,
        pa.count_volunteers AS volunteers,
        pb.count_employees AS employees
    FROM
        charity_ccewcharityarparta pa
        LEFT OUTER JOIN charity_ccewcharityarpartb pb ON pa.organisation_number = pb.organisation_number
        AND pa.fin_period_end_date = pb.fin_period_end_date
    WHERE
        pa.latest_fin_period_submitted_ind
),
grants AS (
    SELECT
        c.organisation_number,
        array_agg(
            jsonb_build_object(
                'id',
                g.grant_id,
                'title',
                g.title,
                'description',
                g.description,
                'funder',
                jsonb_build_object(
                    'id',
                    g."fundingOrganization_id",
                    'name',
                    g."fundingOrganization_name"
                ),
                'amount_awarded',
                g."amountAwarded",
                'currency',
                g.currency,
                'award_date',
                g."awardDate"
            )
        ) AS grants,
        JSONB_AGG(
            DISTINCT jsonb_build_object(
                'id',
                g."fundingOrganization_id",
                'name',
                g."fundingOrganization_name"
            )
        ) AS funders
    FROM
        charity_ccewcharity c
        INNER JOIN other_data_grant g ON g."recipientOrganization_id" = concat(
            'GB-COH-',
            COALESCE(
                c.charity_company_registration_number,
                'XXX|ZZZZ'
            )
        )
        OR g."recipientOrganization_id" = concat('GB-CHC-', c.registered_charity_number)
    WHERE
        c.linked_charity_number = 0
    GROUP BY
        1
),
areas AS (
    SELECT
        organisation_number,
        jsonb_agg(
            jsonb_build_object(
                'id',
                coalesce(
                    aoo2."GSS",
                    aoo2."ISO3166_1",
                    aoo1.geographic_area_description
                ),
                'name',
                aoo1.geographic_area_description
            )
        ) AS areas
    FROM
        charity_ccewcharityareaofoperation aoo1
        LEFT OUTER JOIN charity_areaofoperation aoo2 ON aoo1.geographic_area_description = aoo2.aooname
    GROUP BY
        1
),
geo AS (
    SELECT
        c.organisation_number,
        jsonb_build_object(
            'postcode',
            c.charity_contact_postcode,
            'quality',
            NULL,
            'eastings',
            g.oseast1m,
            'northings',
            g.osnrth1m,
            'country',
            ctry.name,
            'nhs_ha',
            NULL,
            'longitude',
            g.long,
            'latitude',
            g.lat,
            'european_electoral_region',
            NULL,
            'primary_care_trust',
            NULL,
            'region',
            rgn.name,
            'lsoa',
            g.lsoa21,
            'msoa',
            g.msoa21,
            'incode',
            trim(right(g.pcd2, 3)),
            'outcode',
            trim(LEFT(g.pcd2, 4)),
            'parliamentary_constituency',
            pcon.name,
            'admin_district',
            district.name,
            'parish',
            NULL,
            'admin_county',
            county.name,
            'admin_ward',
            ward.name,
            'ced',
            NULL,
            'ccg',
            NULL,
            'nuts',
            NULL,
            'codes',
            jsonb_build_object(
                'admin_district',
                g.laua,
                'admin_county',
                g.cty,
                'admin_ward',
                g.ward,
                'parish',
                NULL,
                'parliamentary_constituency',
                g.pcon,
                'ccg',
                NULL,
                'ced',
                NULL,
                'nuts',
                NULL
            )
        ) AS geo
    FROM
        charity_ccewcharity c
        INNER JOIN geo_postcode g ON c.charity_contact_postcode = g.pcds
        LEFT OUTER JOIN geo_geolookup ward ON g.ward = ward."geoCode"
        LEFT OUTER JOIN geo_geolookup district ON g.laua = district."geoCode"
        LEFT OUTER JOIN geo_geolookup county ON g.cty = county."geoCode"
        LEFT OUTER JOIN geo_geolookup pcon ON g.pcon = pcon."geoCode"
        LEFT OUTER JOIN geo_geolookup rgn ON g.rgn = rgn."geoCode"
        LEFT OUTER JOIN geo_geolookup ctry ON g.ctry = ctry."geoCode"
)
SELECT
    cc.registered_charity_number AS id,
    'ccew' AS "source",
    cc.charity_registration_status = 'Registered' AS active,
    jsonb_build_object(
        'id',
        cc.registered_charity_number,
        'name',
        cc.charity_name,
        'names',
        names.names,
        'activities',
        cc.charity_activities,
        'finances',
        finances.finances,
        'areas',
        areas.areas,
        'area_of_benefit',
        gd.area_of_benefit,
        'causes',
        cl.causes,
        'beneficiaries',
        cl.beneficiaries,
        'operations',
        cl.operations,
        'funding',
        jsonb_build_object(
            'funders',
            grants.funders,
            'grants',
            grants.grants
        ),
        'geo',
        geo.geo,
        'contact',
        jsonb_build_object(
            'address',
            array_remove(
                ARRAY [
				cc.charity_contact_address1,
				cc.charity_contact_address2,
				cc.charity_contact_address3,
				cc.charity_contact_address4,
				cc.charity_contact_address5
			],
                NULL
            ),
            'email',
            cc.charity_contact_email,
            'phone',
            cc.charity_contact_phone,
            'postcode',
            cc.charity_contact_postcode,
            'socal',
            social.social
        ),
        'website',
        cc.charity_contact_web,
        'trustees',
        trustees.trustees,
        'governing_doc',
        gd.governing_document_description,
        'objectives',
        gd.charitable_objects,
        'num_people',
        jsonb_build_object(
            'employees',
            people.employees,
            'trustees',
            trustees.trustee_count,
            'volunteers',
            people.volunteers
        ),
        'org_ids',
        array [
			jsonb_build_object('scheme', 'GB-CHC', 'raw_id', cc.registered_charity_number::text)
		] || CASE
            WHEN cc.charity_company_registration_number IS NOT NULL THEN array [
			jsonb_build_object('scheme', 'GB-COH', 'raw_id', cc.charity_company_registration_number)
		]
            ELSE array [] :: jsonb []
        END,
        'financial_year_end',
        cc.latest_acc_fin_period_end_date,
        'registrations',
        jsonb_build_array(
            jsonb_build_object(
                'registration_date',
                cc.date_of_registration,
                'removal_date',
                cc.date_of_removal,
                'removal_code',
                NULL,
                'removal_reason',
                NULL
            )
        ),
        'image',
        NULL,
        'topics',
        jsonb_build_array()
    ) AS "data"
FROM
    charity_ccewcharity cc
    LEFT OUTER JOIN names ON cc.organisation_number = names.organisation_number
    LEFT OUTER JOIN finances ON cc.organisation_number = finances.organisation_number
    LEFT OUTER JOIN charity_ccewcharitygoverningdocument gd ON cc.organisation_number = gd.organisation_number
    LEFT OUTER JOIN cl ON cc.organisation_number = cl.organisation_number
    LEFT OUTER JOIN social ON cc.registered_charity_number = social.registered_charity_number
    LEFT OUTER JOIN trustees ON cc.organisation_number = trustees.organisation_number
    LEFT OUTER JOIN people ON cc.organisation_number = people.organisation_number
    LEFT OUTER JOIN grants ON cc.organisation_number = grants.organisation_number
    LEFT OUTER JOIN areas ON cc.organisation_number = areas.organisation_number
    LEFT OUTER JOIN geo ON cc.organisation_number = geo.organisation_number
WHERE
    cc.linked_charity_number = 0
ORDER BY
    cc.registered_charity_number ASC