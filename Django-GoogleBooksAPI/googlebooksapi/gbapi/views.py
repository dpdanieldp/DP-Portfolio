from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

import ast
from datetime import datetime
from isbnlib import clean, is_isbn10, is_isbn13

from .functions import db_operations, gb_api_operations, sort_book_info
from .models import Book, TemporaryInfo


# Create your views here.

def home(request):
    empty_table = db_operations.check_if_empty_table()
    books = Book.objects.all()
    dates = []
    if len(books) > 0:
        for book in books:
            dates.append(book.publication_date)

        dates2 = sorted(list(set(dates)))
    else:
        dates2 = []

    if request.method == 'POST':
        if request.POST.get('search'):
            search_title = (request.POST.get('searchTitle')).strip()
            search_author = (request.POST.get('searchAuthor')).strip()
            search_language = (request.POST.get('searchLanguage')).strip()
            select_start_date = request.POST.get('selectStartDate')
            select_end_date = request.POST.get('selectEndDate')

            fields = [search_title, search_author, search_language, select_start_date, select_end_date]
            empty_fields = ['', '---']

            if set(fields) == set(empty_fields):
                messages.error(request, 'Uzupełnij min. jedno kryterium wyszukiwania.')

            elif select_start_date != '---' and select_end_date != '---':
                date1 = datetime.strptime(select_start_date, '%Y-%m-%d')
                date2 = datetime.strptime(select_end_date, '%Y-%m-%d')
                if date2 < date1:
                    messages.error(request, 'Data końcowa nie może być wcześniejsza niż data początkowa')
                else:
                    query_d = {"searchTitle": search_title,
                               "searchAuthor": search_author,
                               "searchLanguage": search_language,
                               "selectStartDate": select_start_date,
                               "selectEndDate": select_end_date
                               }
                    response = db_operations.search_in_db(query_d)

                    title = query_d["searchTitle"]
                    author = query_d["searchAuthor"]
                    language = query_d["searchLanguage"]
                    start_date = query_d["selectStartDate"]
                    end_date = query_d["selectEndDate"]

                    if response is False:
                        messages.error(request, f"Brak wyników dla kryteriów: Tytuł: {title}, Autor: {author},"
                                                f" Język: {language}, Data pocz.:{start_date}, Data końc.: {end_date}")
                    else:
                        count = len(response)

                        messages.success(request,
                                         f"Wyświetlam {count} wyników dla kryteriów: Tytuł: {title}, Autor: {author},"
                                         f" Język: {language}, Data pocz.:{start_date}, Data końc.: {end_date}")
                        books = response

                        return render(request, 'gbapi/home.html', {"empty_table": db_operations.check_if_empty_table(),
                                                                   "dates": sorted(dates2), "books": books})

            else:
                query_d = {"searchTitle": search_title,
                           "searchAuthor": search_author,
                           "searchLanguage": search_language,
                           "selectStartDate": select_start_date,
                           "selectEndDate": select_end_date
                           }
                response = db_operations.search_in_db(query_d)

                title = query_d["searchTitle"]
                author = query_d["searchAuthor"]
                language = query_d["searchLanguage"]
                start_date = query_d["selectStartDate"]
                end_date = query_d["selectEndDate"]

                if response is False:
                    messages.error(request, f"Brak wyników dla kryteriów: Tytuł: {title}, Autor: {author},"
                                            f" Język: {language}, Data pocz.:{start_date}, Data końc.: {end_date}")
                else:
                    count = len(response)

                    messages.success(request,
                                     f" Wyświetlam {count} wyników dla kryteriów: Tytuł: {title}, Autor: {author}, "
                                     f"Język: {language}, Data pocz.:{start_date}, Data końc.: {end_date}")

                    books = response
                    
                    return render(request, 'gbapi/home.html', {"empty_table": db_operations.check_if_empty_table(),
                                                               "dates": sorted(dates2), "books": books})

        if request.POST.get('deleteBook'):
            book_id = request.POST.get('deleteBook')
            db_operations.delete_book_by_id(book_id)
            messages.success(request, 'Pozycja została pomyślnie usunięta')
            return redirect('home')



    return render(request, 'gbapi/home.html', {"empty_table": empty_table, "dates": dates2, "books": books})


