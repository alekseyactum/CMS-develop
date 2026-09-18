# Выкат runtime-индикаторов глобальных секций — 2026-09-18

По запросу владельца исправление CMS backend опубликовано и развёрнуто на develop и release.
CMS-front и публичный сайт не изменялись и не развёртывались.

## Код и проверки

Backend-коммит: `f394448fef9818a1be7eef006021c44f7c8005bf` —
`fix: exclude runtime global sections from publication indicators`.
Удалённые ветки develop, release и `codex/footer-runtime-indicators` указывают на этот коммит;
force-push не применялся. Спецификация опубликована коммитом CMS `6b6ad78`.

После push повторно пройдены 991/991 тестов (119 suites) и production TypeScript build.
Рабочее дерево backend чистое. Несвязанные изменения CMS/playbook не включались.

## Деплой

Preflight GCP прошёл. Использованы существующие git-triggered Cloud Build pipelines в проекте
`composite-ally-360719`, регион `europe-central2`; повторные ручные сборки не запускались.

| Окружение | Build ID | Новая ревизия | Предыдущая ревизия |
| --- | --- | --- | --- |
| develop | `9fc52d43-3fe6-4ba1-99f5-557459d683c8` | `cms-back-develop-00291-6ds` | `cms-back-develop-00290-nd7` |
| release | `69821cfb-543c-4c06-a5dd-78dc7a2c02a0` | `cms-back-release-00080-j6w` | `cms-back-release-00079-hjw` |

Обе сборки SUCCESS, завершены около 08:04 UTC. Новые ready-ревизии получают 100% трафика.
Образы ревизий содержат соответствующий Build ID. `/api/health` и `/api/ready` обоих окружений
подтвердили ожидаемые Build ID и полный SHA; подключение к БД — `ok`.
`/api/docs-json` подтверждает `publicationMode: versioned | runtime` в DTO summary, editor,
locale diagnostics и public content.

## Read-only функциональная проверка

На release вызваны под собственной учётной записью оператора:

- `GET /api/admin/global-sections/site_footer_practices/public-content?locale=uk`;
- `GET /api/admin/global-sections/site_footer_practices/locale-diagnostics`.

Получены runtime-режим, источник `practice_reference_data`, `editable: false`, пустой
`editableContent`, 19 элементов UK и нулевые errors/warnings. Для UK/RU/EN статус `ok`,
подпись «Формується автоматично», опубликованной версии нет. Это подтверждает, что
отсутствие версии больше не создаёт ложную ошибку секции.

На develop админский smoke ограничен ответом 403 `CMS_USER_NOT_FOUND`: текущая учётная
запись не заведена в CMS этого окружения. Права и пользователи не изменялись, чужая
идентичность не использовалась. Health/ready/OpenAPI develop проверены успешно.

Editor и общая navigation намеренно не вызывались: существующие GET-пути могут создавать
служебные записи/строки переводов. Живая UI-приёмка навигации этим smoke не подтверждена;
контракт навигации покрыт локальными тестами. За ограниченное окно 30 минут запросы
логов severity >= ERROR для обеих новых ревизий вернули 0 записей. Это не длительный мониторинг.

## Границы и ручная приёмка

Миграции, запуск migration job, перепубликация и редактирование контента не требуются и
не выполнялись. IAM, секреты, DNS и pipeline не менялись. Штатные backend pipelines обновляют
образ/конфигурацию migration job, но не исполняют его.

После обновления CMS проверить «Глобальные → Практики в футере»: нет ложной ошибки
«не опубликовано» и лишнего счётчика `0/1`; реальные предупреждения источника сохраняются.
Обычные версионные секции по-прежнему требуют публикации. Новый отдельный UI-бейдж
в рамках backend-изменения не добавлялся.

Предпочтительный откат — проверенный revert backend-коммита через существующий pipeline.
Аварийное переключение трафика на предыдущие ревизии из таблицы требует согласования.
Откат БД не нужен; откат backend вернёт прежний ложный индикатор.

Исходная спецификация: [runtime-global-section-indicators-2026-09-18.md](runtime-global-section-indicators-2026-09-18.md).
