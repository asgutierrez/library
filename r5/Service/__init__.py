from r5.Service import App
from r5.Service.Endpoint import (
    Books,
)


def add_urls(app):
    """Urls"""
    # Book
    app.add_url_rule(
        "/books", view_func=Books.Create.as_view("books")
    )
    app.add_url_rule(
        "/books/<id>",
        view_func=Books.Details.as_view("books_info"),
    )


def setup():
    """Start App"""
    app = App.init_app()

    add_urls(app)

    return app
