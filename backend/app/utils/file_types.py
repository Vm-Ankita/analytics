FILE_TYPES = {
    "csv":  {"label": "CSV",      "icon": "📊", "color": "#16a34a", "category": "tabular"},
    "tsv":  {"label": "TSV",      "icon": "📊", "color": "#16a34a", "category": "tabular"},
    "xlsx": {"label": "Excel",    "icon": "📗", "color": "#15803d", "category": "tabular"},
    "xls":  {"label": "Excel",    "icon": "📗", "color": "#15803d", "category": "tabular"},
    "pdf":  {"label": "PDF",      "icon": "📕", "color": "#dc2626", "category": "document"},
    "docx": {"label": "Word",     "icon": "📘", "color": "#2563eb", "category": "document"},
    "doc":  {"label": "Word",     "icon": "📘", "color": "#2563eb", "category": "document"},
    "txt":  {"label": "Text",     "icon": "📄", "color": "#6b7280", "category": "text"},
    "md":   {"label": "Markdown", "icon": "📝", "color": "#7c3aed", "category": "text"},
    "rtf":  {"label": "RTF",      "icon": "📄", "color": "#6b7280", "category": "text"},
    "json": {"label": "JSON",     "icon": "📦", "color": "#d97706", "category": "data"},
    "xml":  {"label": "XML",      "icon": "📦", "color": "#ea580c", "category": "data"},
    "yaml": {"label": "YAML",     "icon": "📦", "color": "#d97706", "category": "data"},
    "yml":  {"label": "YAML",     "icon": "📦", "color": "#d97706", "category": "data"},
    "png":  {"label": "PNG",      "icon": "🖼",  "color": "#0891b2", "category": "image"},
    "jpg":  {"label": "JPEG",     "icon": "🖼",  "color": "#0891b2", "category": "image"},
    "jpeg": {"label": "JPEG",     "icon": "🖼",  "color": "#0891b2", "category": "image"},
    "webp": {"label": "WebP",     "icon": "🖼",  "color": "#0891b2", "category": "image"},
    "gif":  {"label": "GIF",      "icon": "🖼",  "color": "#0891b2", "category": "image"},
    "html": {"label": "HTML",     "icon": "🌐", "color": "#ea580c", "category": "code"},
    "css":  {"label": "CSS",      "icon": "🎨", "color": "#0284c7", "category": "code"},
    "js":   {"label": "JS",       "icon": "⚡", "color": "#ca8a04", "category": "code"},
    "ts":   {"label": "TS",       "icon": "⚡", "color": "#2563eb", "category": "code"},
    "py":   {"label": "Python",   "icon": "🐍", "color": "#16a34a", "category": "code"},
    "java": {"label": "Java",     "icon": "☕", "color": "#ea580c", "category": "code"},
    "cpp":  {"label": "C++",      "icon": "⚙",  "color": "#7c3aed", "category": "code"},
    "c":    {"label": "C",        "icon": "⚙",  "color": "#7c3aed", "category": "code"},
    "go":   {"label": "Go",       "icon": "🐹", "color": "#0891b2", "category": "code"},
    "rs":   {"label": "Rust",     "icon": "🦀", "color": "#ea580c", "category": "code"},
    "sql":  {"label": "SQL",      "icon": "🗄",  "color": "#7c3aed", "category": "code"},
    "log":  {"label": "Log",      "icon": "📋", "color": "#6b7280", "category": "code"},
    "sh":   {"label": "Shell",    "icon": "💻", "color": "#16a34a", "category": "code"},
    "env":  {"label": "ENV",      "icon": "⚙",  "color": "#6b7280", "category": "code"},
}

IMAGE_EXTENSIONS   = {"png", "jpg", "jpeg", "gif", "webp"}
TABULAR_EXTENSIONS = {"csv", "tsv", "xlsx", "xls"}
TEXT_EXTENSIONS    = {
    "txt", "md", "rtf", "json", "xml", "yaml", "yml",
    "html", "css", "js", "ts", "py", "java", "cpp", "c",
    "go", "rs", "sql", "log", "sh", "env",
}

SUGGESTED_QUESTIONS = {
    "tabular":  ["Key trends?", "Any outliers?", "Most correlated columns?", "Top 3 insights?"],
    "document": ["Main topics?", "Key findings?", "Action items?", "Quick summary?"],
    "text":     ["What is this about?", "Key points?", "Any numbers?", "Conclusions?"],
    "data":     ["Describe the structure", "Key fields?", "Nested relationships?", "Summary?"],
    "image":    ["What is shown?", "Any text visible?", "Main elements?", "What stands out?"],
    "code":     ["What does this do?", "Any bugs?", "Main functions?", "How to improve?"],
    "unknown":  ["Summarize this", "Key insights?", "Important info?", "Any patterns?"],
}
