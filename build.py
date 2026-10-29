#!/usr/bin/env python3
"""Turns src/*.md into plain HTML pages: privacy-policy/index.html and delete-account/index.html.
Handles the few constructs those pages use: headings, paragraphs, bold, bullet and numbered lists, one table."""
import html, pathlib, re

ROOT = pathlib.Path(__file__).parent
STYLE = """
body{margin:0;background:#FBF8F6;color:#1F1A1C;font:17px/1.6 -apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:720px;margin:0 auto;padding:40px 20px 64px}
h1{font-size:30px;line-height:1.25;margin:0 0 20px}h2{font-size:22px;margin:36px 0 12px;color:#8E1B3A}h3{font-size:18px;margin:24px 0 8px}
p,li{margin:0 0 12px}ul,ol{padding-left:24px}table{border-collapse:collapse;width:100%;margin:12px 0 20px;font-size:16px}
th,td{border:1px solid #D8CCC6;padding:8px 10px;text-align:left;vertical-align:top}th{background:#F3EDE9}
a{color:#8E1B3A}footer{margin-top:48px;padding-top:16px;border-top:1px solid #D8CCC6;font-size:15px;color:#4A403D}
"""

def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[(.+?)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', text)
    return text

def convert(md):
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    out, para, table = [], [], []
    state = {"list": None}
    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>"); para.clear()
    def close_list():
        if state["list"]:
            out.append(f"</{state['list']}>"); state["list"] = None
    def flush_table():
        if table:
            rows = [[inline(c.strip()) for c in r.strip().strip("|").split("|")] for r in table if not re.match(r"^\|?\s*-", r)]
            head, body = rows[0], rows[1:]
            out.append("<table><thead><tr>" + "".join(f"<th>{c}</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table>")
            table.clear()
    for line in md.splitlines():
        s = line.strip()
        if s.startswith("|"):
            flush_para(); close_list(); table.append(s); continue
        flush_table()
        m = re.match(r"^(#{1,3})\s+(.*)", s)
        if m:
            flush_para(); close_list(); out.append(f"<h{len(m[1])}>{inline(m[2])}</h{len(m[1])}>"); continue
        m = re.match(r"^(-|\d+\.)\s+(.*)", s)
        if m:
            flush_para(); tag = "ul" if m[1] == "-" else "ol"
            if state["list"] != tag:
                close_list(); out.append(f"<{tag}>"); state["list"] = tag
            out.append(f"<li>{inline(m[2])}</li>"); continue
        if not s:
            flush_para(); close_list(); continue
        close_list(); para.append(s)
    flush_para(); close_list(); flush_table()
    return "\n".join(out)

def page(title, body, footer):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title><style>{STYLE}</style></head>
<body><main>
{body}
<footer>{footer}</footer>
</main></body></html>
"""

links = []
for src in sorted((ROOT / "src").glob("*.md")):
    md = src.read_text()
    title = re.search(r"^#\s+(.*)", md, flags=re.M)[1]
    dest = ROOT / src.stem / "index.html"; dest.parent.mkdir(exist_ok=True)
    dest.write_text(page(title, convert(md), 'FundedArmy · <a href="../">All Boutiques pages</a>'))
    links.append(f'<li><a href="{src.stem}/">{html.escape(title)}</a></li>')
    print("wrote", dest.relative_to(ROOT))
index = f"<h1>Boutiques</h1><p>Legal pages for the Boutiques app by FundedArmy, Rewari.</p><ul>{''.join(links)}</ul>"
(ROOT / "index.html").write_text(page("Boutiques legal pages", index, "FundedArmy"))
print("wrote index.html")
