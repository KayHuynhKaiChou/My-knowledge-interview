#!/usr/bin/env python3
"""
Ban do dinh tuyen: moi muc (heading) trong docx thuoc chu de nao tren site.

Key = "<ten tab>::<dau heading>" (so khop theo tien to, khong phan biet hoa thuong)
Value = slug chu de, hoac SKIP neu bo qua muc do.

Ly do SKIP thuong gap:
  - trung noi dung da co ban viet tay trong content/*.html
  - trung heading giua hai tab, giu ban day du hon
  - noi dung khong phuc vu on phong van (prompt AI, credentials)
"""

SKIP = "__skip__"

ROUTES = {
    # ---------------------------------------------------------------- Main
    "Main::4 tinh chat OOP": "backend-dotnet-nestjs",
    "Main::4 tính chất OOP": "backend-dotnet-nestjs",
    "Main::Stack với Heap": "backend-dotnet-nestjs",
    "Main::ADO.NET": "backend-dotnet-nestjs",
    "Main::Chức năng của AddControllers": "backend-dotnet-nestjs",
    "Main::AddDbContext": "backend-dotnet-nestjs",
    "Main::Lazy Loading và Eager Loading": "backend-dotnet-nestjs",
    "Main::Đặc điểm chính của record": "backend-dotnet-nestjs",
    "Main::JWT": "backend-dotnet-nestjs",
    "Main::Express.Multer.File": "backend-dotnet-nestjs",
    "Main::Decorator": "backend-dotnet-nestjs",
    "Main::Guard": "backend-dotnet-nestjs",
    "Main::API": "backend-dotnet-nestjs",
    "Main::Restful API": "backend-dotnet-nestjs",
    "Main::GraphQL": "backend-dotnet-nestjs",
    "Main::@UseInterceptors": SKIP,          # da viet tay o backend-infrastructure

    "Main::Hyper-V": "backend-infrastructure",
    "Main::Reverse Proxy": "backend-infrastructure",
    "Main::HTTP caching": "backend-infrastructure",
    "Main::Thumbnail": "backend-infrastructure",

    "Main::SSH key": "git",
    "Main::GIT và GITHUB": "git",

    "Main::Throttle": "javascript-core",
    "Main::Debounce": "javascript-core",
    "Main::Event delegation": "javascript-core",
    "Main::async và defer": "javascript-core",
    "Main::closure": "javascript-core",
    "Main::Hoisting": "javascript-core",
    "Main::IIFE": "javascript-core",
    "Main::Các cách gọi hàm": "javascript-core",
    "Main::Tham số và đối số": "javascript-core",
    "Main::var, let và const": "javascript-core",
    "Main::context": "javascript-core",
    "Main::Rest parameter": "javascript-core",
    "Main::Call stack": "javascript-core",
    "Main::Modules": "javascript-core",
    "Main::distinguish interface and type": "javascript-core",
    "Main::any type": "javascript-core",
    "Main::unknown type": "javascript-core",
    "Main::keyof": "javascript-core",

    "Main::Cookies - Local Storage": "browser-web-api",
    "Main::Blob": "browser-web-api",
    "Main::FormData": "browser-web-api",
    "Main::IndexedDB": "browser-web-api",
    "Main::Dexie.js": "browser-web-api",
    "Main::popstate": "browser-web-api",
    "Main::DOM và Virtual DOM": "browser-web-api",

    "Main::State": "react",
    "Main::Prop drilling": "react",
    "Main::prop key trong react": "react",
    "Main::Prop": "react",
    "Main::dangerouslySetInnerHTML": "react",
    "Main::stateful và stateless": "react",
    "Main::quá trình update value": "react",
    "Main::lifecycle react": "react",
    "Main::Hydrate": "react",
    "Main::React Hooks": "react",
    "Main::Component-Driven Development": "react",
    "Main::Immutable trong redux": "react",
    "Main::createSelector": "react",
    "Main::hook use() trong react": "react",
    "Main::@sentry/react": "react",
    "Main::@xyflow/react": "react",
    "Main::Flow render server comp": "react",
    "Main::Infinite Scroll": "react",
    "Main::Virtual Scroll": "react",
    "Main::Concurrent Rendering": "react",
    "Main::Slice trong RTK": "react",

    "Main::Native module": "react-native",

    # ----------------------------------------------------------------- SQL
    "SQL::UNION": "database-sql",
    "SQL::SELECT INTO": "database-sql",
    "SQL::VIEW": "database-sql",
    "SQL::Common table expression": "database-sql",
    "SQL::STORE PROCEDURE": "database-sql",
    "SQL::Transaction trong SQL": "database-sql",
    "SQL::Trigger": "database-sql",
    "SQL::Index": "database-sql",
    "SQL::some và every": "database-sql",
    "SQL::schema.prisma": "database-sql",
    "SQL::ACID": "database-sql",
    "SQL::giữa cursor và pagination": "database-sql",
    "SQL::Module": "backend-dotnet-nestjs",
    "SQL::1. Mua hàng Flash Sale": "case-studies",
    "SQL::2. Thanh toán": "case-studies",
    "SQL::3. Import / Export": "case-studies",
    "SQL::4. Gửi mã OTP": "case-studies",
    "SQL::5. Danh sách sản phẩm Hot": "case-studies",
    "SQL::6. Tính năng Đăng xuất": "case-studies",

    # --------------------------------------------- React native and libs
    "React native and libs::Optimizing Flatlist": "react-native",
    "React native and libs::Component Touchable": "react-native",
    "React native and libs::Gesture Responder": "react-native",
    "React native and libs::Ripple effect": "react-native",
    "React native and libs::SafeAreaProvider": "react-native",
    "React native and libs::SafeAreaView": "react-native",
    "React native and libs::OpenIM": "frontend-tooling",
    "React native and libs::Refine": "frontend-tooling",
    "React native and libs::CMS": "saas-platforms",
    "React native and libs::CRM": "saas-platforms",
    "React native and libs::generateMetadata": "nextjs",
    "React native and libs::next/headers": "nextjs",
    "React native and libs::Appium": "testing-environments",
    "React native and libs::Playwright": SKIP,   # ban day du hon o tab Automation test
    "React native and libs::Cucumber": SKIP,     # ban day du hon o tab Automation test
    "React native and libs::ReactQuery": "react",
    "React native and libs::createEntityAdapter": "react",

    # ----------------------------------------------------------------- CSS
    "CSS::Flow render UI CSS": "css-html",
    "CSS::Position vs transform": "css-html",
    "CSS::margin collapse": "css-html",
    "CSS::interview ques CSS": "css-html",
    "CSS::CSS sprite": "css-html",
    "CSS::CSS preprocessor": "css-html",
    "CSS::!important": "css-html",
    "CSS::CSS multi columns": "css-html",
    "CSS::align-content": "css-html",
    "CSS::white-space": "css-html",
    "CSS::inline-block": "css-html",
    "CSS::Scale-y-0": "css-html",
    "CSS::tailwind": "css-html",
    "CSS::getBoundingClientRect": "browser-web-api",
    "CSS::window.scrollY": "browser-web-api",
    "CSS::window.location.hash": "browser-web-api",
    "CSS::innerHight": "browser-web-api",
    "CSS::ScrollIntoView": "browser-web-api",

    # --------------------------------------------------- JS & React & Git
    "JS & React & Git::ES6": "javascript-core",
    "JS & React & Git::Arrow function": "javascript-core",
    "JS & React & Git::Template literals": "javascript-core",
    "JS & React & Git::Modules": "javascript-core",
    "JS & React & Git::Destructuring": "javascript-core",
    "JS & React & Git::Bất đồng bộ": "javascript-core",
    "JS & React & Git::Async/ Await": "javascript-core",
    "JS & React & Git::Callback": "javascript-core",
    "JS & React & Git::Promise chain": "javascript-core",
    "JS & React & Git::Promise.all": "javascript-core",
    "JS & React & Git::Promise.allSettled": "javascript-core",
    "JS & React & Git::Promise": "javascript-core",
    "JS & React & Git::Array.prototype": "javascript-core",
    "JS & React & Git::String.prototype": "javascript-core",
    "JS & React & Git::preventDefault": "javascript-core",
    "JS & React & Git::stopProbagation": "javascript-core",
    "JS & React & Git::Fetch": "javascript-core",
    "JS & React & Git::Interceptor trong Axios": "javascript-core",
    "JS & React & Git::Axios": "javascript-core",
    "JS & React & Git::React hooks": "react",
    "JS & React & Git::Redux Thunk": "react",
    "JS & React & Git::Redux": "react",
    "JS & React & Git::GIT": "git",
    "JS & React & Git::Snapshot": "git",
    "JS & React & Git::The three states": "git",
    "JS & React & Git::Git status": "git",
    "JS & React & Git::Git add": "git",
    "JS & React & Git::Git commit --amend": "git",
    "JS & React & Git::Git commit": "git",
    "JS & React & Git::Git push --force": "git",
    "JS & React & Git::Git push": "git",
    "JS & React & Git::Git restore": "git",
    "JS & React & Git::Git reset": "git",
    "JS & React & Git::.gitignore": "git",
    "JS & React & Git::git stash": "git",
    "JS & React & Git::git merge và git rebase": "git",
    "JS & React & Git::git protocols": "git",

    # -------------------------------------------------------------- nextJS
    "nextJS::Semantic element": "css-html",
    "nextJS::CSR": "nextjs",
    "nextJS::SSR": "nextjs",
    "nextJS::SSG": "nextjs",
    "nextJS::Server Rendering": "nextjs",
    "nextJS::React Server Component Payload": "nextjs",
    "nextJS::Revalidation": "nextjs",
    "nextJS::Prefetching": "nextjs",
    "nextJS::Streaming": "nextjs",
    "nextJS::Interleaving": "nextjs",
    "nextJS::Phân biệt Client Comp": "nextjs",
    "nextJS::import 'server-only'": "nextjs",
    "nextJS::Partial Prerendering": "nextjs",
    "nextJS::Cookies": "nextjs",
    "nextJS::Pre-rendering": "nextjs",
    "nextJS::Metadata": "nextjs",
    "nextJS::Open Graph Images": "nextjs",

    # ----------------------------------------------------- Automation test
    "Automation test::Automation test": "testing-environments",
    "Automation test::White-box testing": "testing-environments",
    "Automation test::Black-box testing": "testing-environments",
    "Automation test::Smoke test": "testing-environments",
    "Automation test::Regression test": "testing-environments",
    "Automation test::Environment testing": "testing-environments",
    "Automation test::End-to-End": SKIP,      # da viet tay o testing-environments
    "Automation test::Test suite": "testing-environments",
    "Automation test::Page object model": "testing-environments",
    "Automation test::Verification and validation": "testing-environments",
    "Automation test::Playwright": "testing-environments",
    "Automation test::Cucumber": "testing-environments",

    # -------------------------------------------------------------- Socket
    "Socket::Socket.IO": "realtime-socket",
    "Socket::Khác biệt giữa socket.emit": "realtime-socket",
    "Socket::Namespace": "realtime-socket",
    "Socket::Socket": "realtime-socket",
    "Socket::HTTP": "realtime-socket",
    "Socket::WebSocket": "realtime-socket",
    "Socket::SSE": "realtime-socket",
    "Socket::OCR": "realtime-socket",
    "Socket::WebRTC": "realtime-socket",

    # ------------------------------------------------------------- Angular
    "Angular::RxJS": "realtime-socket",
    "Angular::Reactive state": "realtime-socket",
}

