
def test_start_title(page):
    page.goto("/")
    assert page.title() == "DP Start"


def test_fca_show_data_h4(page):
    page.goto("/")
    page.click("text=Go to FCA >> nth=-1")
    page.click("[name='showfiscalreports']")
    show_fisc_rep = page.inner_text('h4')
    page.click("text=Go back to FCA")
    page.click("[name='showinvoices']")
    show_inv = page.inner_text('h4')
    assert (show_fisc_rep, show_inv) == ('FCA Show data: Fiscal reports','FCA Show data: Invoices')


def test_fca_pr_error_msg(page):
    page.goto("/")
    page.click("text=Go to FCA >> nth=-1")
    page.click("text=Payment reports")
    page.select_option('select#selectStartDate', '2077-05-24')
    page.click("[name='OKStartDate']")
    page.click("text=Generate and download")
    assert page.inner_text('//*[@id="content-wrap"]/div[1]') == 'First select end date!\n×'


