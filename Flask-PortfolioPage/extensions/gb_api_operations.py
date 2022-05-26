import os

import requests
from isbnlib import clean


def gb_query(query_d):
    q = ""
    in_title = ""
    in_author = ""
    in_publisher = ""
    subject = ""
    isbn = ""
    lcnn = ""
    oclc = ""

    if query_d["q"] != "":
        q = query_d["q"]
    if query_d["in_title"] != "":
        in_title = "+intitle:" + query_d["in_title"]
    if query_d["in_author"] != "":
        in_author = "+inauthor:" + query_d["in_author"]
    if query_d["in_publisher"] != "":
        in_publisher = "+inpublisher:" + query_d["in_publisher"]
    if query_d["subject"] != "":
        subject = "+subject:" + query_d["subject"]
    if query_d["isbn"] != "":
        isbn = "+isbn:" + query_d["isbn"]
    if query_d["lcnn"] != "":
        lcnn = "+lcnn:" + query_d["lcnn"]
    if query_d["oclc"] != "":
        oclc = "+oclc:" + query_d["oclc"]

    google_key = os.getenv("GOOGLE_KEY")
    country_name = "PL"
    max_results = 40
    start_index = 0

    api_url = (
        f"https://www.googleapis.com/books/v1/volumes?q="
        f"{q}{in_title}{in_author}{in_publisher}{subject}"
        f"{isbn}{lcnn}{oclc}&country={country_name}&key={google_key}"
        f"&printType=books&maxResults={str(max_results)}&startIndex={str(start_index)}"
    )

    response = requests.get(api_url)
    if response.status_code != 200:
        return False
    elif response.json()["totalItems"] == 0:
        return None
    else:

        data = response.json()
        books_info_d = {
            "add_title": [],
            "add_author": [],
            "add_pub_date": [],
            "clean_isbn": [],
            "add_page_count": [],
            "add_link_to_cover": [],
            "add_language": [],
        }
        added_info_d = add_response_to_dict(books_info_d=books_info_d, response=data)
        if int(data["totalItems"]) <= len(data["items"]):

            added_info_d_wd = remove_duplications(added_info_d)

            return added_info_d_wd

        else:
            response_l = []
            while "items" in list(data.keys()):

                api_url = (
                    f"https://www.googleapis.com/books/v1/volumes?q="
                    f"{q}{in_title}{in_author}{in_publisher}{subject}"
                    f"{isbn}{lcnn}{oclc}&country={country_name}&key={google_key}"
                    f"&printType=books&maxResults={str(max_results)}&startIndex={str(start_index)}"
                )
                # print(api_url)
                data = requests.get(api_url).json()
                if "items" in list(data.keys()):
                    start_index += len(data["items"])
                    response_l.append(data)
                else:
                    break

            for response in response_l:
                added_info_d2 = add_response_to_dict(
                    books_info_d=added_info_d, response=response
                )
                added_info_d = added_info_d2

            d_to_return = remove_duplications(added_info_d)

            return d_to_return


