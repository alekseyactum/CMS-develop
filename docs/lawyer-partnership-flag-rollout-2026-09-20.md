# Флаг лицензионного партнёрства в публичном профиле — 2026-09-20

## Область

Пользователь подтвердил commit/push/deploy CMS backend в develop и release. Фронтенды,
страница лицензии, ERP, миграции, конфигурация и опубликованные снимки в эту выкладку не входят.

Backend-коммит: `3c5ec012e6311de879ca2831c7d15ec29e4b4bbc` в `re-actum/cms-back`.
Атомарно запушен в `develop`, `release`, `codex/lawyer-partnership-flag` от общей базы
`4f407b33ced6232676898e12187648d7ffd38574`.

## Контракт

- `lawyer_profile.payload.hasLicensePartnership` — `true`, `false` или `null` из ERP.
- Отметку показывать только при строгом `true`; `null` означает неизвестное значение.
- Значение не зависит от языка страницы, номера адвокатского свидетельства или названия организации.
- Название организации остаётся в ERP/admin API, в публичный профиль не добавляется.
- Новых URL, текстов отметки и редактируемых CMS-полей нет.
- Обычный resolver добавляет колонку к существующему запросу без дополнительного обращения к БД.
- Diagnostic runtime override не может заменить ERP-флаг. Остальные override-поля сохраняются.
- Nullable-валидация включена только для нового поля, не для остальных boolean-полей.

Миграция не нужна: исходная колонка уже существует. Документация backend:
`cms-back/docs/lawyer-license-partnership.md`.

## Выкладка

Playbook preflight прошёл для `composite-ally-360719`, `europe-central2`.
Использованы существующие Cloud Build triggers, pipeline не менялся.

| Окружение | Успешный build | Новая ready revision (100% traffic) | Предыдущая ready revision |
| --- | --- | --- | --- |
| develop | `0a6c7e71-3beb-4841-87f3-be62b005ddb1` | `cms-back-develop-00295-wml` | `cms-back-develop-00294-xxq` |
| release | `f2483246-58d3-48c3-9ee1-f08ef114df57` | `cms-back-release-00084-9jm` | `cms-back-release-00083-929` |

Сборки завершились SUCCESS 20.09.2026: develop в `08:00:49 UTC`, release в `08:01:07 UTC`.
Authenticated `/api/health` и `/api/ready` на обоих сервисах подтвердили точные SHA/build,
статусы `ok`/`ready` и `dependencies.database.status=ok`.

Release `GET /api/admin/page-schemas/lawyer_page` подтвердил новое поле:
`{field: "hasLicensePartnership", contentShape: "boolean", requirement: "optional", nullable: true}`.
На develop тот же read-only запрос от настоящего оператора вернул 403: CMS-доступ оператора
недоступен. Роли и пользовательская идентичность не подменялись. Версия develop подтверждена
через Cloud Run и authenticated health/ready; admin-schema smoke выполнен только на release.

Запрос ERROR-логов обеих новых ревизий за ограниченное окно после smoke вернул пустой список.
Это проверка текущего окна, не обещание длительного мониторинга.
После push повторно прошли 1026/1026 тестов (119 suites), typecheck и build. Рабочая backend-ветка чистая.
Нормальный pipeline обновил migration-job image/config, но сами jobs не запускались.

## Снимки и ручная проверка

Код сам не переписывает существующие снимки страниц. После отдельного разрешения нужно
пересобрать нужные опубликованные страницы адвокатов, чтобы новое поле появилось в их ответах.
Preview/новая публикация получает текущий флаг; старый снимок может пока не содержать поле.
Автоматическое обновление страниц при изменении ERP-признака этой задачей не добавлялось.

Проверка после пересборки: найти runtime-секцию `lawyer_profile` в публичном ответе и проверить
`hasLicensePartnership` для true/false/неизвестного значения; убедиться, что поля организации нет.
Для UK/RU/EN источник флага одинаковый, но отдельные снимки могут иметь разное время сборки.

Rollback: revert backend-коммита через существующий git-based pipeline; экстренный возврат traffic
на предыдущую ревизию требует отдельного подтверждения. Схему/данные не удалять. Поскольку снимки
в этом rollout не меняются, отдельного content rollback не требуется.
