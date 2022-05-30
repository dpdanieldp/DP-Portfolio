import ast
import datetime
import json

from extensions import (
    bankier_btfs,
    check_wallet,
    gb_api_operations,
    gb_db_operations,
    polygon_tickersnames,
    sort_book_info,
    ti_wallet_report,
)
from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_login import current_user, login_required
from isbnlib import clean, is_isbn10, is_isbn13
from sqlalchemy import not_

from . import db
from .models import *

views = Blueprint("views", __name__)


def delete_session_variables():
    if session.get("shop") is not None:
        session.pop("shop")
    if session.get("a") is not None:
        session.pop("a")
    if session.get("b") is not None:
        session.pop("b")


@views.route("/", methods=["GET", "POST"])
def start():
    session.clear()
    return render_template("start.html", user=current_user)


@views.route("/aboutgb", methods=["GET", "POST"])
def about_gb():
    session.clear()
    return render_template("aboutgb.html", user=current_user)


@views.route("/gbhome", methods=["GET", "POST"])
def gb_home():
    books = Book.query.all()
    dates = []
    if len(books) > 0:
        for book in books:
            dates.append(book.publication_date)
        dates2 = list(set(dates))
    else:
        dates2 = []

    if request.method == "POST":
        if request.form.get("search"):
            search_title = (request.form.get("searchTitle")).strip()
            search_author = (request.form.get("searchAuthor")).strip()
            search_language = (request.form.get("searchLanguage")).strip()
            select_start_date = request.form.get("selectStartDate")
            select_end_date = request.form.get("selectEndDate")

            fields = [
                search_title,
                search_author,
                search_language,
                select_start_date,
                select_end_date,
            ]
            empty_fields = ["", "---"]

            if set(fields) == set(empty_fields):
                flash("Fill in at least one field", category="error")

            elif select_start_date != "---" and select_end_date != "---":
                date1 = datetime.datetime.strptime(select_start_date, "%Y-%m-%d")
                date2 = datetime.datetime.strptime(select_end_date, "%Y-%m-%d")
                if date2 < date1:
                    flash(
                        "The end date cannot be earlier than the start date",
                        category="error",
                    )
                else:
                    query_d = {
                        "searchTitle": search_title,
                        "searchAuthor": search_author,
                        "searchLanguage": search_language,
                        "selectStartDate": select_start_date,
                        "selectEndDate": select_end_date,
                    }
                    response = gb_db_operations.search_in_db(query_d)

                    title = query_d["searchTitle"]
                    author = query_d["searchAuthor"]
                    language = query_d["searchLanguage"]
                    start_date = query_d["selectStartDate"]
                    end_date = query_d["selectEndDate"]

                    if response is False:

                        flash(
                            f"No results for criteria: Title: {title}, Author: {author},"
                            f" Language: {language}, Start date:{start_date}, End date: {end_date}",
                            category="error",
                        )
                    else:
                        count = len(response)

                        flash(
                            f" Showing {count} results for criteria: Title: {title}, Author: {author}, "
                            f"Language: {language}, Start date:{start_date}, End date: {end_date}",
                            category="success",
                        )
                        books = response

                        return render_template(
                            "gbhome.html",
                            empty_table=gb_db_operations.check_if_empty_table(),
                            dates=sorted(dates2),
                            books=books,
                            user=current_user,
                        )

            else:
                query_d = {
                    "searchTitle": search_title,
                    "searchAuthor": search_author,
                    "searchLanguage": search_language,
                    "selectStartDate": select_start_date,
                    "selectEndDate": select_end_date,
                }
                response = gb_db_operations.search_in_db(query_d)

                title = query_d["searchTitle"]
                author = query_d["searchAuthor"]
                language = query_d["searchLanguage"]
                start_date = query_d["selectStartDate"]
                end_date = query_d["selectEndDate"]

                if response is False:

                    flash(
                        f"No results for criteria: Title: {title}, Author: {author},"
                        f" Language: {language}, Start date:{start_date}, End date: {end_date}",
                        category="error",
                    )
                else:
                    count = len(response)

                    flash(
                        f" Showing {count} results for criteria: Title: {title}, Author: {author}, "
                        f"Language: {language}, Start date:{start_date}, End date: {end_date}",
                        category="success",
                    )
                    books = response

                    return render_template(
                        "gbhome.html",
                        empty_table=gb_db_operations.check_if_empty_table(),
                        dates=sorted(dates2),
                        books=books,
                        user=current_user,
                    )

    return render_template(
        "gbhome.html",
        empty_table=gb_db_operations.check_if_empty_table(),
        dates=sorted(dates2),
        books=books,
        user=current_user,
    )