# Tab "Other knowledge technique" da duoc viet tay trong content/*.html
SKIP_TABS = {"Other knowledge technique"}

# Cac tab khong co heading: dinh nghia muc theo khoang doan (start <= i < end)
SYNTHETIC_SECTIONS = [
    {
        # "currying" trong docx khong duoc to style Heading nen phai tach tay
        "tab": "Main",
        "topic": "javascript-core",
        "id": "currying",
        "title": "Currying",
        "nav": "Currying",
        "start": 266,
        "end": 271,
    },
    {
        "tab": "English reading",
        "topic": "interview-intro",
        "id": "english-reading",
        "title": "Bài đọc tiếng Anh — kể một sự việc đã xảy ra",
        "nav": "Bài đọc tiếng Anh",
        "start": 1548,
        "end": 1554,
    },
    {
        "tab": "Giới thiệu",
        "topic": "interview-intro",
        "id": "gioi-thieu-ban-than",
        "title": "Giới thiệu bản thân khi phỏng vấn",
        "nav": "Giới thiệu bản thân",
        "start": 1578,
        "end": 1583,   # dung truoc phan prompt AI + credentials Supabase
    },
    {
        "tab": "FilterTable hitek",
        "topic": "project-notes",
        "id": "filtertable-common",
        "title": "FilterTable — component dùng chung (dự án Hitek)",
        "nav": "FilterTable Common",
        "start": 1629,
        "end": 1680,
    },
]

