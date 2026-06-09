# ANT Stock — Front-End

Pure HTML/CSS/JavaScript front-end for the ANT Stock platform. No build step, no framework.

## Stack

- HTML5 + CSS3 (custom design system in `css/variables.css`)
- Vanilla JavaScript (ES Modules)
- Lucide Icons, Chart.js and SheetJS via CDN
- Hash-based router (`js/router.js`) with route guards

## Structure

```
frontend/
├── index.html
├── assets/
│   └── images/
├── css/
│   ├── variables.css
│   ├── global.css
│   ├── animations.css
│   ├── components.css
│   ├── login.css
│   ├── dashboard.css
│   └── responsive.css
└── js/
    ├── app.js           # Route registration + boot
    ├── router.js        # Hash router with guards
    ├── services/
    │   ├── api.js       # API client (mocked, ready for FastAPI)
    │   ├── supabase.js  # Supabase placeholder
    │   └── store.js     # Session + demo data
    ├── components/
    │   ├── sidebar.js
    │   ├── navbar.js
    │   ├── table.js
    │   ├── modal.js
    │   ├── cards.js
    │   └── notifications.js
    ├── pages/
    │   ├── login.js
    │   ├── register.js
    │   ├── forgot-password.js
    │   ├── dashboard.js
    │   ├── products.js
    │   ├── reports.js
    │   ├── profile.js
    │   ├── settings.js
    │   ├── exports.js
    │   └── placeholder.js
    └── utils/
        ├── exportExcel.js
        ├── exportTxt.js
        ├── validators.js
        ├── security.js
        └── helpers.js
```

## Future integration

- **FastAPI**: replace mocked functions in `js/services/api.js` and point `API.BASE_URL` to the FastAPI endpoint.
- **Supabase**: replace the stub in `js/services/supabase.js` by instantiating the real `@supabase/supabase-js` client and wiring it into `session`.

## Run

Open `/frontend/` from any static server, or visit the published URL.
The site root (`/`) redirects to `/frontend/index.html`.