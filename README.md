![logo](./readme_assets/logo2.svg)

<a href="https://codecov.io/gh/Alstacon/ToDoCon" > <img src="https://img.shields.io/codecov/c/github/Alstacon/ToDoCon?color=EB66A5&style=plastic"></a>

### 📋 ToDoCon —
This is a web application for planning by category, with authorization via VK, Telegram bot and the ability to share goals.
___

![google](./readme_assets/google.svg) [todocon.ga](http://todocon.ga)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![telegram](./readme_assets/telegram.svg)[@todocon_bot](https://t.me/todocon_bot)
___
### Back-end functionality:
- Create/view/edit/delete boards, categories, goals and comments on them
- Setting the priority and deadline for each goal.
- Three levels of access to the board, including the ability to read and edit:

&nbsp;&nbsp;&nbsp;&nbsp;![table](./readme_assets/permission_table.svg)

- Login and password authorization or via a social network vk.com.
- Personal account with the ability to change login, password, first name, last name and email address.
- Telegram bot for viewing created categories and goals, with the function of creating new goals in existing categories.

___
## Tech stack:
![Python](https://img.shields.io/badge/%20-PYTHON-C083E5)&nbsp;&nbsp;
![Django](https://img.shields.io/badge/-DJANGO-EB66A5)&nbsp;&nbsp;
![DjangoREST](https://img.shields.io/badge/%20-DJANGO--REST-C083E5)&nbsp;&nbsp;
![Postgres](https://img.shields.io/badge/%20-POSTGRES-EB66A5)&nbsp;&nbsp;
![Docker](https://img.shields.io/badge/%20-DOCKER-C083E5)&nbsp;&nbsp;
___


## Usage:
1) Clone the repository
`git clone https://github.com/Alstacon/ToDoCon.git`.
2) Change `.env.example`'s file name for `.env` and fill it with valid parameters.
3) Run docker `docker-compose up --build -d`.