@views.route("/add-book", methods=["GET", "POST"])
def add_book():
    books = Book.query.all()
    if request.method == "POST":
        if request.form.get("addBook"):
            add_title = (request.form.get("addTitle")).strip()
            add_author = (request.form.get("addAuthor")).strip()
            add_pub_date = (request.form.get("addPubDate")).strip()
            add_isbn = (request.form.get("addIsbn")).strip()
            add_page_count = request.form.get("addPageCount")
            add_link_to_cover = (request.form.get("addLinkToCover")).strip()
            add_language = (request.form.get("addLanguage")).strip()

            clean_isbn = clean(add_isbn)

            list_of_required_fields = [
                add_title,
                add_author,
                add_pub_date,
                add_page_count,
                add_language,
                clean_isbn,
            ]

            if "" in set(list_of_required_fields):
                flash("Fields marked with * are mandatory.", category="error")
            elif (
                clean_isbn != ""
                and not is_isbn13(clean_isbn)
                and not is_isbn10(clean_isbn)
            ):
                flash("Incorrect ISBN!", category="error")
            else:

                if add_link_to_cover == "":
                    add_link_to_cover = "---"

                books_info_d = {
                    "add_title": [add_title],
                    "add_author": [add_author],
                    "add_pub_date": [add_pub_date],
                    "clean_isbn": [clean_isbn],
                    "add_page_count": [add_page_count],
                    "add_link_to_cover": [add_link_to_cover],
                    "add_language": [add_language],
                }

                info_from_db = gb_db_operations.check_if_isbns_in_db([clean_isbn])
                if info_from_db is False:
                    gb_db_operations.add_books(books_info_d)
                    flash("The book was successfully saved", category="success")
                    books = Book.query.all()
                    return render_template(
                        "add_book.html",
                        empty_table=gb_db_operations.check_if_empty_table(),
                        books=books,
                        user=current_user,
                    )
                else:
                    """Delete temporary info"""
                    db.session.query(TemporaryInfo).delete()
                    db.session.commit()

                    """Save temporary info"""

                    gb_db_operations.save_temporary_info(
                        key="l_isbn", info=str([clean_isbn])
                    )
                    gb_db_operations.save_temporary_info(
                        key="books_info_d", info=str(books_info_d)
                    )
                    gb_db_operations.save_temporary_info(key="old_id", info="-")
                    return redirect((url_for("views.confirm_overwriting")))

    return render_template(
        "add_book.html",
        empty_table=gb_db_operations.check_if_empty_table(),
        books=books,
        user=current_user,
    )


@views.route("/confirm-overwriting", methods=["GET", "POST"])
def confirm_overwriting():
    """Confirm overwriting if ISBN already in DB"""

    """Get temporary info"""
    books_info_str = gb_db_operations.get_temporary_info(key="books_info_d")
    l_isbn_str = gb_db_operations.get_temporary_info(key="l_isbn")
    old_id_str = gb_db_operations.get_temporary_info(key="old_id")

    if books_info_str is None or l_isbn_str is None:
        flash("An error occurred", category="error")
        return redirect((url_for("views.gb_home")))
    else:
        books_info_d = ast.literal_eval(books_info_str)
        l_isbn = ast.literal_eval(l_isbn_str)

        data_in_db = gb_db_operations.check_if_isbns_in_db(l_isbn)

        if request.method == "POST":
            if request.form.get("overwriteAll"):
                if old_id_str != "-":
                    try:
                        old_id = int(old_id_str)
                        gb_db_operations.overwrite_books(books_info_d, l_isbn)
                        gb_db_operations.delete_book_by_id(old_id)
                    except:
                        flash("An unknown error occurred", category="error")
                else:
                    try:
                        gb_db_operations.overwrite_books(books_info_d, [])
                        flash("Successfully saved", category="success")
                    except:
                        flash("An unknown error occurred", category="error")

                return redirect((url_for("views.gb_home")))

        return render_template(
            "confirm_overwriting.html",
            data_in_db=data_in_db,
            books_info_d=books_info_d,
            lenght=len(books_info_d["add_title"]),
            user=current_user,
        )


