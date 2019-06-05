# Secret Share

## Installation

Required packages are managed by `pipenv` so you need to have it installed in your system.
Go to directory app and run following commands
```bash
$ pipenv install --dev
$ pipenv shell
$ ./manage.py migrate
$ ./manage.py runserver
```
And then application should be available under http://localhost:8000

Admin panel is available under `[APP_URL]/admin`

## API endpoints

### Authorization

Secured endpoints required token which can be fetched using authorization endpoint.
Token should be set as header:

`Authorization: Token [TOKEN_VALUE]`

`[APP_URL]/api/login/` *POST*

#### Request:
* **username** (*string*, *required*)
* **password** (*string*, *required*)

#### Response:
* **token** (*string*)

### Create item

Secured endpoint - authorization header is required.

In order to send file you need to set header `Content-Type: application/x-www-form-urlencoded`

`[APP_URL]/api/item/` *POST*

#### Request:
* **url** (*URL string*)*
* **file** (*file object*)*

*Only one of these fields can be sent at once.

#### Response:
* **url** (*URL string*) URL address to endpoint with access to created item 
* **password** (*string*)


### Get item

`[APP_URL]/api/item/[UUID]/` *GET*

#### Request:
* **password** (*string*, *required*)

#### Response:
Redirect to url address or to file


### Get stats

`[APP_URL]/api/stats` *GET*

Secured endpoint - authorization header is required.
