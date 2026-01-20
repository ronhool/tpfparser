# Промпт для поиска новых источников Typefeed Parser

## 📋 Промпт для веб-поиска или AI-ассистента:

```
Найди новые RSS-ленты и веб-источники по типографике, шрифтам и дизайну шрифтов (type design, font releases, typography news), которые ЕЩЕ НЕ включены в следующий список:

УЖЕ ЕСТЬ В ПАРСЕРЕ:

RSS-источники (9):
1. Typecache (typecache.com/news/rss)
2. FreeTypography (freetypography.com/feed)
3. TypographyDaily (feeds.feedburner.com/TypographyDaily)
4. Underware (underware.nl/blog/rss/)
5. GoogleFontsBlog (fonts.googleblog.com/feeds/posts/default)
6. ILoveTypography (ilovetypography.com/feed/)
7. Typographica (typographica.org/feed/)
8. Typotheque (typotheque.com/blog/typotheque-rss-feed)
9. Typography.Guru (typography.guru/feed/)

HTML-источники (26):
1. TypewolfResources (typewolf.com/resources)
2. FontsInUse (fontsinuse.com)
3. Wallpaper (wallpaper.com)
4. Dezeen (dezeen.com)
5. ItsNiceThat (itsnicethat.com)
6. AIGAEyeOnDesign (eyeondesign.aiga.org)
7. CreativeReview (creativereview.co.uk)
8. DesignWeek (designweek.co.uk)
9. TheBrandIdentity (the-brandidentity.com)
10. PrintMagTypeTuesday (printmag.com/type-tuesday)
11. MonotypeNews (monotype.com/company/news-press)
12. TypographyComBranding (typography.com/blog/tag/Branding)
13. CommercialType (commercialtype.com)
14. ProductionType (productiontype.com)
15. DaltonMaag (daltonmaag.com)
16. Fontfabric (fontfabric.com)
17. TypeTogether (type-together.com)
18. Typeroom (typeroom.eu)
19. AIGA (aiga.org)
20. SlantedNews (slanted.de/news/)
21. Type01 (type-01.com)
22. MindSparkle (mindsparklemag.com/inspiration)
23. Abduzeedo (abduzeedo.com)
24. GMK (gmk.org.tr)
25. DandAD (dandad.org)
26. CommArts (commarts.com)

ТРЕБОВАНИЯ К НОВЫМ ИСТОЧНИКАМ:
- Приоритет RSS-лентам (быстрее и надежнее)
- Источники должны публиковать новости о шрифтах, типографике, релизах шрифтов, дизайне шрифтов
- Регулярные обновления (минимум раз в неделю)
- Английский или русский язык контента
- Международные источники приветствуются (Азия, Латинская Америка, Европа)
- Крупные foundries, дизайн-блоги, типографические журналы, конкурсы и награды

НЕ НУЖНЫ:
- Дубли существующих источников
- Источники только с бесплатными шрифтами без новостей
- Неактивные или заброшенные блоги
- Источники без RSS или с очень сложной структурой HTML

Верни список новых источников с:
- Названием
- URL RSS-ленты (если есть) или главной страницы
- Кратким описанием (чем полезен)
- Типом (RSS/HTML)
- Приоритетом добавления (высокий/средний/низкий)
```

## 🔍 Альтернативный промпт для специализированного поиска:

```
Я собираю новости о типографике и шрифтах для медиа-канала. Нужно найти НОВЫЕ источники, которых нет в моем списке.

МОЙ ТЕКУЩИЙ СПИСОК (35 источников):
[RSS: Typecache, FreeTypography, TypographyDaily, Underware, GoogleFontsBlog, ILoveTypography, Typographica, Typotheque, Typography.Guru]
[HTML: Typewolf, FontsInUse, Wallpaper, Dezeen, ItsNiceThat, AIGA, CreativeReview, DesignWeek, BrandIdentity, PrintMag, Monotype, Typography.com, CommercialType, ProductionType, DaltonMaag, Fontfabric, TypeTogether, Typeroom, Slanted, Type01, MindSparkle, Abduzeedo, GMK, D&AD, CommArts]

Найди:
1. RSS-ленты крупных foundries (Hoefler & Co, House Industries, Klim, Font Bureau и др.)
2. Международные типографические журналы с RSS
3. Конкурсы и награды по типографике (TDC, Granshan и др.)
4. Азиатские источники (Япония, Китай, Корея)
5. Латинская Америка (Tipografía, Tipos Latinos)
6. Европейские региональные источники
7. GitHub-репозитории с open-source шрифтами (если есть RSS)
8. Социальные сети foundries (если есть публичные RSS)

Для каждого источника укажи:
- Название
- RSS URL (если есть) или главную страницу
- Почему стоит добавить
- Приоритет (1-5, где 5 = обязательно добавить)
```

## 📝 Промпт для ChatGPT/Claude:

```
Я разрабатываю парсер новостей о типографике и шрифтах. У меня уже есть 35 источников (9 RSS + 26 HTML). 

СУЩЕСТВУЮЩИЕ ИСТОЧНИКИ:
RSS: Typecache, FreeTypography, TypographyDaily, Underware, GoogleFontsBlog, ILoveTypography, Typographica, Typotheque, Typography.Guru
HTML: Typewolf, FontsInUse, Wallpaper, Dezeen, ItsNiceThat, AIGA Eye on Design, Creative Review, Design Week, The Brand Identity, Print Magazine Type Tuesday, Monotype News, Typography.com Branding, Commercial Type, Production Type, Dalton Maag, Fontfabric, TypeTogether, Typeroom, AIGA, Slanted News, Type-01, MindSparkle, Abduzeedo, GMK, D&AD, CommArts

ЗАДАЧА: Найди НОВЫЕ источники, которых нет в списке выше.

КРИТЕРИИ:
✅ Приоритет RSS-лентам
✅ Новости о шрифтах, типографике, релизах, дизайне шрифтов
✅ Регулярные обновления
✅ Международные источники (Азия, Латинская Америка, Европа)
✅ Крупные foundries, дизайн-блоги, журналы, конкурсы

ФОРМАТ ОТВЕТА:
Для каждого нового источника:
1. Название
2. URL (RSS предпочтительно)
3. Описание
4. Тип (RSS/HTML)
5. Приоритет (высокий/средний/низкий)
6. Почему стоит добавить

Сфокусируйся на источниках, которые дадут УНИКАЛЬНЫЙ контент, не дублирующий существующие.
```

## 🎯 Краткий промпт для быстрого поиска:

```
Найди RSS-ленты и веб-источники по типографике и шрифтам, которых НЕТ в списке:
Typecache, FreeTypography, TypographyDaily, Underware, GoogleFontsBlog, ILoveTypography, Typographica, Typotheque, Typography.Guru, Typewolf, FontsInUse, Wallpaper, Dezeen, ItsNiceThat, AIGA, CreativeReview, DesignWeek, BrandIdentity, PrintMag, Monotype, Typography.com, CommercialType, ProductionType, DaltonMaag, Fontfabric, TypeTogether, Typeroom, Slanted, Type01, MindSparkle, Abduzeedo, GMK, D&AD, CommArts

Приоритет: RSS-ленты крупных foundries, международные журналы, конкурсы (TDC, Granshan), азиатские источники.
```

