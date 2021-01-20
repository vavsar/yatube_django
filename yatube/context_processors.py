import datetime as dt


def year(request):
    this_year = dt.datetime.now().year
    return {
        "year": this_year
    }
