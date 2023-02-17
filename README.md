![logo](./readme_assets/logo2.svg)
<a href="https://codecov.io/gh/Alstacon/ToDoCon" > <img src="https://img.shields.io/codecov/c/github/Alstacon/ToDoCon?color=EB66A5&style=plastic"  </a>

### 📋 ToDoCon —
Это веб-приложение для планирования по категориям, с авторизацией через VK, Telegram-ботом и возможностью шеринга целей.

___

![google](./readme_assets/google.svg) [todocon.ga](http://todocon.ga)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![telegram](./readme_assets/telegram.svg)[@todocon_bot](https://t.me/todocon_bot)
___
### Бэкенд функционал:
- Создание/просмотр/редактирование/удаление досок, категорий, целей и комментариев к ним.
- Три уровня доступа к доске, включающие возможность чтения и редактирования:

&nbsp;&nbsp;&nbsp;&nbsp;![table](./readme_assets/permission_table.svg)

- Авторизация по логину и паролю или через социальную сеть vk.com.
- Личный кабинет с возможностью смены логина, пароля, имени, фамилии и email-адреса.
- Telegram-бот для просмотра созданных категорий и целей, с функцией создания новых целей в имеющихся категориях.

___
## Стек:
![Python](https://img.shields.io/badge/%20-PYTHON-C083E5)&nbsp;&nbsp;
![Django](https://img.shields.io/badge/-DJANGO-EB66A5)&nbsp;&nbsp;
![DjangoREST](https://img.shields.io/badge/%20-DJANGO--REST-C083E5)&nbsp;&nbsp;
![Postgres](https://img.shields.io/badge/%20-POSTGRES-EB66A5)&nbsp;&nbsp;
![Docker](https://img.shields.io/badge/%20-DOCKER-C083E5)&nbsp;&nbsp;
___


## Запуск:
1) Клонируйте репозиторий
`git clone https://github.com/Alstacon/ToDoCon.git`.
2) Переименуйте файл `.env.example` в `.env` и заполните его валидными значениями.
3) Запустите докер `docker-compose up --build -d`.
