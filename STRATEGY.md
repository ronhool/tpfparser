# Стратегия развития Typefeed Parser

## 🎯 Цель: Быть на шаг впереди конкурентов

## 📊 Текущее состояние
- **31 источник** (4 RSS + 27 HTML)
- **Покрытие**: крупные foundries, дизайн-блоги, RSS-агрегаторы
- **Проблемы**: 
  - Много HTML-источников (блокировки, медленнее)
  - Нет соцсетей (ранние анонсы)
  - Нет GitHub (open-source шрифты)
  - Нет конкурсов/наград

## 🚀 Приоритетные источники для добавления

### 1. RSS-источники (надежнее и быстрее)

**Специализированные типографические блоги:**
- I Love Typography: `https://ilovetypography.com/feed/`
- Typographica: `https://typographica.org/feed/`
- Typography.Guru: `https://typography.guru/feed/`
- FontShop News: `https://www.fontshop.com/news/feed`
- Fonts.com Blog: `https://www.fonts.com/blog/feed`

**Международные источники:**
- FontShop Japan: `https://www.fontshop.jp/news/feed` (если есть)
- Linotype News: `https://www.linotype.com/news/feed`
- FontShop Deutschland: `https://www.fontshop.de/news/feed`

**Крупные foundries с RSS:**
- Hoefler & Co: `https://www.typography.com/blog/feed`
- Font Bureau: `https://www.fontbureau.com/news/feed` (если есть)
- House Industries: `https://www.houseind.com/news/feed` (если есть)

### 2. GitHub (open-source шрифты)

**GitHub API для мониторинга:**
- Поиск по тегам: `font`, `typeface`, `typography`
- Популярные репозитории:
  - Google Fonts releases
  - Adobe Fonts open-source
  - Variable fonts projects

### 3. Социальные сети (ранние анонсы)

**Twitter/X API:**
- Мониторинг хештегов: `#fontrelease`, `#newfont`, `#typography`
- Аккаунты foundries: @HoeflerCo, @Monotype, @AdobeType
- Дизайнеры: @typographica, @ilovetypography

**Instagram (опционально):**
- Stories и посты foundries
- Ранние анонсы релизов

### 4. Конкурсы и награды

**TDC (Type Directors Club):**
- `https://www.tdc.org/news/feed`
- Ежегодные награды — важные новости

**Granshan:**
- Международный конкурс нелатинской типографики
- `https://granshan.org/news/feed` (если есть)

**Communication Arts:**
- Уже есть, но можно добавить RSS категории Typography

### 5. Азиатские источники

**Япония:**
- Typography.jp: `https://typography.jp/feed`
- Fontworks: `https://www.fontworks.co.jp/news/feed`

**Китай:**
- 3type (三言): `https://3type.cn/feed`
- Foundertype: `https://www.foundertype.com/news/feed`

**Корея:**
- Sandoll: `https://www.sandoll.com/news/feed`

### 6. Латинская Америка

- Tipografía: `https://tipografia.com/feed`
- Tipos Latinos (конкурс)

## ⚡ Стратегия опережения

### 1. Частота проверки
- **Текущая**: 1 раз в день (08:00 MSK)
- **Рекомендуемая**: Каждые 4-6 часов
  - 08:00 MSK (основной сбор)
  - 14:00 MSK (дополнительный)
  - 20:00 MSK (вечерний)

### 2. Приоритизация источников
- **Tier 1 (проверять каждые 4 часа)**: RSS-источники, крупные foundries
- **Tier 2 (раз в день)**: HTML-источники, дизайн-блоги
- **Tier 3 (раз в 2 дня)**: Медленные/проблемные источники

### 3. Ранние сигналы
- **Соцсети**: Мониторить за 1-2 дня до официального релиза
- **GitHub**: Новые коммиты в популярных репозиториях
- **Пресс-релизы**: Подписки на email-рассылки foundries

### 4. Уникальный контент
- **Аналитика**: Какие foundries активнее всего
- **Тренды**: Какие стили шрифтов популярны
- **Эксклюзивы**: Ранние анонсы через соцсети

### 5. Автоматизация
- **Webhooks**: Если foundries поддерживают
- **RSS Hub**: Создать собственные RSS для источников без фида
- **API**: Использовать официальные API где доступны

## 📈 Метрики успеха

1. **Скорость**: Первым публиковать новости (в течение 1-2 часов после релиза)
2. **Покрытие**: 50+ источников к концу года
3. **Качество**: 80%+ новостей релевантны типографике
4. **Уникальность**: 30%+ новостей не встречаются у конкурентов

## 🔧 Технические улучшения

1. **Кэширование**: ETag/Last-Modified для RSS
2. **Приоритетная очередь**: Сначала RSS, потом HTML
3. **Retry стратегия**: Умные задержки для проблемных источников
4. **Мониторинг**: Алерты при падении ключевых источников
5. **Аналитика**: Отслеживание успешности источников

## 📝 План действий

### Фаза 1 (Сейчас): RSS-источники
- [ ] Добавить I Love Typography RSS
- [ ] Добавить Typographica RSS
- [ ] Добавить Typography.Guru RSS
- [ ] Проверить RSS у крупных foundries

### Фаза 2 (Через неделю): Соцсети
- [ ] Интеграция Twitter/X API
- [ ] Мониторинг ключевых аккаунтов
- [ ] Фильтрация по релевантности

### Фаза 3 (Через месяц): GitHub
- [ ] GitHub API для open-source шрифтов
- [ ] Мониторинг популярных репозиториев
- [ ] Автоматическое определение релизов

### Фаза 4 (Через 2 месяца): Международные
- [ ] Азиатские источники
- [ ] Латинская Америка
- [ ] Европейские региональные источники

