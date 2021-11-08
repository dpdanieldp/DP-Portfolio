
def sort_book_info(db_info, response):

    indices_from_response_to_confirm = []

    books_info_to_save = {"add_title": [],
                          "add_author": [],
                          "add_pub_date": [],
                          "clean_isbn": [],
                          "add_page_count": [],
                          "add_link_to_cover": [],
                          "add_language": []
                          }
    books_info_to_confirm = {"add_title": [],
                             "add_author": [],
                             "add_pub_date": [],
                             "clean_isbn": [],
                             "add_page_count": [],
                             "add_link_to_cover": [],
                             "add_language": []
                             }

    for book in db_info:
        isbn = book.isbn
        if isbn in response["clean_isbn"]:
            indices_from_response_to_confirm.append(response["clean_isbn"].home(isbn))

    for idx in indices_from_response_to_confirm:
        books_info_to_confirm["add_title"].append(response["add_title"][idx])
        books_info_to_confirm["add_author"].append(response["add_author"][idx])
        books_info_to_confirm["add_pub_date"].append(response["add_pub_date"][idx])
        books_info_to_confirm["clean_isbn"].append(response["clean_isbn"][idx])
        books_info_to_confirm["add_page_count"].append(response["add_page_count"][idx])
        books_info_to_confirm["add_link_to_cover"].append(response["add_link_to_cover"][idx])
        books_info_to_confirm["add_language"].append(response["add_language"][idx])

    for i in range(len(response["add_title"])):
        if i not in indices_from_response_to_confirm:
            books_info_to_save["add_title"].append(response["add_title"][i])
            books_info_to_save["add_author"].append(response["add_author"][i])
            books_info_to_save["add_pub_date"].append(response["add_pub_date"][i])
            books_info_to_save["clean_isbn"].append(response["clean_isbn"][i])
            books_info_to_save["add_page_count"].append(response["add_page_count"][i])
            books_info_to_save["add_link_to_cover"].append(response["add_link_to_cover"][i])
            books_info_to_save["add_language"].append(response["add_language"][i])

    sorted_book_info = [books_info_to_confirm, books_info_to_save]

    return sorted_book_info