def add_response_to_dict(books_info_d, response):
    for i in range(len(response["items"])):
        """books_info_d = {"add_title": [],
        "add_author": [],
        "add_pub_date": [],
        "clean_isbn": []
        "add_page_count": [],
        "add_link_to_cover": [],
        "add_language": []
        }"""
        try:
            books_info_d["add_title"].append(
                response["items"][i]["volumeInfo"]["title"]
            )
        except KeyError:
            books_info_d["add_title"].append("!REMOVE_ME!")
        finally:
            try:
                books_info_d["add_author"].append(
                    ";".join(response["items"][i]["volumeInfo"]["authors"])
                )
            except KeyError:
                books_info_d["add_author"].append("---")
            finally:
                try:
                    books_info_d["add_pub_date"].append(
                        response["items"][i]["volumeInfo"]["publishedDate"]
                    )
                except KeyError:
                    books_info_d["add_pub_date"].append("---")
                finally:

                    try:
                        isbns_list_of_dicts = response["items"][i]["volumeInfo"][
                            "industryIdentifiers"
                        ]
                        isbn = clean(isbns_list_of_dicts[0]["identifier"])
                        books_info_d["clean_isbn"].append(isbn)
                    except KeyError:
                        books_info_d["clean_isbn"].append("---")
                    finally:

                        try:
                            books_info_d["add_page_count"].append(
                                response["items"][i]["volumeInfo"]["pageCount"]
                            )
                        except KeyError:
                            books_info_d["add_page_count"].append("---")
                        finally:
                            try:
                                books_info_d["add_link_to_cover"].append(
                                    response["items"][i]["volumeInfo"]["imageLinks"][
                                        "thumbnail"
                                    ]
                                )
                            except KeyError:
                                books_info_d["add_link_to_cover"].append("---")
                            finally:
                                try:
                                    books_info_d["add_language"].append(
                                        response["items"][i]["volumeInfo"]["language"]
                                    )
                                except KeyError:
                                    books_info_d["add_language"].append("---")

    return books_info_d


def remove_duplications(d_without_invalid):
    number_of_all_positions = len(d_without_invalid["clean_isbn"])
    number_of_unique_positions = len(set(d_without_invalid["clean_isbn"]))

    if number_of_all_positions == number_of_unique_positions:
        return d_without_invalid
    else:
        d_without_duplications = {
            "add_title": [],
            "add_author": [],
            "add_pub_date": [],
            "clean_isbn": [],
            "add_page_count": [],
            "add_link_to_cover": [],
            "add_language": [],
        }
        unique_isbn = set(d_without_invalid["clean_isbn"])
        indices_of_unique_titles_without_isbn = []
        if "---" in unique_isbn:
            unique_isbn.remove("---")
            indices_of_no_isbn = [
                i for i, x in enumerate(d_without_invalid["clean_isbn"]) if x == "---"
            ]
            unique_titles_without_isbn = []
            for idx in indices_of_no_isbn:
                if (
                    d_without_invalid["add_title"][idx]
                    not in unique_titles_without_isbn
                ):
                    indices_of_unique_titles_without_isbn.append(idx)
                    unique_titles_without_isbn.append(
                        d_without_invalid["add_title"][idx]
                    )

        for isbn in unique_isbn:
            idx = d_without_invalid["clean_isbn"].index(isbn)
            d_without_duplications["add_title"].append(
                d_without_invalid["add_title"][idx]
            )
            d_without_duplications["add_author"].append(
                d_without_invalid["add_author"][idx]
            )
            d_without_duplications["add_pub_date"].append(
                d_without_invalid["add_pub_date"][idx]
            )
            d_without_duplications["clean_isbn"].append(
                d_without_invalid["clean_isbn"][idx]
            )
            d_without_duplications["add_page_count"].append(
                d_without_invalid["add_page_count"][idx]
            )
            d_without_duplications["add_link_to_cover"].append(
                d_without_invalid["add_link_to_cover"][idx]
            )
            d_without_duplications["add_language"].append(
                d_without_invalid["add_language"][idx]
            )

        for idx in indices_of_unique_titles_without_isbn:
            d_without_duplications["add_title"].append(
                d_without_invalid["add_title"][idx]
            )
            d_without_duplications["add_author"].append(
                d_without_invalid["add_author"][idx]
            )
            d_without_duplications["add_pub_date"].append(
                d_without_invalid["add_pub_date"][idx]
            )
            d_without_duplications["clean_isbn"].append(
                d_without_invalid["clean_isbn"][idx]
            )
            d_without_duplications["add_page_count"].append(
                d_without_invalid["add_page_count"][idx]
            )
            d_without_duplications["add_link_to_cover"].append(
                d_without_invalid["add_link_to_cover"][idx]
            )
            d_without_duplications["add_language"].append(
                d_without_invalid["add_language"][idx]
            )

        return d_without_duplications
