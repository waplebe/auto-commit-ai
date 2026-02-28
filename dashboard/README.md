# Дыхание — Breathe

Дыхательный тренажёр: круг подсказывает фазу (вдох/задержка/выдох). Режимы: Квадрат 4-4-4-4, 4-7-8, Спокойное.

## Деплой на reg.ru

Да, работает. Next.js собран в статику (`output: "export"`).

```bash
cd dashboard
npm install
npm run build
```

Папка `out/` — залей её содержимое (index.html, _next/, и т.д.) в `www` или `public_html` на reg.ru через FTP/файловый менеджер.

## Локально

```bash
npm run dev
```
