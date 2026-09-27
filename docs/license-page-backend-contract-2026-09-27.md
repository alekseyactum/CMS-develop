# Лицензия: backend-контракт

Дата: 2026-09-27. Тип: `lawyer_license_page`. Исходная база: `c085375`.

Реализация в исходниках; публикация кода не создаёт контент и редиректы в БД.
Frontend CMS и сайта не изменены. Приём и доставка заявок не реализуются на этом этапе.

## Маршрут и создание

- Единственная локаль `uk`, фиксированный путь `/license`, без региональных вариантов.
- Bootstrap, routing, lifecycle и public payload отклоняют неподдерживаемые варианты.
- Матрицы и их диагностика не ожидают RU/EN-копии.
- В публичных alternates нет RU/EN-переводов. Sitemap использует существующий каталог
  опубликованных страниц; отдельные страницы для языковых алиасов создавать нельзя.
- Новые таблицы, миграции, ERP-поля, секреты и настройки Cloud Run не нужны.

Существующие административные API (с авторизацией и штатными CMS permissions):

```http
GET /api/admin/page-schemas/lawyer_license_page
POST /api/admin/pages/bootstrap
```

```json
{ "pageType": "lawyer_license_page", "locale": "uk" }
```

Bootstrap создаёт неполные черновики восьми секций, включая SEO; это не публикация
заглушек. Существующие `authoring`, `sections/:slotKey/editor`, `editor/draft`,
`editor/validate`, `preview`, `publish`, история и rollback работают без отдельного
семейства endpoint. Общие глобальные header/footer не копируются в эту страницу.

```http
GET /api/admin/page-workbench/page-types/lawyer_license_page?locale=uk
GET /api/admin/pages/:pageId/authoring
GET /api/admin/pages/:pageId/sections/:slotKey/editor
POST /api/admin/pages/:pageId/sections/:slotKey/editor/draft
POST /api/admin/pages/:pageId/sections/:slotKey/editor/validate
POST /api/admin/pages/:pageId/preview
POST /api/admin/pages/:pageId/publish
```

Тела запросов editor/publish и concurrency/version checks остаются штатными: новый
тип не отменяет их. Черновики разрешено сохранять неполными. Публикация и пересборка
опубликованной страницы проверяют вложенные данные и готовность всех изображений.
Сохранение черновика передаёт полный объект секции, не partial PATCH: обязательные
ключи верхнего уровня должны присутствовать с верными типами. Пустые строки и
незавершённые массивы допустимы; вместо отсутствующего media ID передаётся `""`, не
`null`. Полная диагностика остаётся в редакторе и явной валидации.
Общий endpoint независимой публикации секции теперь проверяет сохранённые привязки:
`with_page` и непривязанная page-owned секция возвращают `SECTION_NOT_INDEPENDENT`,
даже если клиент передал поддельную schema. Публиковать их нужно через страницу;
независимые глобальные секции сохраняют свой workflow.

## Контент секций

Все семь содержательных секций обязательны, page-owned, `with_page`, с фиксированным
порядком. Отключение и добавление произвольных секций не предусмотрены. Текст — plain
text, не HTML. Изображение — существующий `imageMediaId` плюс обязательный `imageAlt`.

| slotKey | Редактируемые поля |
| --- | --- |
| `seo` | Стандартный SEO-контракт; canonicalPath, если задан, только `/license` |
| `license_hero` | `eyebrow`, `title`, `description`, `imageMediaId`, `imageAlt`, `ctaLabel` |
| `license_roles` | `title`, `imageMediaId`, `imageAlt`, `items`: ровно 2 объекта `{role,title,description}`, по одному `lawyer` и `actum` |
| `license_model` | `accentText`, `description` |
| `license_support` | `title`, `description`, `items`: ровно 4 объекта `{title,description,imageMediaId,imageAlt}` |
| `license_formats` | `items`: ровно 2 объекта `{format,title,description,ctaLabel}`, по одному `individual_practice` и `office` |
| `license_expectations` | `title`, `items`: ровно 2 объекта `{description,imageMediaId,imageAlt}` |
| `license_application` | `title`, `description`, `labels`, `submitLabel`, `unavailableText` |

`labels` содержит ровно согласованные подписи:

```json
{
  "name": "Ваше ім’я",
  "phone": "Телефон",
  "city": "Місто",
  "cooperationFormat": "Формат співпраці",
  "about": "Кілька слів про вашу спеціалізацію та плани",
  "individualPractice": "Індивідуальна адвокатська практика",
  "office": "Офіс у своєму місті"
}
```

Лимиты: заголовки/подписи/идентификаторы — 200 символов, alt — 500, описания — 10 000,
`unavailableText` — 1 000. Названия полей формы, обязательность, коды форматов и
действия не редактируются в CMS. Добавление email/резюме через labels не допускается.
Порядок массивов сохраняется; анимация четырёх карточек — ответственность frontend.

## Публичный payload и CTA

Стандартный snapshot: `pageType`, `locale: "uk"`, `route: "/license"`, `seo`, `sections`.
Контент секции находится в обычном `sections[].payload`.

Для изображений backend добавляет `imageUrl` рядом с `imageMediaId`/`imageAlt`, включая
вложенные items. URL получается из media service, не из пользовательского JSON. На
публикации требуется active/uploaded image с serving path; missing/archived/pending
media блокируют новую публикацию и пересборку, но не перезаписывают старый snapshot.
В публичном payload сохраняется нормализованный media ID без крайних пробелов,
чтобы существующая проверка использования не позволяла удалить опубликованное фото.

