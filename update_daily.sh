python ./manage.py import_all
python ./manage.py import_charities
python ./manage.py update_geodata
python ./manage.py es_index
python ./manage.py refresh_data_views