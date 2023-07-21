from r5.Service import App
from r5.Service.Endpoint import (
    Books,
    Users,
)


def add_urls(app):
    """Urls"""
    # Book
    app.add_url_rule(
        "/books", view_func=Books.Create.as_view("books")
    )
    app.add_url_rule(
        "/books/<book_id>",
        view_func=Books.Details.as_view("books_info"),
    )
    # User
    app.add_url_rule(
        "/register", view_func=Users.Create.as_view("register")
    )
    app.add_url_rule(
        "/auth",
        view_func=Users.Auth.as_view("auth"),
    )


def setup():
    """Start App"""
    app = App.init_app()

    add_urls(app)

    return app
