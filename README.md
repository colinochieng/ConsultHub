# ConsultHub API

- This is an API-based program that allows users to login under certain fields (e.g. Developer, Electrician, etc.) and post or answer questions related to their field. Users can also subscribe to notifications from their own or general channels.
- This API provides functionalities to facilitate querying among users within specific categories and channels. Users can post questions, receive notifications, respond to queries, and manage their notification preferences.

---

## Getting Started

To use this API, you need to have a valid account and an API key. You can register for an account and get an API key at [http://consulthub/register](http://consulthub.com/register).

## Authentication

The API requires user authentication. To access the endpoints, users need to log in with their username and password associated with their specific field (e.g., Developer, Electrician).

### Endpoints

**_User Authentication_**

- _POST_ `/api/auth/login/` Authenticates a user and returns an access token for further API requests.
- _POST_ `/api/auth/logout/`: Logs out the user and invalidates the access token.

To authenticate your requests:

- You need to include your API key as a query parameter in every request. For example:

```
http://consulthub.com/api/channel/{channel}?api_key=YOUR_API_KEY
```

**OR**

- You should include your API key in the custom header X-Api-Token of your HTTP request

```
X-Api-Token: YOUR_API_KEY
```

**_User profile_**

- _GET_ `/api/users/{username}/`: Retrieves user details by username.
- _PUT_ `/api/users/{username}/`: Updates user profile information.

## Nofications

- _PUT_ `/api/users/{username}/notifications/`: Updates user notification settings for their subscribed channels (own and general channels).

## Querying Channels

Users can post queries, respond to queries, and manage their notification settings.

### Endpoints

- _GET_ `/api/channel/{channel}/`: Returns a JSON representation of questions posted to all channels with their responses (paginated) if query parameter all is true else defaults to `general` channel or else you need to specify the channel name as a query parameter. For examples:

  - `http://consulthub.com/api/channel/`
  - `http://consulthub.com/api/channel/?all=true`
  - `http://consulthub.com/api/channel/?channel=developer`

- _GET_ `/api/channel/{channel}`: Returns a JSON representation of questions posted to the channel with their responses (paginated).

  ```
  http://consulthub.com/api/channel/developer/
  ```

- _GET_ `/api/channel/{channel}/username/`: Returns a JSON representation of the questions the user posted and their responses, together with the questions they responded to with their responses:

```
http://consulthub.com/api/channel/developer/john_smith/
```

- _GET_ `/api/channel/{channel}/multi/?name=John&name=Alice&name=Bob`: Returns a JSON representation of the questions the named users posted and their responses, together with the questions they responded to with their responses:

```
http://consulthub.com/api/channel/developer/multi?name=John&name=Alice&name=Bob
```

- _GET_ `/api/channel/{channel}/{username}/{question_title}/`: Returns a JSON representation of the question with the specified title, if it is valid and associated with the user. If it is the user who posted the question, it shows the responses from others. Otherwise, it shows the response made by the user to the question.

```
  http://consulthub.com/api/channel/{channel}/john_smith/How_to_use_Django/
```

- _GET_ `/api/channel/{channel}/{username}/{question_id}/`: Returns a JSON representation of the question with the specified ID, if it is valid and associated with the user. If it is the user who posted the question, it shows the responses from others. Otherwise, it shows the response made by the user to the question. You need to specify the channel name, the username, and the question ID as query parameters. For example:

```
http://consulthub.com/api/channel/developer/john_smith/0ca920885239ee74f292e7d3/
```

- _GET_ `/api/channel/{channel}/{question_title}/`: Returns a JSON representation of the question with the specified title and its responses, if it is associated with the channel. Responses have embedded info of the responder.

```
http://consulthub.com/api/channel/developer/How_to_use_Django/
```

- _GET_ `/api/channel/{channel}/{question_id}/`: Returns a JSON representation of the question with the specified ID and its responses, if it is associated with the channel. Responses have embedded info of the responder.

```
http://consulthub.com/api/channel/{channel}/0ca920885239ee74f292e7d3/
```

- _GET_ `/api/general`: Similar to `/api/channel/`. Returns a JSON representation of questions posted to the general channel and their responses (paginated).

```
http://consulthub.com/api/general/
```

## Response Format

The response format for each endpoint is a JSON object with the following fields:

- `status`: A string indicating the status of the request. Possible values are `success` or `error`.
- `message`: A string providing more details about the status of the request. For example, `Invalid API key` or `Question not found`.
- `data`: A JSON object containing the requested data, if the request was successful. The data object has the following fields:

  - `question`: A JSON object representing the question, if the endpoint is for a single question. The question object has the following fields:

    - `id`: A string representing the unique ID of the question.
    - `title`: A string representing the title of the question.
    - `content`: A string representing the content of the question.
    - `author`: A string representing the username of the author of the question.
    - `channel`: A string representing the channel of the question.
    - `created_at`: A string representing the date and time when the question was created, in ISO 8601 format.
    - `updated_at`: A string representing the date and time when the question was last updated, in ISO 8601 format.

  - `questions`: A JSON array of question objects, if the endpoint is for multiple questions. Each question object has the same fields as described above.

  - `responses`: A JSON array of response objects, if the endpoint is for a question or questions with responses. Each response object has the following fields:

    - `id`: A string representing the unique ID of the response.
    - `content`: A string representing the content of the response.
    - `author`: A string representing the username of the author of the response.
    - `question_id`: A string representing the ID of the question that the response is for.
    - `created_at`: A string representing the date and time when the response was created, in ISO 8601 format.
    - `updated_at`: A string representing the date and time when the response was last updated, in ISO 8601 format.

  - `page`: An integer representing the current page number, if the endpoint is paginated.
  - `per_page`: An integer representing the number of items per page, if the endpoint is paginated.
  - `total_pages`: An integer representing the total number of pages, if the endpoint is paginated.
  - `total_items`: An integer representing the total number of items, if the endpoint is paginated.

## Examples

Here are some examples of requests and responses for each endpoint:

- `/api/channel/developer/`

  Request:

  `http://consulthub.com/api/channel/developer/?api_key=YOUR_API_KEY`

  Response:

  ```json
  {
    "status": "success",
    "message": "Questions retrieved successfully",
    "data": {
      "questions": [
        {
          "id": "123",
          "title": "How to use Django?",
          "content": "I am new to Django and I want to learn how to use it for web development. Can anyone recommend some good resources or tutorials?",
          "author": "john",
          "channel": "developer",
          "created_at": "2023-12-11T07:39:10Z",
          "updated_at": "2023-12-11T07:39:10Z"
        },
        {
          "id": "124",
          "title": "What is the best IDE for Python?",
          "content": "I am looking for a good IDE for Python development. I have heard of PyCharm, VS Code, and Spyder. Which one do you prefer and why?",
          "author": "mary",
          "channel": "developer",
          "created_at": "2023-12-11T07:41:15Z",
          "updated_at": "2023-12-11T07:41:15Z"
        }
      ],
      "page": 1,
      "per_page": 10,
      "total_pages": 1,
      "total_items": 2
    }
  }
  ```

- `/api/channel/{channel}/{username}/`

  Request:

  `http://consulthub.com/api/channel/developer/john/?api_key=YOUR_API_KEY`

  Response:

  ```json
  {
    "status": "success",
    "message": "User questions and responses retrieved successfully",
    "data": {
      "questions": [
        {
          "id": "123",
          "title": "How to use Django?",
          "content": "I am new to Django and I want to learn how to use it for web development. Can anyone recommend some good resources or tutorials?",
          "author": "john",
          "channel": "developer",
          "created_at": "2023-12-11T07:39:10Z",
          "updated_at": "2023-12-11T07:39:10Z"
        }
      ],
      "responses": [
        {
          "id": "456",
          "content": "I think VS Code is the best IDE for Python. It has a lot of features and extensions that make coding easier and faster. It also has a built-in terminal and debugger that are very useful.",
          "author": "john",
          "question_id": "124",
          "created_at": "2023-12-11T07:43:20Z",
          "updated_at": "2023-12-11T07:43:20Z"
        }
      ]
    }
  }
  ```

- `/api/channel/{channel}/{username}/{question_title}`
  Request:

  `https://consulthub.com/api/channel/developer/john/How_to_use_Django?api_key=YOUR_API_KEY`

  Response:

  ```json
  {
    "status": "success",
    "message": "Question and responses retrieved successfully",
    "data": {
      "question": {
        "id": "123",
        "title": "How to use Django?",
        "content": "I am new to Django and I want to learn how to use it for web development. Can anyone recommend some good resources or tutorials?",
        "author": "john",
        "channel": "developer",
        "created_at": "2023-12-11T07:39:10Z",
        "updated_at": "2023-12-11T07:39:10Z"
      },
      "responses": [
        {
          "id": "456",
          "content": "You can check out the official Django documentation, which has a lot of useful information and examples. You can also follow this tutorial from [Django Girls], which is a great introduction to Django and web development in general.",
          "author": "mary",
          "question_id": "123",
          "created_at": "2023-12-11T07:45:30Z",
          "updated_at": "2023-12-11T07:45:30Z"
        },
        {
          "id": "457",
          "content": "I would recommend this course from [Udemy], which covers the basics of Django and how to build a fully functional website with it. It also teaches you how to use HTML, CSS, Bootstrap, and JavaScript to make your website look nice and interactive.",
          "author": "bob",
          "question_id": "123",
          "created_at": "2023-12-11T07:48:40Z",
          "updated_at": "2023-12-11T07:48:40Z"
        }
      ]
    }
  }
  ```

---

## Contributing

We welcome any contributions from developers who are interested in improving this project. You can clone or fork this repository and make your own changes. To run the project locally, you need to install the Python dependencies by running:

```
pip install -r requirements.txt
```

`NOTE: `

- The database constitutes of two collection `[users, Queries]`.This database design follows the guideline of storing together what needs to be accessed together. By embedding the responses inside the questions, one can avoid performing multiple queries or joins to fetch the related data. However, this design also has some trade-offs. For example, you need to consider the size limit of a document in MongoDB, which is 16 MB. If you expect to have a lot of responses for each question, you might need to split them into separate documents or collections. You also need to consider the update frequency of your data. If you expect to have frequent updates or deletions of responses, you might need to use a different schema or indexing strategy to optimize your operations
- Please note that the API is currently only configured to accept gmail accounts for authentication. If you want to use other email providers, you need to modify the code accordingly.

---

## Collections

1. **Users Collection**:

_Fields:_

- \_id (ObjectId)
- username (String, Unique)
- password (String, Hashed)
- field (String(e.g., "Developer"))
- notifications (Embedded document) e.g

```json
{
  "own_channel": true,
  "general_channel": false
}
```

2. **Queries Collection:**
   _Fields:_

- \_id (ObjectId)
- title (String)
- author (String {Reference to User (questioner)})
- channel (String (e.g. developer))
- query_text (String)
- created_at (Datetime)
- responses (Embedded Document)

**_`Response document body`_**

```javaScript
{
      "_id": ObjectId("60c9a0f8b8f2a1c4f3a7e6a3"),
      "content": "Hello world",
      "author": "Mark",
      "created_at": new Date()
}
```

---

## DevDependencies

This project uses the following Python libraries as dev dependencies:

- [Flask](https://flask.palletsprojects.com/en/3.0.x/): A lightweight web framework for used for building the API's endpoints.

![Flask logo](https://flask.palletsprojects.com/en/2.0.x/_images/flask-logo.png)

- [Redis](https://redis.io/): An used for caching.

![Redis logo](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRXBM7fu342qxqm35OYtXyzQGu4Ef0k62-o3uojpg11o8l9AdMUT1Ucl73U62fqKL0Zn4Y&usqp=CAU)

- [MongoDB](https://www.mongodb.com/): A stores data. Used as the base for storage

## ![MongoDB logo](https://webassets.mongodb.com/_com_assets/cms/mongodb_logo1-76twgcu2dm.png)

---

## Author

colinochieng@gmail.com