В hero backend добавляет:

```json
{
  "cta": {
    "kind": "scroll_to_form",
    "href": "#license-application",
    "cooperationFormat": null
  }
}
```

В каждом `license_formats.items[]` аналогичный `cta`, но `cooperationFormat` равен
машинному коду соответствующей карточки. Frontend скроллит/фокусирует общую форму,
предвыбирает формат и оставляет возможность изменить выбор. Произвольного target URL нет.

В `license_application.payload` сервер добавляет `form`:

```json
{
  "kind": "license_partnership",
  "locale": "uk",
  "anchorId": "license-application",
  "fields": [
    { "key": "name", "type": "text", "required": true },
    { "key": "phone", "type": "tel", "required": true },
    { "key": "city", "type": "text", "required": true },
    { "key": "cooperationFormat", "type": "select", "required": true },
    { "key": "about", "type": "textarea", "required": false }
  ],
  "options": [
    { "value": "individual_practice", "label": "Індивідуальна адвокатська практика" },
    { "value": "office", "label": "Офіс у своєму місті" }
  ],
  "submission": {
    "enabled": false,
    "endpoint": null,
    "reason": "LICENSE_APPLICATION_DELIVERY_NOT_CONFIGURED"
  }
}
```

`options[].label` берутся из CMS labels. Поля `form`, `cta` и `imageUrl` вычисляются
сервером, не принимаются как доверенные настройки редактора. Сейчас frontend должен
показывать `unavailableText`, отключать отправку и не имитировать успех. API вакансий
использовать нельзя. Не собирать/отправлять персональные данные без согласованного
приёмника. Реальную доставку в email и ERP внедряем отдельной задачей перед запуском.

## Навигация CMS и входящие ссылки

`GET /api/admin/navigation` во всех языках включает пункт «Ліцензія» с
`href: "/uk/admin/pages/lawyer_license_page"`, `target.locale: "uk"`. Его индикаторы
считаются по UK. Frontend должен учитывать href/target.locale, а не приставлять
текущий язык к относительному route. Матрица отдаёт `locales: ["uk"]`; прямой RU/EN
запрос матрицы возвращает 400 `PAGE_WORKBENCH_LOCALE_UNSUPPORTED`.

Карьерный баннер любой локали может выбрать опубликованную национальную UK-страницу
этого типа по `/license`. Для других целей правило одинаковой локали сохранено.
Получить кандидата: `GET /api/admin/pages?pageType=lawyer_license_page&locale=uk`;
проверять `currentSnapshot.status === "published"`, а не только существование черновика.
Сохранить её `pageId` в существующий `career_partner_banner.targetPageId` и опубликовать
потребителя. Само появление License не пересобирает автоматически все старые баннеры.

`hasLicensePartnership` адвоката не изменяется. Новое публичное поле со ссылкой в
snapshot адвоката не добавлено. При подключении отметки frontend отдельно учитывает
опубликованность `/license`; наличие флага адвоката не означает доступность страницы.

## Языковые 301: контролируемое включение

Специального раннего redirect в обход реестра нет. Применяется существующий registry,
проверки владения адресом и доступности целевой опубликованной страницы.
После развёртывания кода и публикации контента необходимо:

1. Проверить существующие правила и владельцев `/ru/license` и `/en/license`.
   При конфликте остановиться, не перезаписывать существующие записи.
2. Подготовить два правила через `POST /api/admin/redirects`, например
   `{ "oldUrl": "<canonical-origin>/ru/license", "newUrl": "<canonical-origin>/license" }`
   и аналогично для `/en/license`. Это шаблоны; заменить origin разрешённым origin
   конкретного окружения. Backend разрешает newUrl в targetPageId.
3. Получить актуальные `id` и `version` подготовленных правил. Активировать через
   `POST /api/admin/redirects/activate` с `{ "records": [{"id":"...","version":1}] }`,
   подставляя фактические версии, не константу 1. Не активировать неопубликованную цель.
4. Проверить `POST /api/public/routes/resolve` с полным `url`: `/license` — страница,
   оба алиаса — один 301 непосредственно на канонический URL. Решение resolver применяет
   сервер сайта как реальный HTTP status/Location, не клиентский JavaScript.
5. При снятии цели с публикации — 404; отключённое вручную правило само не включается
   после новой публикации. Инфраструктурные ошибки используют штатную обработку resolver.

Данные правил в общую БД в ходе разработки не внесены. Один deploy не делает алиасы
активными. Полноценная проверка HTTP 301 проводится после настройки и интеграции сайта.

## Приёмка после развёртывания

Создать UK-черновик; заполнить SEO и семь секций; загрузить изображения; проверить
preview и опубликовать. Проверить, что 3/5 support-карточек, дубли форматов/ролей,
неполные поля и неготовые изображения дают отказ без изменения опубликованной версии.
Создать новую версию секции и страницы, проверить историю/откат. Проверить UK-only
меню/индикаторы в RU/EN CMS, опубликованный публичный JSON, баннеры карьеры и языковые
редиректы. Публичная форма остаётся явно недоступной до отдельного этапа доставки.

## Локальная проверка реализации

2026-09-27: `npm run typecheck`, `npm run build`, `npm test` — успешно.
Полный набор: 1113 тестов, 0 ошибок, 0 пропусков; `git diff --check` — без замечаний.
Это локальные автоматические проверки, не smoke на Cloud Run и не проверка реальной БД.
Новые зависимости не устанавливались; используется существующая совместимая копия
`node_modules`. Деплой, создание контента и активация редиректов не выполнялись.
