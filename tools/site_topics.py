#!/usr/bin/env python3
"""
Danh muc chu de cua site va cach nhom chung tren header menu.

kind = "qa"      -> 12 cau hoi backend, moi cau mot page rieng
kind = "partial" -> mot page gom nhieu muc; noi dung lay tu
                    content/<slug>.html (viet tay) + content/generated/<slug>.html
                    (sinh tu docx). Neu ca hai cung ton tai thi ban viet tay
                    duoc xep truoc.
"""

# Nhom hien tren header: (ten nhom, [slug, ...])
GROUPS = [
    ("Backend", [
        "advanced-backend",
        "backend-dotnet-nestjs",
        "database-sql",
        "backend-infrastructure",
        "realtime-socket",
        "case-studies",
    ]),
    ("Frontend", [
        "javascript-core",
        "react",
        "nextjs",
        "css-html",
        "browser-web-api",
        "react-native",
        "frontend-tooling",
    ]),
    ("Quy trình &amp; Nền tảng", [
        "git",
        "testing-environments",
        "saas-platforms",
        "auth-blockchain",
    ]),
    ("Khác", [
        "interview-intro",
        "project-notes",
    ]),
]

TOPICS = [
    # ------------------------------------------------------------- Backend
    {
        "slug": "advanced-backend",
        "kind": "qa",
        "nav": "Advanced Backend",
        "title": "Advanced Backend",
        "kicker": "Interview prep · Backend / Payment System",
        "heading": "Advanced Backend — 12 câu hỏi phỏng vấn thường gặp",
        "lede": "Từ bài toán kinh điển “2 request cùng trừ tiền 1 tài khoản” cho tới idempotency, saga, queue, cache, index và API design. Mỗi câu hỏi là một trang riêng, kèm ví dụ code, so sánh thực tế và câu trả lời mẫu dùng được ngay khi phỏng vấn.",
        "blurb": "12 câu hỏi chuyên sâu về concurrency, lock, idempotency, saga, queue, cache, index và API design — kèm code và câu trả lời mẫu.",
    },
    {
        "slug": "backend-dotnet-nestjs",
        "kind": "partial",
        "nav": ".NET &amp; NestJS",
        "title": "Backend — .NET &amp; NestJS",
        "kicker": "Interview prep · Backend / OOP / API",
        "heading": "Backend — .NET &amp; NestJS",
        "lede": "Nền tảng OOP, stack vs heap, ADO.NET và Entity Framework phía .NET; decorator, guard, module, upload file phía NestJS; cùng nhóm câu hỏi về API, REST và GraphQL.",
        "blurb": "OOP, stack/heap, ADO.NET, EF Core, JWT, decorator, guard, module, API — REST — GraphQL.",
    },
    {
        "slug": "database-sql",
        "kind": "partial",
        "nav": "Database &amp; SQL",
        "title": "Database &amp; SQL",
        "kicker": "Interview prep · SQL / Prisma",
        "heading": "Database &amp; SQL",
        "lede": "Các câu hỏi SQL hay gặp: UNION, VIEW, CTE, stored procedure, transaction, trigger, index; cùng phần Prisma và lựa chọn giữa cursor và offset pagination.",
        "blurb": "UNION, VIEW, CTE, procedure, transaction, trigger, index, ACID, Prisma và cursor pagination.",
    },
    {
        "slug": "backend-infrastructure",
        "kind": "partial",
        "nav": "Hạ tầng",
        "title": "Backend &amp; Hạ tầng",
        "kicker": "Interview prep · Backend / Infrastructure",
        "heading": "Backend &amp; Hạ tầng",
        "lede": "Những khái niệm hạ tầng hay bị hỏi kèm sau phần backend: CDN, Bloom filter, HTTP caching, reverse proxy, ảo hoá và phần cứng ảnh hưởng thế nào tới hiệu năng hệ thống.",
        "blurb": "CDN, RedisBloom, upload file NestJS, HTTP caching, reverse proxy, Hyper-V, SSD vs HDD, GPU.",
    },
    {
        "slug": "realtime-socket",
        "kind": "partial",
        "nav": "Realtime &amp; Socket",
        "title": "Realtime &amp; Socket",
        "kicker": "Interview prep · Realtime / Streaming",
        "heading": "Realtime &amp; Socket",
        "lede": "Socket.IO, WebSocket, SSE và WebRTC khác nhau ở đâu, khi nào chọn cái nào; kèm phần reactive stream với RxJS.",
        "blurb": "Socket.IO, namespace, WebSocket, SSE, WebRTC, OCR và RxJS / reactive state.",
    },
    {
        "slug": "case-studies",
        "kind": "partial",
        "nav": "Case studies",
        "title": "Case studies thực chiến",
        "kicker": "Interview prep · Bài toán hệ thống",
        "heading": "Case studies thực chiến",
        "lede": "Sáu bài toán kinh điển được hỏi dưới dạng tình huống: flash sale, trừ tiền lũy đẳng, import/export file triệu dòng, chống spam OTP, bảng xếp hạng và đăng xuất mọi thiết bị.",
        "blurb": "Flash sale, idempotency, import/export triệu dòng, chống spam OTP, caching bảng xếp hạng, thu hồi JWT.",
    },

    # ------------------------------------------------------------ Frontend
    {
        "slug": "javascript-core",
        "kind": "partial",
        "nav": "JavaScript &amp; TS",
        "title": "JavaScript &amp; TypeScript",
        "kicker": "Interview prep · JavaScript / TypeScript",
        "heading": "JavaScript &amp; TypeScript",
        "lede": "Closure, hoisting, this, event loop, module, ES6, promise và bất đồng bộ — nhóm câu hỏi nền tảng nhất khi phỏng vấn frontend; kèm phần TypeScript: interface vs type, any, unknown, keyof.",
        "blurb": "Closure, hoisting, this, event loop, promise, ES6, throttle/debounce, axios và TypeScript cơ bản.",
    },
    {
        "slug": "react",
        "kind": "partial",
        "nav": "React &amp; State",
        "title": "React &amp; State Management",
        "kicker": "Interview prep · React / Redux",
        "heading": "React &amp; State Management",
        "lede": "State, props, lifecycle, hooks, hydrate, virtual scroll và concurrent rendering; cùng nhóm quản lý state: Redux, Redux Thunk, RTK, createSelector và React Query.",
        "blurb": "State, props, hooks, lifecycle, hydrate, virtual scroll, Redux/RTK, React Query, Sentry.",
    },
    {
        "slug": "nextjs",
        "kind": "partial",
        "nav": "Next.js",
        "title": "Next.js &amp; Rendering",
        "kicker": "Interview prep · Next.js / Rendering",
        "heading": "Next.js &amp; Rendering",
        "lede": "CSR, SSR, SSG và các cơ chế mới của App Router: RSC payload, streaming, partial prerendering, revalidation, prefetching và metadata.",
        "blurb": "CSR/SSR/SSG, RSC payload, streaming, PPR, revalidation, prefetching, metadata, server-only.",
    },
    {
        "slug": "css-html",
        "kind": "partial",
        "nav": "CSS &amp; HTML",
        "title": "CSS &amp; HTML",
        "kicker": "Interview prep · CSS / HTML",
        "heading": "CSS &amp; HTML",
        "lede": "Luồng render CSS, position vs transform, margin collapse, sprite, preprocessor, multi-column và Tailwind; kèm phần semantic HTML.",
        "blurb": "Render flow, position vs transform, margin collapse, sprite, preprocessor, Tailwind, semantic HTML.",
    },
    {
        "slug": "browser-web-api",
        "kind": "partial",
        "nav": "Browser &amp; Web API",
        "title": "Browser &amp; Web API",
        "kicker": "Interview prep · Browser APIs",
        "heading": "Browser &amp; Web API",
        "lede": "DOM và virtual DOM, ba kiểu lưu trữ phía trình duyệt, Blob và FormData, IndexedDB/Dexie, cùng nhóm API đo đạc và cuộn trang.",
        "blurb": "DOM/VDOM, cookies vs storage, Blob, FormData, IndexedDB, Dexie, getBoundingClientRect, scroll API.",
    },
    {
        "slug": "react-native",
        "kind": "partial",
        "nav": "React Native",
        "title": "React Native",
        "kicker": "Interview prep · Mobile / React Native",
        "heading": "React Native",
        "lede": "Tối ưu FlatList, hệ thống chạm và cử chỉ, hiệu ứng ripple, safe area và native module — nhóm câu hỏi khi phỏng vấn vị trí mobile.",
        "blurb": "FlatList optimization, Touchable, Gesture Responder, ripple, SafeArea, native module.",
    },
    {
        "slug": "frontend-tooling",
        "kind": "partial",
        "nav": "Frontend Tooling",
        "title": "Frontend &amp; Tooling",
        "kicker": "Interview prep · Frontend / Developer tooling",
        "heading": "Frontend &amp; Tooling",
        "lede": "PWA khác web thường ở chỗ nào, hot reload thực chất là gì, SDK gồm những gì, monorepo với Nx giải quyết vấn đề gì, và vài thư viện hay xuất hiện trong JD.",
        "blurb": "PWA, Hot Reloading, SDK, Nx monorepo, OpenIM, Refine.",
    },

    # ------------------------------------------------ Quy trinh & Nen tang
    {
        "slug": "git",
        "kind": "partial",
        "nav": "Git",
        "title": "Git",
        "kicker": "Interview prep · Version control",
        "heading": "Git",
        "lede": "Ba trạng thái của file, snapshot, các lệnh hay bị hỏi (reset, restore, amend, stash, force push) và khác biệt giữa merge với rebase.",
        "blurb": "Three states, snapshot, add/commit/push, reset vs restore, amend, stash, merge vs rebase, SSH key.",
    },
    {
        "slug": "testing-environments",
        "kind": "partial",
        "nav": "Testing",
        "title": "Testing &amp; Môi trường",
        "kicker": "Interview prep · QA / Release process",
        "heading": "Testing &amp; Môi trường triển khai",
        "lede": "Alpha, staging và production khác nhau ra sao; các loại kiểm thử hay hỏi (white-box, black-box, smoke, regression, e2e) và bộ công cụ Playwright, Cucumber, Appium.",
        "blurb": "Alpha/staging, white-box, black-box, smoke, regression, e2e, POM, Playwright, Cucumber, Appium.",
    },
    {
        "slug": "saas-platforms",
        "kind": "partial",
        "nav": "SaaS &amp; Nền tảng",
        "title": "SaaS &amp; Nền tảng",
        "kicker": "Interview prep · Product / E-commerce platform",
        "heading": "SaaS &amp; Nền tảng thương mại điện tử",
        "lede": "Thế nào là một SaaS, hai cách làm store trên Shopify, và phân biệt CMS với CRM — nhóm câu hỏi về mô hình sản phẩm.",
        "blurb": "SaaS, điều kiện để là SaaS, Shopify theme vs headless, Haravan, CMS và CRM.",
    },
    {
        "slug": "auth-blockchain",
        "kind": "partial",
        "nav": "Auth &amp; Blockchain",
        "title": "Auth &amp; Blockchain",
        "kicker": "Interview prep · Authorization / Web3",
        "heading": "Auth &amp; Blockchain",
        "lede": "OAuth2 gồm những vai trò nào và token hoạt động ra sao, cùng nhóm khái niệm Web3 hay gặp trong JD: Solana, DApp và ví MetaMask.",
        "blurb": "OAuth2 (vai trò, token, scope), Solana, DApp và MetaMask.",
    },

    # ----------------------------------------------------------------- Khac
    {
        "slug": "interview-intro",
        "kind": "partial",
        "nav": "Giới thiệu &amp; English",
        "title": "Giới thiệu &amp; English",
        "kicker": "Interview prep · Soft skills",
        "heading": "Giới thiệu bản thân &amp; English",
        "lede": "Phần mở đầu buổi phỏng vấn: giới thiệu bản thân, quá trình học và làm việc; kèm một bài đọc tiếng Anh để luyện kể lại sự việc.",
        "blurb": "Kịch bản giới thiệu bản thân khi phỏng vấn và một bài đọc tiếng Anh kèm bản dịch.",
    },
    {
        "slug": "project-notes",
        "kind": "partial",
        "nav": "Ghi chú dự án",
        "title": "Ghi chú dự án",
        "kicker": "Interview prep · Kinh nghiệm dự án",
        "heading": "Ghi chú dự án",
        "lede": "Ghi chép về component dùng chung FilterTable trong dự án Hitek — dùng khi phỏng vấn hỏi sâu về thứ bạn đã tự xây dựng.",
        "blurb": "FilterTable: cách dùng, props, các state và hàm chính — tài liệu component dùng chung.",
    },
]

TOPIC_BY_SLUG = {t["slug"]: t for t in TOPICS}
