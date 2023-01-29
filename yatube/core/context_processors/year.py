from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    day = datetime.today()
    year = day.year
    return {
        "year": year
    }
