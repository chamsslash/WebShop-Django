# WebShop — бэкенд маркетплейса (Django)

Простой бэкенд для практики фронтенда: каталог товаров, корзина, «внутренняя валюта»,
заказы, инвентарь купленного, регистрация и вход.
Есть готовый JSON API, его документация генерируется автоматически (Swagger).

> Инструкция написана для **macOS**. Для Windows есть отдельный раздел [в конце](#запуск-на-windows).

## Что нужно

- **Python 3.10+** (проверено на 3.14). Откройте **Терминал** (Spotlight `⌘ + Пробел` → «Терминал») и проверьте:

  ```bash
  python3 --version
  ```

  Если в ответ пришло `command not found` или macOS предлагает установить инструменты разработчика, поставьте Python одним из способов:
  - через [Homebrew](https://brew.sh): `brew install python`;
  - или скачайте установщик с [python.org](https://www.python.org/downloads/macos/).
- **Git**, чтобы скачать проект: `git --version`. Если его нет, macOS сама предложит установить Command Line Tools, соглашайтесь.
- Больше ничего не нужно: база данных SQLite, это один файл, создаётся сам.

## Запуск на Mac (первый раз)

```bash
git clone https://github.com/chamsslash/WebShop.git
cd WebShop/WeBs-main/chamsslash     # дальше все команды выполняются отсюда (здесь лежит manage.py)

python3 -m venv .venv               # создать виртуальное окружение (папка .venv)
source .venv/bin/activate           # активировать его: в начале строки появится (.venv)
pip install -r requirements.txt     # поставить зависимости
python manage.py migrate            # создать таблицы в БД
python manage.py seed               # залить тестовые данные
python manage.py runserver          # запустить сервер
```

В истории git остались тяжёлые гифки (~130 МБ), поэтому `git clone` может идти несколько минут.

Когда появится строка `Starting development server at http://127.0.0.1:8000/`, откройте в браузере http://127.0.0.1:8000/api/docs/.

Остановить сервер: `Control + C` в окне терминала.

> Внутри активированного `.venv` команды `python` и `python3` равнозначны. Без него на Mac работает только `python3`.

## Запуск на Mac (последующие разы)

```bash
cd путь/до/WebShop/WeBs-main/chamsslash
source .venv/bin/activate
python manage.py runserver
```

Подсказка: в Терминал можно перетащить папку из Finder, и он сам вставит её путь после `cd `.

## Что открыть

| Адрес | Что там |
|---|---|
| http://127.0.0.1:8000/api/docs/ | **Swagger: все ручки API, можно вызывать прямо из браузера** |
| http://127.0.0.1:8000/api/redoc/ | та же документация в виде удобной для чтения страницы |
| http://127.0.0.1:8000/api/schema/ | OpenAPI-схема (YAML), из неё можно генерировать TS-типы и клиенты |
| http://127.0.0.1:8000/main/ | старый сайт на Django-шаблонах, можно взять за образец |
| http://127.0.0.1:8000/admin/ | админка: добавлять и редактировать товары, категории, картинки, пользователей |

## Тестовые пользователи (после `seed`)

| Логин | Пароль | Что умеет |
|---|---|---|
| `admin` | `admin` | вход в админку `/admin/` |
| `test` | `test12345` | обычный покупатель, баланс 10000 |

В базе 3 категории (`stickers`, `avatars`, `gifs`) и 20 товаров с картинками (`product-1` … `product-20`).

## Как работать с API с фронтенда

Документация по каждой ручке (параметры, тело запроса, ответы) находится в Swagger, `/api/docs/`.
Ниже то, что Swagger не объясняет.

### Авторизация через cookie

Токенов нет, авторизация сессионная: после `POST /api/auth/login/` браузер сам хранит cookie `sessionid`
и отправляет её со всеми запросами. В `fetch` для этого указывайте `credentials: 'include'`.

### CSRF-токен для POST, PATCH и DELETE

Django защищается от CSRF, поэтому к каждому изменяющему запросу нужен заголовок `X-CSRFToken`
со значением cookie `csrftoken`. Cookie выдаёт `GET /api/csrf/`, вызовите его один раз при старте приложения.

**После логина и регистрации токен меняется**, поэтому всегда читайте его из cookie заново, а не сохраняйте в переменную.

```js
function getCookie(name) {
  return document.cookie.split('; ').find(c => c.startsWith(name + '='))?.split('=')[1];
}

async function api(path, { method = 'GET', body } = {}) {
  const res = await fetch(path, {
    method,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  return res.status === 204 ? null : res.json();
}

await api('/api/csrf/');                                              // получить cookie
await api('/api/auth/login/', { method: 'POST', body: { username: 'test', password: 'test12345' } });
const products = await api('/api/products/?category=gifs&page=1');   // { count, next, previous, results }
await api('/api/cart/add/', { method: 'POST', body: { product_id: 1 } });
const cart = await api('/api/cart/');                                 // { items, total_price, total_quantity }
```

Корзина работает и без логина, она привязана к сессии. При входе или регистрации анонимная корзина переносится в аккаунт.

### Ответы с ошибками

- `403 {"detail": "Authentication credentials were not provided."}`: нужен логин.
- `403 {"detail": "CSRF Failed: ..."}`: не передан или устарел `X-CSRFToken`.
- `400 {"success": false, "error": "..."}`: бизнес-ошибка (товар не найден, мало денег, пустая корзина).
- `400 {"username": ["..."], ...}`: ошибки валидации по полям (регистрация).

Цены приходят строками (`"60.00"`), это нормально для денег. Для вычислений приводите через `Number(...)`.

### Если фронтенд крутится на отдельном dev-сервере (Vite, CRA и т.п.)

Самый простой вариант — проксировать запросы к бэку, тогда cookie и CSRF работают без настроек CORS.
Пример для Vite (`vite.config.js`):

```js
export default {
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/media': 'http://127.0.0.1:8000',   // картинки товаров
    },
  },
};
```

На фронте запросы делайте на относительные пути (`/api/products/`), без `http://127.0.0.1:8000`.
Порты 5173 (Vite) и 3000 (CRA) уже разрешены в `CSRF_TRUSTED_ORIGINS` в `chamsslash/settings.py`.
Для другого порта допишите его туда.

## Полезное

- **Сбросить базу до тестовых данных:** удалить файл `db.sqlite3`, затем `python manage.py migrate` и `python manage.py seed`.
- **Добавить свои товары:** через админку `/admin/` → «Продукты».
- **Включить django-debug-toolbar** (панель отладки на HTML-страницах): `DEBUG_TOOLBAR=1 python manage.py runserver`.
- **Запустить на другом порту:** `python manage.py runserver 8001`.
- **Открыть с телефона в той же Wi-Fi сети:** `python manage.py runserver 0.0.0.0:8000`, узнать IP Мака командой `ipconfig getifaddr en0` и зайти с телефона на `http://<этот-IP>:8000`.

## Где что лежит

```
chamsslash/      настройки (settings.py) и корневые URL
api/             JSON API: views.py (ручки), serializers.py (форматы данных), urls.py
main/            товары и категории (models.py), страницы каталога
carts/           модель корзины, страница корзины
users/           пользователь (баланс money), инвентарь, вход и регистрация на шаблонах
templates/       HTML-шаблоны старого сайта
static/styles/   CSS старого сайта
media/           загруженные картинки товаров и аватарок
```

## Проблемы

| Симптом | Что делать |
|---|---|
| `Error: That port is already in use` | сервер уже запущен в другом окне; запустите на другом порту, `runserver 8001` |
| `no such table: ...` | не выполнили `python manage.py migrate` |
| Каталог пустой | не выполнили `python manage.py seed` |
| `ModuleNotFoundError: No module named 'django'` | не активировано окружение: `source .venv/bin/activate` |
| `zsh: command not found: python` или `pip` | окружение не активировано (без него на Mac есть только `python3`) |
| `externally-managed-environment` при `pip install` | ставите пакеты мимо `.venv`; сначала `source .venv/bin/activate` |
| Swagger открывается белым экраном | его интерфейс грузится с CDN jsdelivr, нужен интернет |

## Запуск на Windows

Вариант для будущих пользователей; всё, кроме команд ниже, совпадает с инструкцией для Mac.

1. Поставьте Python с [python.org](https://www.python.org/downloads/windows/). **В установщике отметьте галочку «Add python.exe to PATH».**
2. Поставьте [Git for Windows](https://git-scm.com/download/win).
3. В **PowerShell**:

```powershell
git clone https://github.com/chamsslash/WebShop.git
cd WebShop\WeBs-main\chamsslash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

В следующие разы: `cd` в папку, затем `.venv\Scripts\Activate.ps1` и `python manage.py runserver`.

Отличия от Mac:

| На Mac | На Windows |
|---|---|
| `python3` | `python` |
| `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` (в cmd: `.venv\Scripts\activate.bat`) |
| `DEBUG_TOOLBAR=1 python manage.py runserver` | `$env:DEBUG_TOOLBAR=1; python manage.py runserver` |
| `ipconfig getifaddr en0` | `ipconfig`, строка «IPv4-адрес» |

Если PowerShell пишет `...Activate.ps1 cannot be loaded because running scripts is disabled`, выполните один раз
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` и повторите активацию.
