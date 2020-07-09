from unittest import TestCase

from findthatcharity.utils import to_titlecase, list_to_string

# from django.test import TestCase


class TestUtils(TestCase):

    def test_to_titlecase(self):
        names = (
            ('THE CHARITY THE NAME', 'The Charity the Name'),
            ('CHARITY UK LTD', 'Charity UK Ltd'),
            ('BCDF', 'BCDF'),
            ('MRS SMITH', 'Mrs Smith'),
            ("THE CHARITY (THE NAME)", 'The Charity (the Name)'),
        )
        for n1, n2 in names:
            assert to_titlecase(n1) == n2

    def test_list_to_string(self):
        lists = (
            (['item1'], 'item1'),
            (['item1', 'item2'], 'item1 and item2'),
            (['item1', 'item2', 'item3'], 'item1, item2 and item3'),
        )
        for l1, l2 in lists:
            assert list_to_string(l1) == l2
        assert list_to_string(['item1', 'item2', 'item3'], sep="; ") == 'item1; item2 and item3'
        assert list_to_string(['item1', 'item2', 'item3'],
                              final_sep=" et ") == 'item1, item2 et item3'
        assert list_to_string(['item1', 'item2', 'item3'],
                              sep="; ", final_sep=" et ") == 'item1; item2 et item3'