@views.route("/import-from-API", methods=["GET", "POST"])
def import_book():
    books = Book.query.all()
    if request.method == "POST":
        if request.form.get("searchInGB"):

            q = (request.form.get("searchInAllFields")).strip()
            in_title = (request.form.get("inTitle")).strip()
            in_author = (request.form.get("inAuthor")).strip()
            in_publisher = (request.form.get("inPublisher")).strip()
            subject = (request.form.get("subject")).strip()
            isbn = (request.form.get("isbn")).strip()
            lcnn = (request.form.get("lcnn")).strip()
            oclc = (request.form.get("oclc")).strip()

            query_d = {
                "q": q,
                "in_title": in_title,
                "in_author": in_author,
                "in_publisher": in_publisher,
                "subject": subject,
                "isbn": clean(isbn),
                "lcnn": lcnn,
                "oclc": oclc,
            }
            if set(list(query_d.values())) == {""}:
                flash("Fill in at least one field", category="error")
            else:
                response = gb_api_operations.gb_query(query_d)
                if response is False:
                    info = "error"
                    flash(
                        "An error occurred while connecting to Google Books",
                        category="error",
                    )
                    return render_template(
                        "import_from_API.html",
                        empty_table=gb_db_operations.check_if_empty_table(),
                        info=info,
                        books=books,
                        user=current_user,
                    )
                elif response is None:
                    info = "no_result"
                    flash("No results for the given criteria", category="error")
                    return render_template(
                        "import_from_API.html",
                        empty_table=gb_db_operations.check_if_empty_table(),
                        info=info,
                        books=books,
                        user=current_user,
                    )
                else:
                    """Delete temporary info"""
                    db.session.query(TemporaryInfo).delete()
                    db.session.commit()

                    """Save temporary info"""

                    gb_db_operations.save_temporary_info(
                        key="response", info=str(response)
                    )

                    info = str(len(response["add_title"])) + " books were found"
                    flash(info, category="success")
                    return render_template(
                        "import_from_API.html",
                        empty_table=gb_db_operations.check_if_empty_table(),
                        info=info,
                        books=books,
                        books_info_d=response,
                        lenght=len(response["add_title"]),
                        user=current_user,
                    )

        if request.form.get("addAll"):

            temporary_response_str = gb_db_operations.get_temporary_info(key="response")

            """Delete temporary info"""

            db.session.query(TemporaryInfo).delete()
            db.session.commit()

            if temporary_response_str is None:
                flash("An error occurred", category="error")
                return redirect((url_for("views.import_book")))
            else:
                response = ast.literal_eval(temporary_response_str)

                db_info = gb_db_operations.check_if_isbns_in_db(response["clean_isbn"])
                if db_info is False:
                    gb_db_operations.add_books(response)
                    info = str(len(response["add_title"])) + " books saved successfully"
                    flash(info, category="success")
                    return redirect((url_for("views.import_book")))

                else:

                    if len(db_info) < len(response["add_title"]):
                        sorted_book_info = sort_book_info.sort_book_info(
                            db_info, response
                        )
                        try:
                            gb_db_operations.add_books(sorted_book_info[1])
                            info = (
                                str(len(response["add_title"]))
                                + " books saved successfully"
                            )

                            """Delete temporary info"""
                            db.session.query(TemporaryInfo).delete()
                            db.session.commit()

                            """Save temporary info"""

                            gb_db_operations.save_temporary_info(
                                key="l_isbn",
                                info=str(sorted_book_info[0]["clean_isbn"]),
                            )

                            gb_db_operations.save_temporary_info(
                                key="books_info_d", info=str(sorted_book_info[0])
                            )
                            gb_db_operations.save_temporary_info(key="old_id", info="-")

                            flash(info, category="success")
                            return redirect((url_for("views.confirm_overwriting")))
                        except:

                            flash("An error occurred", category="error")
                            return redirect((url_for("views.import_book")))
                    else:
                        """Delete temporary info"""
                        db.session.query(TemporaryInfo).delete()
                        db.session.commit()

                        """Save temporary info"""

                        gb_db_operations.save_temporary_info(
                            key="l_isbn", info=str(response["clean_isbn"])
                        )
                        gb_db_operations.save_temporary_info(
                            key="books_info_d", info=str(response)
                        )
                        gb_db_operations.save_temporary_info(key="old_id", info="-")

                        return redirect((url_for("views.confirm_overwriting")))

    return render_template(
        "import_from_API.html",
        empty_table=gb_db_operations.check_if_empty_table(),
        info="before_result",
        books=books,
        user=current_user,
    )


