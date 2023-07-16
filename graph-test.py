from flask import Flask
from flask_graphql import GraphQLView
import graphene
import requests

app = Flask(__name__)

# Define un tipo de objeto para los libros
class Book(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    author = graphene.String()

# Define una consulta GraphQL
class Query(graphene.ObjectType):
    books = graphene.List(Book, title=graphene.String())

    def resolve_books(self, info, title=None):
        base_url = 'https://openlibrary.org'
        search_term = 'Harry Potter'

        # Construye la URL completa con el endpoint '/search.json' y el query parameter 'title'
        url = f'{base_url}/search.json?'

        if title:
            url += f'title={title}'

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Mapea los datos de los libros a instancias de objetos Book
            books_data = data.get("docs", [])
            filtered_books = []
            for book in books_data:
                book_title = book.get("title", "")
                book_author = book.get("author_name", "")
                if book_title == title:
                    filtered_books.append(Book(
                        id=book.get("id", ""),
                        title=book_title,
                        author=book_author
                    ))
            return filtered_books
        else:
            print('Error al realizar la solicitud:', response.status_code)
            return []

# Crea el esquema de GraphQL
schema = graphene.Schema(query=Query)

# Configura la vista de GraphQL
view_func = GraphQLView.as_view('graphql', schema=schema, graphiql=True)

# Asigna la vista de GraphQL a la ruta '/graphql'
app.add_url_rule('/graphql', view_func=view_func)

if __name__ == '__main__':
    app.run()
