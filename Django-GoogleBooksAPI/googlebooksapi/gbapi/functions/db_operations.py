# from website import db
from ..models import Book, TemporaryInfo
from datetime import datetime
from django.db.models import Q
import re


def check_if_empty_table():
    """
    Function checks if table Book is empty or not
    """

    if Book.objects.first() is None:
        return True
    else:
        return False


def check_if_isbns_in_db(l_isbn):
    """
    Function checks if ISBNs from list are already present in db
    """
    l_of_isbns_without_none = list(set(l_isbn))
    if '---' in l_of_isbns_without_none:
        l_of_isbns_without_none.remove('---')

    books = Book.objects.filter(isbn__in=l_of_isbns_without_none)

    if len(books) == 0:
        return False
    else:
        return books


def add_books(books_info_d):
    """
    Function adds new books to Book table using data get in dictionary books_info_d
    """
    for i in range(len(books_info_d["add_title"])):
        try:
            date = datetime.strptime(books_info_d["add_pub_date"][i], '%Y-%m-%d')
        except ValueError:
            try:
                date = datetime.strptime(books_info_d["add_pub_date"][i], '%Y-%m').date()
            except ValueError:
                try:
                    date = datetime.strptime(books_info_d["add_pub_date"][i], '%Y').date()
                except:
                    date = datetime.strptime('1000-01-01', '%Y-%m-%d')
        finally:

            book_info = Book(title=books_info_d["add_title"][i],
                             author=books_info_d["add_author"][i],
                             publication_date=date,
                             isbn=books_info_d["clean_isbn"][i],
                             page_count=books_info_d["add_page_count"][i],
                             link_to_cover=books_info_d["add_link_to_cover"][i],
                             publication_language=books_info_d["add_language"][i])

            book_info.save()


def search_in_db(query_d):
    """
    Function searches books in db by criteria passed in query_d dictionary.
    Function searches using .like function so it is possible to find book searching by fragment of it's title or author name.
    If no dates were passed in query_d all dates existing in db are passed to  Book.publication_date.between([start_date, end_date])
    If only start_date was selected- end_date is latest date from db; if only end_date was selected- start_date is earliest date from db
    """

    empty_fields = [None, '', '---']
    dates = []
    for date in Book.objects.values_list('publication_date'):
        dates.append(date[0])
    dates2 = list(set(dates))
    sorted_dates = sorted(dates2)

    like_title = '%%'
    like_author = '%%'
    like_publication_language = '%%'
    like_dates = [sorted_dates[0], sorted_dates[-1]]

    if query_d["searchTitle"] not in empty_fields:
        like_title = '%%' + query_d["searchTitle"] + '%%'
    if query_d["searchAuthor"] not in empty_fields:
        like_author = '%%' + query_d["searchAuthor"] + '%%'
    if query_d["searchLanguage"] not in empty_fields:
        like_publication_language = '%%' + query_d["searchLanguage"] + '%%'
    if query_d["selectStartDate"] not in empty_fields:
        like_dates[0] = datetime.strptime(query_d["selectStartDate"], '%Y-%m-%d').date()
    if query_d["selectEndDate"] not in empty_fields:
        like_dates[1] = datetime.strptime(query_d["selectEndDate"], '%Y-%m-%d').date()
    books = Book.objects.extra(where=['title like "' + like_title +
                                      '" and author like "' + like_author +
                                      '" and publication_language like "' + like_publication_language +
                                      '" and publication_date between "' + str(like_dates[0]) +
                                      '" and "' + str(like_dates[1]) + '"'])

    if len(books) == 0:
        return False
    else:
        return books


def overwrite_books(books_info_d, old_isbn_l):
    """
    Overwrites book or books by ISBN in db.

    If old_isbn_l was passed (as not empty list) function overwrites book in db by this ISBN
    (used only when user wants to edit book in db changing it's ISBN to ISBN of a book already present in db)
    """

    for i in range(len(books_info_d["add_title"])):
        try:
            date = datetime.strptime(books_info_d["add_pub_date"][i], '%Y-%m-%d')
        except ValueError:
            try:
                date = datetime.strptime(books_info_d["add_pub_date"][i], '%Y-%m').date()
            except ValueError:
                try:
                    date = datetime.strptime(books_info_d["add_pub_date"][i], '%Y').date()
                except:
                    date = datetime.strptime('1000-01-01', '%Y-%m-%d')
        finally:
            if len(old_isbn_l) == 0:
                book = Book.objects.get(isbn=books_info_d["clean_isbn"][i])
            else:
                book = Book.objects.get(isbn=old_isbn_l[0])

            book.title = books_info_d["add_title"][i]
            book.author = books_info_d["add_author"][i]
            book.isbn = books_info_d["clean_isbn"][i]
            book.publication_date = date
            book.page_count = books_info_d["add_page_count"][i]
            book.link_to_cover = books_info_d["add_link_to_cover"][i]
            book.publication_language = books_info_d["add_language"][i]

            book.save()


def delete_book_by_id(id):
    """
    Deletes book from db by id
    """
    Book.objects.filter(id=int(id)).delete()


def save_temporary_info(key, info):
    """
    Saves temporary info by key
    """

    response_to_db = TemporaryInfo(key=key, info=info)
    response_to_db.save()



def get_temporary_info(key):
    """
    Returns temporary info by key or None if there is no info for key in db
    """
    try:
        result = TemporaryInfo.objects.get(key=key)
        return result.info
    except TemporaryInfo.DoesNotExist:
        return None