@views.route("/edit-book/<id>", methods=["GET", "POST"])
def edit_book(id):
    book = Book.query.filter_by(id=id).first()
    if request.method == "POST":
        if request.form.get("save"):
            add_title = (request.form.get("title")).strip()
            add_author = (request.form.get("author")).strip()
            add_pub_date = (request.form.get("pubDate")).strip()
            add_isbn = (request.form.get("isbn")).strip()
            add_page_count = request.form.get("number_of_pages")
            add_link_to_cover = (request.form.get("link_to_cover")).strip()
            add_language = (request.form.get("language")).strip()

            clean_isbn = clean(add_isbn)
            list_of_fields = [
                add_title,
                add_author,
                add_page_count,
                add_language,
                clean_isbn,
            ]

            if set(list_of_fields) == {""}:
                flash("No changes were made", category="info")

            elif (
                clean_isbn != ""
                and not is_isbn13(clean_isbn)
                and not is_isbn10(clean_isbn)
            ):
                flash("Incorrect ISBN!", category="error")

            else:

                if add_title == "":
                    add_title = book.title
                if add_author == "":
                    add_author = book.author
                if add_page_count == "":
                    add_page_count = book.page_count
                if add_link_to_cover == "":
                    add_link_to_cover = book.link_to_cover
                if add_language == "":
                    add_language = book.publication_language

                if clean_isbn == "":
                    clean_isbn = book.isbn

                    books_info_d = {
                        "add_title": [add_title],
                        "add_author": [add_author],
                        "add_pub_date": [str(add_pub_date)],
                        "clean_isbn": [clean_isbn],
                        "add_page_count": [int(add_page_count)],
                        "add_link_to_cover": [add_link_to_cover],
                        "add_language": [add_language],
                    }
                    try:
                        gb_db_operations.overwrite_books(books_info_d, [book.isbn])
                        flash("Saved successfully", category="success")

                    except:
                        flash("An unknown error occurred", category="error")

                    return redirect((url_for("views.gb_home")))
                else:
                    """
                    If ISBN was modified- I check if this new ISBN is already present in DB:
                    """
                    db_info = gb_db_operations.check_if_isbns_in_db([clean_isbn])

                    books_info_d = {
                        "add_title": [add_title],
                        "add_author": [add_author],
                        "add_pub_date": [str(add_pub_date)],
                        "clean_isbn": [clean_isbn],
                        "add_page_count": [int(add_page_count)],
                        "add_link_to_cover": [add_link_to_cover],
                        "add_language": [add_language],
                    }
                    if db_info is False:
                        try:
                            gb_db_operations.overwrite_books(books_info_d, [book.isbn])
                            flash("Saved successfully", category="success")

                        except:
                            flash("An unknown error occurred", category="error")
                    else:

                        """Delete temporary info"""
                        db.session.query(TemporaryInfo).delete()
                        db.session.commit()

                        """Save temporary info"""

                        gb_db_operations.save_temporary_info(
                            key="l_isbn", info=str([clean_isbn])
                        )
                        gb_db_operations.save_temporary_info(
                            key="books_info_d", info=str(books_info_d)
                        )
                        gb_db_operations.save_temporary_info(key="old_id", info=str(id))
                        return redirect((url_for("views.confirm_overwriting")))

    return render_template("edit_book.html", book=book, user=current_user)


books_schema = BookSchema(many=True)