# Heading bi dinh lien voi noi dung phia sau trong docx -> cat lai tieu de
HEADING_FIXES = {
    "async và defer trong <script>Polyfill": "async và defer trong &lt;script&gt;",
    "Các cách gọi hàm trong jsfunction show() {": "Các cách gọi hàm trong JS",
    "Rest parameter , Spread operator , Destructuring": "Rest parameter, Spread operator, Destructuring",
    "Immutable trong redux": "Immutable trong Redux",
    "interview ques CSS": "Câu hỏi phỏng vấn CSS &amp; HTML",
    "prop key trong react": "prop key trong React",
    "4 tính chất OOP :": "4 tính chất OOP",
    "ADO.NET (ActiveX Data Object) giống với JDBC của Java": "ADO.NET",
}

# Nhan hien thi cua tung tab tren the muc
TAB_LABELS = {
    "Main": "Kiến thức nền",
    "SQL": "SQL",
    "React native and libs": "React Native & Libs",
    "CSS": "CSS",
    "JS & React & Git": "JS · React · Git",
    "nextJS": "Next.js",
    "Automation test": "Automation test",
    "Socket": "Socket & Realtime",
    "Angular": "Angular / RxJS",
    "English reading": "English",
    "Giới thiệu": "Phỏng vấn",
    "FilterTable hitek": "Ghi chú dự án",
}