def add_book(request):
    books = Book.objects.all()
    form = AddBook()
    if request.method == 'POST':
        if request.POST.get('addBook'):
            add_title = (request.POST.get('addTitle')).strip()
            add_author = (request.POST.get('addAuthor')).strip()
            add_pub_date = (request.POST.get('addPubDate')).strip()
            add_isbn = (request.POST.get('addIsbn')).strip()
            add_page_count = request.POST.get('addPageCount')
            add_link_to_cover = (request.POST.get('addLinkToCover')).strip()
            add_language = (request.POST.get('addLanguage')).strip()


            clean_isbn = clean(add_isbn)

            list_of_required_fields = [add_title, add_author, add_pub_date, add_page_count, add_language, clean_isbn]

            if '' in set(list_of_required_fields):
                messages.error(request, 'Pola oznaczone gwiazdką nie mogą być puste!')
            elif clean_isbn != '' and not is_isbn13(clean_isbn) and not is_isbn10(clean_isbn):
                messages.error(request, 'Nieprawidłowy ISBN!')
            else:

                if add_link_to_cover == '':
                    add_link_to_cover = '---'

                books_info_d = {"add_title": [add_title],
                                "add_author": [add_author],
                                "add_pub_date": [add_pub_date],
                                "clean_isbn": [clean_isbn],
                                "add_page_count": [add_page_count],
                                "add_link_to_cover": [add_link_to_cover],
                                "add_language": [add_language]
                                }

                info_from_db = db_operations.check_if_isbns_in_db([clean_isbn])
                if info_from_db is False:
                    db_operations.add_books(books_info_d)
                    messages.success(request, 'Książka została pomyślnie zapisana.')
                    books = Book.objects.all()
                    return render(request, "gbapi/add_book.html", {"empty_table": db_operations.check_if_empty_table(),
                                                                   "books": books, "form": form})
                else:
                    """Delete temporary info"""
                    TemporaryInfo.objects.all().delete()

                    """Save temporary info"""

                    db_operations.save_temporary_info(key='l_isbn', info=str([clean_isbn]))
                    db_operations.save_temporary_info(key='books_info_d', info=str(books_info_d))
                    db_operations.save_temporary_info(key='old_id', info='-')
                    return redirect('confirm-overwriting')

    return render(request, "gbapi/add_book.html", {"empty_table": db_operations.check_if_empty_table(),
                                                   "books": books, "form": form})


