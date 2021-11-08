from django.test import TestCase, Client
import json
from .models import Book

# Create your tests here.

class TestGet(TestCase):

    def set_up(self):
        self.client = Client()
        pass

    # Checkinng if get method works for all views
    def test_home_get(self):
        # client = Client()
        response = self.client.get('/')
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_add_book_get(self):
        response = self.client.get('/add-book')
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)


    def test_confir_overw_get(self):
        response = self.client.get('/confirm-overwriting', follow_redirects=True)
        statuscode = response.status_code
        self.assertEqual(statuscode, 302)

    def test_import_get(self):
        response = self.client.get('/import-from-API')
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    def test_edit_book_get_not_exist(self):
        response = self.client.get('/edit-book/4')
        statuscode = response.status_code
        self.assertEqual(statuscode, 404)

    def test_edit_book_get_exist(self):
        b1 = Book.objects.create(title="Book1",
                                 author="Author1",
                                 publication_date='2001-01-01',
                                 isbn="9783404160006",
                                 page_count='98',
                                 link_to_cover='---',
                                 publication_language='de')
        response = self.client.get('/edit-book/1')
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    # For API query without args response.status_code is 404 (nothing was found)
    def test_api_get_404(self):
        response = self.client.get('/api/query')
        statuscode = response.status_code
        self.assertEqual(statuscode, 404)

    def test_api_get_200(self):
        b1 = Book.objects.create(title="Book1",
                                 author="Author1",
                                 publication_date='2001-01-01',
                                 isbn="9783404160006",
                                 page_count='98',
                                 link_to_cover='---',
                                 publication_language='de')
        response = self.client.get('/api/query?title=Book1')
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)






