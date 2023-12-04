python ./manage.py import_all
python ./manage.py import_charities
python ./manage.py import_ch
python ./manage.py update_geodata
python ./manage.py es_index
python manage.py output_ccew --upload-to-storage --geo-field geo_laua all
python manage.py output_ccew --upload-to-storage --geo-field geo_rgn all