def import_book(request):
    books = Book.objects.all()
    if request.method == 'POST':
        if request.POST.get('searchInGB'):

            q = (request.POST.get('searchInAllFields')).strip()
            in_title = (request.POST.get('inTitle')).strip()
            in_author = (request.POST.get('inAuthor')).strip()
            in_publisher = (request.POST.get('inPublisher')).strip()
            subject = (request.POST.get('subject')).strip()
            isbn = (request.POST.get('isbn')).strip()
            lcnn = (request.POST.get('lcnn')).strip()
            oclc = (request.POST.get('oclc')).strip()

            query_d = {"q": q,
                       "in_title": in_title,
                       "in_author": in_author,
                       "in_publisher": in_publisher,
                       "subject": subject,
                       "isbn": clean(isbn),
                       "lcnn": lcnn,
                       "oclc": oclc
                       }
            if set(list(query_d.values())) == {''}:
                messages.error(request, "Uzupełnij przynajmniej jedno pole.")
            else:
                response = gb_api_operations.gb_query(query_d)
                if response is False:
                    info = 'error'
                    messages.error(request, "Wystąpił błąd przy połączeniu z Google Books")
                    return render(request, 'gbapi/import_from_API.html',
                                  {"empty_table": db_operations.check_if_empty_table(),
                                   "info": info, "books": books})
                elif response is None:
                    info = 'no_result'
                    messages.error(request, "Brak wyników dla podanych kryteriów")
                    return render(request, 'gbapi/import_from_API.html',
                                  {"empty_table": db_operations.check_if_empty_table(),
                                   "info": info, "books": books})
                else:
                    """Delete temporary info"""
                    TemporaryInfo.objects.all().delete()

                    """Save temporary info"""

                    db_operations.save_temporary_info(key='response', info=str(response))

                    info = 'Znaleziono ' + str(len(response["add_title"])) + ' książek'
                    messages.success(request, info)
                    return render(request, 'gbapi/import_from_API.html',
                                  {"empty_table": db_operations.check_if_empty_table(),
                                   "info": info, "books": books, "books_info_d": response,
                                   "range": range(len(response["add_title"]))})

        if request.POST.get('addAll'):

            temporary_response_str = db_operations.get_temporary_info(key='response')

            """Delete temporary info"""

            # db.session.query(TemporaryInfo).delete()
            # db.session.commit()

            TemporaryInfo.objects.all().delete()

            if temporary_response_str is None:
                messages.error(request, 'Wystąpił błąd')
                # return redirect((url_for('views.import_book')))
                return redirect('import-from-API')
            else:
                response = ast.literal_eval(temporary_response_str)

                db_info = db_operations.check_if_isbns_in_db(response["clean_isbn"])
                if db_info is False:
                    db_operations.add_books(response)
                    info = 'Pomyślnie zapisano ' + str(len(response["add_title"])) + ' książek'
                    messages.success(request, info)
                    return redirect('import-from-API')

                else:

                    if len(db_info) < len(response["add_title"]):
                        sorted_book_info = sort_book_info.sort_book_info(db_info, response)
                        try:
                            db_operations.add_books(sorted_book_info[1])
                            info = 'Pomyślnie zapisano ' + str(len(sorted_book_info[1]["add_title"])) + \
                                   ' książek'

                            """Delete temporary info"""
                            # db.session.query(TemporaryInfo).delete()
                            # db.session.commit()
                            TemporaryInfo.objects.all().delete()

                            """Save temporary info"""

                            db_operations.save_temporary_info(key='l_isbn',
                                                              info=str(sorted_book_info[0]["clean_isbn"]))

                            db_operations.save_temporary_info(key='books_info_d',
                                                              info=str(sorted_book_info[0]))
                            db_operations.save_temporary_info(key='old_id', info='-')

                            messages.success(request, info)
                            return redirect('confirm-overwriting')
                        except:

                            messages.error(request, 'Wystąpił błąd')
                            return redirect('import-from-API')
                    else:
                        """Delete temporary info"""
                        TemporaryInfo.objects.all().delete()

                        """Save temporary info"""

                        db_operations.save_temporary_info(key='l_isbn',
                                                          info=str(response["clean_isbn"]))
                        db_operations.save_temporary_info(key='books_info_d',
                                                          info=str(response))
                        db_operations.save_temporary_info(key='old_id', info='-')

                        return redirect('confirm-overwriting')

    return render(request, 'gbapi/import_from_API.html',
                  {"empty_table": db_operations.check_if_empty_table(), "range": False,
                   "info": "before_result", "books": books})


def confirm_overwriting(request):
    """Confirm overwriting if ISBN already in DB"""

    """Get temporary info"""
    books_info_str = db_operations.get_temporary_info(key='books_info_d')
    l_isbn_str = db_operations.get_temporary_info(key='l_isbn')
    old_id_str = db_operations.get_temporary_info(key='old_id')

    if books_info_str is None or l_isbn_str is None:
        messages.error(request, 'Wystąpił błąd')
        return redirect('home')
    else:
        books_info_d = ast.literal_eval(books_info_str)
        l_isbn = ast.literal_eval(l_isbn_str)

        data_in_db = db_operations.check_if_isbns_in_db(l_isbn)

        if request.method == 'POST':
            if request.POST.get('overwriteAll'):
                if old_id_str != '-':
                    try:
                        old_id = int(old_id_str)
                        db_operations.overwrite_books(books_info_d, l_isbn)
                        db_operations.delete_book_by_id(old_id)
                    except:
                        messages.error(request, 'Wystąpił nieznany błąd')
                else:
                    try:
                        db_operations.overwrite_books(books_info_d, [])
                        messages.success(request, 'Zapisano dane pomyślnie')
                    except:
                        messages.error(request, 'Wystąpił nieznany błąd')

                return redirect('home')

        return render(request, "gbapi/confirm_overwriting.html",
                      {"data_in_db": data_in_db, "books_info_d": books_info_d,
                       "range": range(len(books_info_d["add_title"]))})



