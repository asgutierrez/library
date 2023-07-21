# Library

![Base](docs/Base.png)

## Setup

Install Python https://www.python.org/

Version >= 3.10.11

Configure your IDE to use a virtual environment:

```sh
make project/venv
```

Install dependencies:

```shell
make deps/install/full 
```

Start local with a Mysql database:

Install Docker and Docker-compose under your machine

```shell
make docker/compose
```

```shell
./start_local_msql.sh 
```

## Environment Config

### API 

| Name                 | Desc                 | Default     |
|----------------------|----------------------|-------------|
| R5_TOKEN_TTL         | Token Time to Live   | 3600 * 24   |
| R5_LOG               | Logger Level         | INFO        |
| R5_SECRET_KEY        | Session Secret       | Random UUID |
| R5_DATABASE_HOSTNAME | Database Hostname    | None        |
| R5_DATABASE_NAME     | Database Table Name  | None        |
| R5_DATABASE_USER     | Database User        | None        |
| R5_DATABASE_PASSWORD | Database Password    | None        |
| R5_DRIVER            | Database Driver      | None        |


### Compose Ports

| Component | Name | Port Public | Port Internal |
|-----------|------|-------------|---------------|
| Mysql     | msql | 3306        | 3306          |
| This app  | api  | 8080        | 5000          |


#### API DOCS

# API de Libros
## Version: 1.0.0

### /books

#### GET
##### Summary:

Obtener libros

##### Description:

Obtiene una lista de libros filtrados por diferentes opciones.

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| title | query | Título del libro. | No | string |
| subtitle | query | Subtítulo del libro. | No | string |
| published_date | query | Fecha de publicación del libro. | No | date |
| publisher | query | Editorial del libro. | No | string |
| description | query | Descripción del libro. | No | string |
| author | query | Autor del libro. | No | string |
| category | query | Categoría del libro. | No | string |
| page | query | Número de página (para paginación). | No | integer |
| max_per_page | query | Número máximo de resultados por página (para paginación). | No | integer |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Lista de libros encontrados. |

#### POST
##### Summary:

Agregar un nuevo libro

##### Description:

Agrega un nuevo libro utilizando la información proporcionada.

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Libro agregado exitosamente. |
| 400 | Solicitud inválida. Puede faltar información o ser incorrecta. |

### /books/{book_id}

#### GET
##### Summary:

Obtener información de un libro por ID

##### Description:

Obtiene la información de un libro específico según su ID y la fuente proporcionada.

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| book_id | path | ID del libro a obtener. | No | integer |
| source | query | Fuente para obtener la información (INTERNAL, GOOGLE u OPENLIBRARY). | No | string |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Información del libro encontrada. |
| 404 | Libro no encontrado. |

#### DELETE
##### Summary:

Eliminar un libro por ID

##### Description:

Elimina el libro especificado por su ID.

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| book_id | path | ID del libro a eliminar. | No | integer |

##### Responses

| Code | Description |
| ---- | ----------- |
| 204 | Libro eliminado exitosamente. |
| 404 | Libro no encontrado. |