@views.route("book-collection/api/query", methods=["GET"])
def api_request():
    api_title = request.args.get("title")
    api_author = request.args.get("author")
    api_language = request.args.get("language")
    api_start_date = request.args.get("fromdate")
    api_end_date = request.args.get("todate")

    arguments_l = [api_title, api_author, api_language, api_start_date, api_end_date]
    invalid_sets = [{None}, {None, ""}, {""}]

    try:
        new_start_date = datetime.datetime.strptime(api_start_date, "%Y-%m-%d")
        new_end_date = datetime.datetime.strptime(api_end_date, "%Y-%m-%d")
        correct_date = True
    except ValueError:
        correct_date = False
    except TypeError:
        correct_date = True
        pass

    if (
        gb_db_operations.check_if_empty_table() is True
        or set(arguments_l) in invalid_sets
        or correct_date is False
    ):
        return (jsonify({"results": "0", "api_response": "Nothing was found"}), 404)
    else:

        query_d = {
            "searchTitle": api_title,
            "searchAuthor": api_author,
            "searchLanguage": api_language,
            "selectStartDate": api_start_date,
            "selectEndDate": api_end_date,
        }

        response = gb_db_operations.search_in_db(query_d)

        if response is False:
            return (jsonify({"results": "0", "api_response": "Nothing was found"}), 404)
        else:
            return (
                jsonify(
                    {
                        "results": str(len(response)),
                        "api_response": books_schema.dump(response),
                    }
                ),
                200,
            )


@views.route("/aboutti", methods=["GET"])
def aboutti():
    delete_session_variables()
    return render_template("aboutti.html", user=current_user)


@views.route("/aboutawsda", methods=["GET"])
def aboutawsda():
    session.clear()
    return render_template("aboutawsda.html", user=current_user)


@views.route("/awsda-q1", methods=["GET"])
def awsda_q1():
    session.clear()
    return render_template("awsda_q1.html", user=current_user)


@views.route("/awsda-q2", methods=["GET"])
def awsda_q2():
    session.clear()
    return render_template("awsda_q2.html", user=current_user)


@views.route("/awsda-q3", methods=["GET"])
def awsda_q3():
    session.clear()
    return render_template("awsda_q3.html", user=current_user)


@views.route("/awsda-relational-1", methods=["GET"])
def awsda_relational_1():
    session.clear()
    return render_template("awsda_relational_1.html", user=current_user)


@views.route("/awsda-relational-2", methods=["GET"])
def awsda_relational_2():
    session.clear()
    return render_template("awsda_relational_2.html", user=current_user)


@views.route("/awsda-relational-2-1", methods=["GET"])
def awsda_relational_2_1():
    session.clear()
    return render_template("awsda_relational_2_1.html", user=current_user)


@views.route("/awsda-relational-sol-mso", methods=["GET"])
def awsda_relational_sol_mso():
    session.clear()
    return render_template("awsda_relational_sol_mso.html", user=current_user)


@views.route("/awsda-relational-sol-mp", methods=["GET"])
def awsda_relational_sol_mp():
    session.clear()
    return render_template("awsda_relational_sol_mp.html", user=current_user)


@views.route("/awsda-relational-sol-mp-1", methods=["GET"])
def awsda_relational_sol_mp_1():
    session.clear()
    return render_template("awsda_relational_sol_mp_1.html", user=current_user)


@views.route("/awsda-relational-sol-a", methods=["GET"])
def awsda_relational_sol_a():
    session.clear()
    return render_template("awsda_relational_sol_a.html", user=current_user)


@views.route("/awsda-relational-sol-a-1", methods=["GET"])
def awsda_relational_sol_a_1():
    session.clear()
    return render_template("awsda_relational_sol_a_1.html", user=current_user)


@views.route("/awsda-in-memory-1", methods=["GET"])
def awsda_in_memory_1():
    session.clear()
    return render_template("awsda_in_memory_1.html", user=current_user)


@views.route("/awsda-in-memory-sol-ec", methods=["GET"])
def awsda_in_memory_sol_ec():
    session.clear()
    return render_template("awsda_in_memory_sol_ec.html", user=current_user)


@views.route("/awsda-in-memory-sol-mdb", methods=["GET"])
def awsda_in_memory_sol_mdb():
    session.clear()
    return render_template("awsda_in_memory_sol_mdb.html", user=current_user)


@views.route("/download-ti")
def download_ti():
    path = "./Reports/TI_rep/TI_wallet.xlsx"

    return send_file(path, as_attachment=True)


