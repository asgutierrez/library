from r5.Framework import Types
from r5.Service.Config import Service
from r5.Service.Schemas.Authors import AuthorModel
from r5.Service.Schemas.Books import Book, BookModel, BookPayload
from r5.Service.Schemas.BooksAuthors import BookAuthorModel
from r5.Service.Schemas.BooksCategories import BookCategoryModel
from r5.Service.Schemas.Categories import CategoryModel
from r5.Service.Services.Utils import with_result


class Books:
    """Books service"""

    def __init__(
        self
    ) -> None:
        pass

    def get(self, filters: Types.OptionalDict = None) -> BookModel:
        """Get Book model"""

        book_models_info = BookModel.get_all_by_filters(filters=filters)
        books_dict = {}

        for book_model, author, category in book_models_info:
            if book_model.id not in books_dict:
                books_dict[book_model.id] = Book.to_dict(book_model)

                books_dict[book_model.id]["authors"] = set()
                books_dict[book_model.id]["categories"] = set()

            if author:
                books_dict[book_model.id]["authors"].add(author)

            if category:
                books_dict[book_model.id]["categories"].add(category)

        books = []
        for _, book in books_dict.items():
            book["authors"] = list(book["authors"])
            book["categories"] = list(book["categories"])
            books.append(book)

        return books


    def save(self, book_payload: BookPayload) -> BookModel:
        """Save Book"""

        book = Book(**book_payload.dict())
        book_model = book.to_model()
        book_model.save()

        authors_names = book_payload.authors
        categories_names = book_payload.categories

        for author_name in authors_names:
            author_model = AuthorModel.get_by_name(name=author_name)

            if not author_model:
                author_model = AuthorModel(name=author_name)
                author_model.save()

            book_author_model = BookAuthorModel(book_id=book_model.id, author_id=author_model.id)
            book_author_model.save()

        for category_name in categories_names:
            category_model = CategoryModel.get_by_name(name=category_name)

            if not category_model:
                category_model = CategoryModel(name=category_name)
                category_model.save()

            book_category_model = BookCategoryModel(book_id=book_model.id, category_id=category_model.id)
            book_category_model.save()

        return book_model