def edit_book(request, id):
    book = get_object_or_404(Book, pk=id)
    if request.method == 'POST':
        if request.POST.get('save'):
            add_title = (request.POST.get('title')).strip()
            add_author = (request.POST.get('author')).strip()
            add_pub_date = (request.POST.get('pubDate')).strip()
            add_isbn = (request.POST.get('isbn')).strip()
            add_page_count = request.POST.get('number_of_pages')
            add_link_to_cover = (request.POST.get('link_to_cover')).strip()
            add_language = (request.POST.get('language')).strip()

            clean_isbn = clean(add_isbn)
            list_of_fields = [add_title, add_author, add_page_count, add_language, clean_isbn]

            if set(list_of_fields) == {''}:
                messages.info(request, 'Nie wprowadzono zmian')

            elif clean_isbn != '' and not is_isbn13(clean_isbn) and not is_isbn10(clean_isbn):
                messages.error(request, 'Nieprawidłowy ISBN!')

            else:

                if add_title == '':
                    add_title = book.title
                if add_author == '':
                    add_author = book.author
                if add_page_count == '':
                    add_page_count = book.page_count
                if add_link_to_cover == '':
                    add_link_to_cover = book.link_to_cover
                if add_language == '':
                    add_language = book.publication_language

                if clean_isbn == '':
                    clean_isbn = book.isbn

                    books_info_d = {"add_title": [add_title],
                                    "add_author": [add_author],
                                    "add_pub_date": [str(add_pub_date)],
                                    "clean_isbn": [clean_isbn],
                                    "add_page_count": [int(add_page_count)],
                                    "add_link_to_cover": [add_link_to_cover],
                                    "add_language": [add_language]
                                    }
                    try:
                        db_operations.overwrite_books(books_info_d, [book.isbn])
                        messages.success(request, 'Zapisano dane pomyślnie')

                    except:
                        messages.error(request, 'Wystąpił nieznany błąd')

                    return redirect('home')
                else:
                    """                    
                If ISBN was modified- I check if this new ISBN is already present in DB:                    
                """
                    db_info = db_operations.check_if_isbns_in_db([clean_isbn])

                    books_info_d = {"add_title": [add_title],
                                    "add_author": [add_author],
                                    "add_pub_date": [str(add_pub_date)],
                                    "clean_isbn": [clean_isbn],
                                    "add_page_count": [int(add_page_count)],
                                    "add_link_to_cover": [add_link_to_cover],
                                    "add_language": [add_language]
                                    }
                    if db_info is False:
                        try:
                            db_operations.overwrite_books(books_info_d, [book.isbn])
                            messages.success(request, 'Zapisano dane pomyślnie')

                        except:
                            messages.success(request, 'Wystąpił nieznany błąd')
                    else:

                        """Delete temporary info"""
                        TemporaryInfo.objects.all().delete()

                        """Save temporary info"""

                        db_operations.save_temporary_info(key='l_isbn', info=str([clean_isbn]))
                        db_operations.save_temporary_info(key='books_info_d', info=str(books_info_d))
                        db_operations.save_temporary_info(key='old_id', info=str(id))
                        return redirect('confirm_overwriting')

    return render(request, "gbapi/edit_book.html", {"book": book})


@require_http_methods(["GET"])
def api_request(request):
    api_title = request.GET.get('title', '')
    api_author = request.GET.get('author', '')
    api_language = request.GET.get('api_language', '')
    api_start_date = request.GET.get('fromdate', None)
    api_end_date = request.GET.get('todate', None)

    arguments_l = [api_title, api_author, api_language, api_start_date, api_end_date]
    invalid_sets = [{None}, {None, ''}, {''}]

    try:
        new_start_date = datetime.strptime(api_start_date, '%Y-%m-%d')
        new_end_date = datetime.strptime(api_end_date, '%Y-%m-%d')
        correct_date = True
    except ValueError:
        correct_date = False
    except TypeError:
        correct_date = True
        pass


    if db_operations.check_if_empty_table() is True or set(arguments_l) in invalid_sets or correct_date is False:

        return (JsonResponse({'results': '0', 'api_response': 'Nothing was found'}, status=404))
    else:

        query_d = {"searchTitle": api_title,
                   "searchAuthor": api_author,
                   "searchLanguage": api_language,
                   "selectStartDate": api_start_date,
                   "selectEndDate": api_end_date
                   }

        response = db_operations.search_in_db(query_d)

        if response is False:
            return (JsonResponse({'results': '0', 'api_response': 'Nothing was found'}, status=404))
        else:
            data = list(response.values())
            return (JsonResponse({'results': str(len(response)), 'api_response': data}, status=200))