@views.route("/tiwallet", methods=["GET", "POST"])
@login_required
def ti_wallet():
    delete_session_variables()

    bankier_btfs.bankier_currencies_check_or_not()
    bankier_btfs.bankier_rest_check_or_not()

    user = current_user

    if len(user.components) == 0:
        empty_wallet = True
    else:
        empty_wallet = False

    if not empty_wallet:
        user_currency = check_wallet.check_user_currency(user=current_user)
        check_wallet.check_wallet_components(user=current_user, currency=user_currency)

    current_wallet_value = check_wallet.check_wallet_sum_value(user=current_user)

    currencies = check_wallet.get_cur_list(user=current_user)

    if request.method == "POST":

        if request.form.get("OKchangeCurrency"):
            currency = request.form.get("selectCurrency")
            user = current_user

            if len(user.components) == 0:
                empty_wallet = True
            else:
                empty_wallet = False

            if not empty_wallet:
                check_wallet.check_wallet_components(
                    user=current_user, currency=currency
                )

            current_wallet_value = check_wallet.check_wallet_sum_value(
                user=current_user
            )

            currencies = check_wallet.get_cur_list(user=current_user)

            return render_template(
                "ti_home.html",
                user=current_user,
                empty_wallet=empty_wallet,
                currencies=currencies,
                current_wallet_value=current_wallet_value,
            )

        if request.form.get("downloadTIRep"):
            ti_wallet_report.generate_ti_wallet_rep(user=current_user)

            return redirect(url_for("views.download_ti"))

        if request.form.get("addComponent"):
            polygon_tickersnames.polygon_tickers_to_db_or_not()

            list_of_categories = [
                "Polish stocks/bonds",
                "US stocks/ ETFs",
                "Gold/Silver bullion",
                "Commodities",
                "Crypto",
                "Cash",
                "Other",
            ]

            return render_template(
                "ti_add_comp1.html",
                user=current_user,
                empty_wallet=empty_wallet,
                list_of_categories=list_of_categories,
                currencies=currencies,
            )

        if request.form.get("OKcategory"):
            category = request.form.get("selectCategory")
            if category == "Select category...":

                flash("First select category!", category="error")

                list_of_categories = [
                    "Polish stocks/bonds",
                    "US stocks/ ETFs",
                    "Gold/Silver bullion",
                    "Commodities",
                    "Crypto",
                    "Cash",
                    "Other",
                ]

                return render_template(
                    "ti_add_comp1.html",
                    user=current_user,
                    empty_wallet=empty_wallet,
                    currencies=currencies,
                    list_of_categories=list_of_categories,
                )

            elif category in ["Polish stocks/bonds", "US stocks/ ETFs"]:

                if category == "Polish stocks/bonds":
                    tickers_names = BankierStockBond.query.all()
                    tickers = []
                    names = []
                    for result in tickers_names:
                        tickers.append(result.ticker)
                        names.append(result.name)

                    zipped_tickers_names = zip(tickers, names)

                if category == "US stocks/ ETFs":
                    tickers_names = (
                        PolygonTicker.query.filter(
                            not_(PolygonTicker.ticker.like("%C:%"))
                        )
                        .filter(not_(PolygonTicker.ticker.like("%X:%")))
                        .all()
                    )
                    tickers = []
                    names = []
                    for result in tickers_names:
                        tickers.append(result.ticker)
                        names.append(result.name)

                    zipped_tickers_names = zip(tickers, names)

                return render_template(
                    "ti_add_comp2_stocksbonds.html",
                    user=current_user,
                    empty_wallet=empty_wallet,
                    category=category,
                    zipped_tickers_names=zipped_tickers_names,
                    currencies=currencies,
                    current_wallet_value=current_wallet_value,
                )

            elif category in ["Commodities", "Crypto", "Cash", "Gold/Silver bullion"]:

                if category == "Crypto":
                    tickers_names = (
                        PolygonTicker.query.filter(PolygonTicker.ticker.like("%X:%"))
                        .filter(PolygonTicker.ticker.like("%USD%"))
                        .all()
                    )
                    tickers = []
                    names = []
                    for result in tickers_names:
                        tickers.append(result.ticker)
                        names.append(result.name)

                    zipped_tickers_names = zip(tickers, names)

                if category == "Commodities":
                    tickers_names = BankierCommodity.query.all()
                    tickers = []
                    names = []
                    for result in tickers_names:
                        tickers.append(result.ticker)
                        names.append(result.name)

                    zipped_tickers_names = zip(tickers, names)

                if category == "Cash":
                    tickers_names = BankierPLNCurrency.query.all()
                    tickers = []
                    names = []
                    for result in tickers_names:
                        tickers.append(result.currency)
                        names.append("-")

                    tickers_with_pln = ["PLN"]
                    names_with_pln = ["-"]
                    tickers_with_pln.extend(tickers)
                    names_with_pln.extend(names)

                    zipped_tickers_names = zip(
                        sorted(tickers_with_pln), sorted(names_with_pln)
                    )

                if category == "Gold/Silver bullion":
                    bulion_l = ["Gold bullion", "Silver bullion"]
                    empty_l = ["-", "-"]
                    zipped_tickers_names = zip(bulion_l, empty_l)

                return render_template(
                    "ti_add_comp2_ccc.html",
                    user=current_user,
                    empty_wallet=empty_wallet,
                    category=category,
                    zipped_tickers_names=zipped_tickers_names,
                    currencies=currencies,
                )

            elif category == "Other":

                return render_template(
                    "ti_add_comp2_other.html",
                    user=current_user,
                    empty_wallet=empty_wallet,
                    category=category,
                    currencies=currencies,
                )

        if request.form.get("addThisComponent"):
            category = request.form.get("selectCategory")
            if category == "Other":
                asset = request.form.get("inputAsset")
                value = request.form.get("inputValue")

                if (asset is None) or (value is None):

                    tickers_names = BankierPLNCurrency.query.all()
                    tickers = []

                    for result in tickers_names:
                        tickers.append(result.currency)

                    tickers_with_pln = ["PLN"]
                    tickers_with_pln.extend(tickers)

                    flash("First fill in all fields!", category="error")

                    return render_template(
                        "ti_add_comp2_other.html",
                        user=current_user,
                        empty_wallet=empty_wallet,
                        category=category,
                        currencies=tickers_with_pln,
                    )
                else:
                    quantity = 1
                    currency = request.form.get("pickCurrency")
                    now = datetime.datetime.now()
                    component_date = now.strftime("%Y-%m-%d %H:%M")

                    component = Wallet(
                        ticker=asset,
                        name=asset,
                        category=category,
                        amount=quantity,
                        value_per_1=value,
                        value=value,
                        value_currency=currency,
                        date=component_date,
                        user_id=current_user.id,
                    )

                    db.session.add(component)
                    db.session.commit()

                    check_wallet.check_wallet_components(
                        user=current_user, currency=currency
                    )
                    check_wallet.check_wallet_sum_value(user=current_user)

                    list_of_categories = [
                        "Polish stocks/bonds",
                        "US stocks/ ETFs",
                        "Gold/Silver bullion",
                        "Commodities",
                        "Crypto",
                        "Cash",
                        "Other",
                    ]
                    currencies = check_wallet.get_cur_list(user=current_user)

                    user = current_user

                    if len(user.components) == 0:
                        empty_wallet = True
                    else:
                        empty_wallet = False

                    return render_template(
                        "ti_add_comp1.html",
                        user=current_user,
                        empty_wallet=empty_wallet,
                        list_of_categories=list_of_categories,
                        currencies=currencies,
                    )

            else:
                asset = request.form.get("selectTicker")
                quantity = request.form.get("inputQuantity")
                currency = request.form.get("pickCurrency")

                if (asset == "Select asset...") or (quantity is None):
                    if category in ["Polish stocks/bonds", "US stocks/ ETFs"]:

                        if category == "Polish stocks/bonds":
                            tickers_names = BankierStockBond.query.all()
                            tickers = []
                            names = []
                            for result in tickers_names:
                                tickers.append(result.ticker)
                                names.append(result.name)

                            zipped_tickers_names = zip(tickers, names)

                        if category == "US stocks/ ETFs":
                            tickers_names = (
                                PolygonTicker.query.filter(
                                    not_(PolygonTicker.ticker.like("%C:%"))
                                )
                                .filter(not_(PolygonTicker.ticker.like("%X:%")))
                                .all()
                            )
                            tickers = []
                            names = []
                            for result in tickers_names:
                                tickers.append(result.ticker)
                                names.append(result.name)

                            zipped_tickers_names = zip(tickers, names)

                        flash("First fill in all fields!", category="error")

                        return render_template(
                            "ti_add_comp2_stocksbonds.html",
                            user=current_user,
                            empty_wallet=empty_wallet,
                            category=category,
                            zipped_tickers_names=zipped_tickers_names,
                        )

                    elif category in [
                        "Commodities",
                        "Crypto",
                        "Cash",
                        "Gold/Silver bullion",
                    ]:
                        if category == "Crypto":
                            tickers_names = (
                                PolygonTicker.query.filter(
                                    PolygonTicker.ticker.like("%X:%")
                                )
                                .filter(PolygonTicker.ticker.like("%USD%"))
                                .all()
                            )
                            tickers = []
                            names = []
                            for result in tickers_names:
                                tickers.append(result.ticker)
                                names.append(result.name)

                            zipped_tickers_names = zip(tickers, names)

                        if category == "Commodities":
                            tickers_names = BankierCommodity.query.all()
                            tickers = []
                            names = []
                            for result in tickers_names:
                                tickers.append(result.ticker)
                                names.append(result.name)

                            zipped_tickers_names = zip(tickers, names)

                        if category == "Cash":
                            tickers_names = BankierPLNCurrency.query.all()
                            tickers = []
                            names = []
                            for result in tickers_names:
                                tickers.append(result.currency)
                                names.append("")

                            tickers_with_pln = ["PLN"]
                            names_with_pln = [""]
                            tickers_with_pln.extend(tickers)
                            names_with_pln.extend(names)

                            zipped_tickers_names = zip(tickers_with_pln, names_with_pln)

                        if category == "Gold/Silver bullion":
                            bulion_l = ["Gold", "Silver"]
                            empty_l = ["", ""]
                            zipped_tickers_names = zip(bulion_l, empty_l)

                        flash("First fill in all fields!", category="error")

                        return render_template(
                            "ti_add_comp2_ccc.html",
                            user=current_user,
                            empty_wallet=empty_wallet,
                            category=category,
                            zipped_tickers_names=zipped_tickers_names,
                        )

                else:
                    asset_ticker = asset.split(" - ")[0]

                    component = Wallet(
                        ticker=asset_ticker,
                        category=category,
                        amount=quantity,
                        user_id=current_user.id,
                    )

                    db.session.add(component)
                    db.session.commit()

                    check_wallet.check_wallet_components(
                        user=current_user, currency=currency
                    )
                    check_wallet.check_wallet_sum_value(user=current_user)

                    list_of_categories = [
                        "Polish stocks/bonds",
                        "US stocks/ ETFs",
                        "Gold/Silver bullion",
                        "Commodities",
                        "Crypto",
                        "Cash",
                        "Other",
                    ]
                    currencies = check_wallet.get_cur_list(user=current_user)

                    user = current_user

                    if len(user.components) == 0:
                        empty_wallet = True
                    else:
                        empty_wallet = False

                    return render_template(
                        "ti_add_comp1.html",
                        user=current_user,
                        empty_wallet=empty_wallet,
                        list_of_categories=list_of_categories,
                        currencies=currencies,
                    )

        if request.form.get("goBackToCategory"):
            list_of_categories = [
                "Polish stocks/bonds",
                "US stocks/ ETFs",
                "Gold/Silver bullion",
                "Commodities",
                "Crypto",
                "Cash",
                "Other",
            ]

            return render_template(
                "ti_add_comp1.html",
                user=current_user,
                empty_wallet=empty_wallet,
                list_of_categories=list_of_categories,
                currencies=currencies,
            )

    return render_template(
        "ti_home.html",
        user=current_user,
        empty_wallet=empty_wallet,
        currencies=currencies,
        current_wallet_value=current_wallet_value,
    )


@views.route("/delete-component", methods=["POST"])
def delete_component():
    component = json.loads(request.data)
    componentId = component["componentId"]
    component = Wallet.query.get(componentId)
    if component:
        if component.user_id == current_user.id:
            db.session.delete(component)
            db.session.commit()
            flash("Element was successfully deleted", category="success")

    return jsonify({})


@views.route("/delete-book", methods=["POST"])
def delete_book():
    book = json.loads(request.data)
    book_id = book["bookId"]
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        flash("Element was successfully deleted", category="success")

    return jsonify({})


@views.context_processor
def inject_now():
    return {"now": datetime.datetime.utcnow()}
