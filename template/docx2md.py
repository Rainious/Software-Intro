"""Convert .docx to .md with structure preservation."""
import zipfile, sys, io, re
from xml.etree import ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DOCX_PATH = 'E:/CCProjects/JZPPT/Software-Intro/template.docx'
OUT_PATH = 'E:/CCProjects/JZPPT/Software-Intro/template.md'

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
XML = 'http://www.w3.org/XML/1998/namespace'

NSMAP = {
    'w': W,
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'v': 'urn:schemas-microsoft-com:vml',
    'o': 'urn:schemas-microsoft-com:office:office',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
}

class DocxToMarkdown:
    def __init__(self, zip_path):
        self.zip = zipfile.ZipFile(zip_path, 'r')
        self.styles = {}
        self.numbering = {}
        self.num_map = {}
        self.image_counter = 0
        self._load_supporting()

    def _load_supporting(self):
        if 'word/styles.xml' in self.zip.namelist():
            styles_xml = ET.fromstring(self.zip.read('word/styles.xml'))
            for style in styles_xml.findall(f'.//{{{W}}}style'):
                sid = style.get(f'{{{W}}}styleId')
                name_el = style.find(f'{{{W}}}name')
                name = name_el.get(f'{{{W}}}val') if name_el is not None else ''
                stype = style.get(f'{{{W}}}type', '')
                self.styles[sid] = {'name': name, 'type': stype}

        if 'word/numbering.xml' in self.zip.namelist():
            num_xml = ET.fromstring(self.zip.read('word/numbering.xml'))
            for absn in num_xml.findall(f'.//{{{W}}}abstractNum'):
                aid = absn.get(f'{{{W}}}abstractNumId')
                levels = {}
                for lvl in absn.findall(f'{{{W}}}lvl'):
                    ilvl = lvl.get(f'{{{W}}}ilvl')
                    nf = lvl.find(f'{{{W}}}numFmt')
                    lt = lvl.find(f'{{{W}}}lvlText')
                    levels[ilvl] = {
                        'numfmt': nf.get(f'{{{W}}}val') if nf is not None else 'decimal',
                        'lvlText': lt.get(f'{{{W}}}val') if lt is not None else '%1.',
                    }
                self.numbering[aid] = levels

            for num in num_xml.findall(f'.//{{{W}}}num'):
                nid = num.get(f'{{{W}}}numId')
                ref = num.find(f'{{{W}}}abstractNumId')
                if ref is not None and ref.get(f'{{{W}}}val') in self.numbering:
                    self.num_map[nid] = ref.get(f'{{{W}}}val')

    def _get_style(self, para_elem):
        pPr = para_elem.find(f'{{{W}}}pPr')
        if pPr is None:
            return ''
        pStyle = pPr.find(f'{{{W}}}pStyle')
        if pStyle is None:
            return ''
        sid = pStyle.get(f'{{{W}}}val')
        return sid

    def _get_style_name(self, para_elem):
        sid = self._get_style(para_elem)
        if sid in self.styles:
            return self.styles[sid]['name']
        return sid

    def _extract_run_text(self, run_elem):
        """Extract text from a single run element."""
        texts = []
        bold = False
        italic = False

        rPr = run_elem.find(f'{{{W}}}rPr')
        if rPr is not None:
            b = rPr.find(f'{{{W}}}b')
            bold = b is not None and b.get(f'{{{W}}}val') not in ('false', '0')
            i = rPr.find(f'{{{W}}}i')
            italic = i is not None and i.get(f'{{{W}}}val') not in ('false', '0')

        for elem in run_elem.iter():
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            if tag == 't':
                text = elem.text or ''
                texts.append(text)
            elif tag == 'tab':
                texts.append('\t')
            elif tag in ('br', 'cr'):
                texts.append('\n')

        # Deduplicate consecutive identical text segments (common in WPS templates)
        deduped = []
        for t in texts:
            if deduped and deduped[-1] == t:
                continue
            deduped.append(t)
        content = ''.join(deduped)

        if bold and italic:
            content = f'***{content}***'
        elif bold:
            content = f'**{content}**'
        elif italic:
            content = f'*{content}*'
        return content

    def _extract_paragraph_text(self, para_elem):
        """Extract all text from a paragraph."""
        parts = []
        # Direct runs
        for run in para_elem.findall(f'{{{W}}}r'):
            parts.append(self._extract_run_text(run))
        # Hyperlinks
        for hl in para_elem.findall(f'{{{W}}}hyperlink'):
            for run in hl.findall(f'{{{W}}}r'):
                parts.append(self._extract_run_text(run))
        # SDT (structured document tags)
        for sdt in para_elem.findall(f'{{{W}}}sdt'):
            for p in sdt.findall(f'.//{{{W}}}p'):
                parts.append(self._extract_paragraph_text(p))
        # Simple fields (fldSimple)
        for fld in para_elem.findall(f'{{{W}}}fldSimple'):
            for run in fld.findall(f'{{{W}}}r'):
                parts.append(self._extract_run_text(run))

        text = ''.join(parts)
        # Clean up formatting artifacts: merge adjacent bold markers
        text = re.sub(r'\*\*\*\*\s*\*\*\*\*', '****', text)
        text = re.sub(r'\*\*\*\*', '', text)
        text = re.sub(r'\*\*\s*\*\*', '', text)
        # Clean up duplicate ** patterns
        text = text.replace('****', '')
        return text

    def _detect_heading_level(self, para_elem):
        """Detect heading level from style or outline level or content pattern."""
        style_name = self._get_style_name(para_elem)
        sn = style_name.lower()

        # Standard heading styles
        heading_map = {
            'heading 1': 1, 'heading 2': 2, 'heading 3': 3,
            'heading 4': 4, 'heading 5': 5, 'heading 6': 6,
            '标题 1': 1, '标题 2': 2, '标题 3': 3,
            '标题 4': 4, '标题 5': 5, '标题 6': 6,
            'toc1': 0, 'toc2': 0, 'toc3': 0,  # TOC entries are not real headings
        }
        for key, level in heading_map.items():
            if key in sn:
                return level

        # Check outline level
        pPr = para_elem.find(f'{{{W}}}pPr')
        if pPr is not None:
            ol = pPr.find(f'{{{W}}}outlineLvl')
            if ol is not None:
                return int(ol.get(f'{{{W}}}val')) + 1

        return 0

    def _has_numbering(self, para_elem):
        pPr = para_elem.find(f'{{{W}}}pPr')
        if pPr is None:
            return None
        numPr = pPr.find(f'{{{W}}}numPr')
        if numPr is None:
            return None
        nid_el = numPr.find(f'{{{W}}}numId')
        ilvl_el = numPr.find(f'{{{W}}}ilvl')
        if nid_el is not None:
            return (nid_el.get(f'{{{W}}}val'), ilvl_el.get(f'{{{W}}}val') if ilvl_el is not None else '0')
        return None

    def _extract_table(self, tbl_elem):
        """Extract table as markdown."""
        rows = []
        for tr in tbl_elem.findall(f'{{{W}}}tr'):
            cells = []
            for tc in tr.findall(f'{{{W}}}tc'):
                parts = []
                for p in tc.findall(f'{{{W}}}p'):
                    t = self._extract_paragraph_text(p).strip()
                    if t:
                        parts.append(t)
                text = ' '.join(parts).replace('\n', ' ').replace('|', '\\|')
                cells.append(text)
            rows.append(cells)

        if not rows:
            return ''

        max_cols = max(len(r) for r in rows)
        for r in rows:
            while len(r) < max_cols:
                r.append('')

        # 1-column table: render as bullet list
        if max_cols == 1:
            items = []
            for row in rows:
                text = row[0].strip()
                if text:
                    # Clean up bold artifacts
                    text = text.replace('******', '**').replace('****', '')
                    # Remove redundant ** markers mid-text
                    text = re.sub(r'\*\*\s+\*\*', '', text)
                    items.append(f'- {text}')
            if items:
                return '\n'.join(items) + '\n'
            return ''

        # 2-column table: key-value format
        if max_cols == 2:
            all_items = []
            header_like = all('**' in (r[0] + r[1]) for r in rows[:min(3, len(rows))])
            for row in rows:
                key = row[0].strip()
                val = row[1].strip()
                # Clean up markers
                key = key.replace('******', '**').replace('****', '').strip('* :：').strip()
                val = val.replace('******', '**').replace('****', '').strip('*').strip()
                key = re.sub(r'\*\*\s+\*\*', '', key)
                val = re.sub(r'\*\*\s+\*\*', '', val)
                if key or val:
                    all_items.append(f'- **{key}**：{val}' if key else f'- {val}')
            if all_items:
                return '\n'.join(all_items) + '\n'

        # Standard table
        lines = []
        lines.append('| ' + ' | '.join(rows[0]) + ' |')
        lines.append('| ' + ' | '.join(['---'] * max_cols) + ' |')
        for row in rows[1:]:
            lines.append('| ' + ' | '.join(row) + ' |')
        return '\n'.join(lines) + '\n'

    def _element_to_md(self, elem):
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag == 'p':
            return self._para_to_md(elem)
        elif tag == 'tbl':
            return self._extract_table(elem)
        elif tag == 'sdt':
            results = []
            for child in elem:
                results.append(self._element_to_md(child))
            return '\n'.join(r for r in results if r)
        elif tag == 'customXml':
            return ''
        return ''

    def _para_to_md(self, para_elem):
        text = self._extract_paragraph_text(para_elem).strip()
        style_name = self._get_style_name(para_elem)
        style_id = self._get_style(para_elem)
        heading_level = self._detect_heading_level(para_elem)
        num_info = self._has_numbering(para_elem)

        # Detect page break
        pPr = para_elem.find(f'{{{W}}}pPr')
        has_page_break = False
        if pPr is not None:
            pb = pPr.find(f'{{{W}}}pageBreakBefore')
            has_page_break = pb is not None

        # Skip decorative separators (lines of dots or similar)
        clean_text = text.replace('*', '').replace(' ', '').replace('\t', '')
        if re.match(r'^\.{2,}$', clean_text):
            return '\n---\n'
        # Skip empty/whitespace paragraphs (spacers)
        if not clean_text:
            return ''

        # Skip TOC entries (style-based) but keep the text
        is_toc = 'toc' in style_name.lower() or style_id.startswith('TOC')

        # Headings
        if heading_level > 0:
            if not text:
                return ''
            prefix = '#' * heading_level
            sep = '\n---\n\n' if has_page_break else '\n'
            # Remove leading numbers from headings (e.g. "1  引言" -> "引言")
            cleaned = re.sub(r'^[\d.]+\s*', '', text).strip()
            if not cleaned:
                cleaned = text
            return f'{sep}{prefix} {cleaned}\n'

        # Numbered list items
        if num_info is not None:
            if not text:
                return ''
            nid, ilvl = num_info
            indent = '    ' * int(ilvl)
            return f'{indent}1. {text}\n'

        # TOC entries: format cleanly
        if is_toc:
            if not text:
                return ''
            # TOC entries have page numbers at end, keep but separate
            cleaned = re.sub(r'\s+\d+\s*$', '', text)  # Remove trailing page number
            return f'- {cleaned}\n'

        # Regular text
        if not text:
            return ''

        # Title/subtitle detection
        sn = style_name.lower()
        if 'title' in sn or sn == '标题':
            return f'\n# {text}\n'
        if 'subtitle' in sn or sn == '副标题':
            return f'\n## {text}\n'

        prefix = '\n---\n\n' if has_page_break else '\n'
        # Clean up bold artifacts in regular text
        text = re.sub(r'\*\*\s*\*\*', '', text)
        text = re.sub(r'\*\*\*\*', '', text)
        return f'{prefix}{text}\n\n'

    def convert(self):
        doc_xml = ET.fromstring(self.zip.read('word/document.xml'))
        body = doc_xml.find(f'{{{W}}}body')
        if body is None:
            return ''

        # Collect output segments with their types for post-processing
        segments = []
        for elem in body:
            md = self._element_to_md(elem)
            if md:
                segments.append(md)

        result = ''.join(segments)

        # Cleanup passes
        result = re.sub(r'\n{4,}', '\n\n\n', result)           # Collapse blank lines
        result = re.sub(r'\*\*\s*\*\*', '', result)            # Empty bold markers
        result = re.sub(r'\*\*\*\*\s*\*\*\*\*', '', result)    # Empty bold-italic
        result = re.sub(r'\*\*\*\*', '', result)               # Quad asterisks
        result = re.sub(r'\*\*\.\.\*\*', '', result)           # Bold dots
        result = re.sub(r'\n\s+\n', '\n\n', result)            # Whitespace-only lines
        result = re.sub(r'\*\*\t\*\*', '\t', result)           # TOC tab formatting
        result = re.sub(r'(\n---)+$', '', result)              # Trailing separators
        result = re.sub(r'---\n---\n?', '---\n', result)       # Merge consecutive hr
        result = re.sub(r'\n---\n\n---\n', '\n---\n', result)  # Merge spaced hr
        result = re.sub(r'\n\*\*\.\.\n', '\n---\n', result)    # Bold dots line
        result = re.sub(r'- \n', '', result)                   # Empty bullet items
        result = re.sub(r'\n\*\*\n', '\n', result)             # Solitary bold line
        result = re.sub(r'^\*\*\n', '', result)                # Leading bold-only line
        # Clean section dividers with bold-dots
        result = re.sub(r'\*\*(.+?)\n\n\*\*', r'**\1**\n\n', result)
        result = re.sub(r'\.\.\*\*\n', '---\n', result)        # Dots before bold end
        # Remove any remaining standalone ".." lines
        result = re.sub(r'\n\.\.\n', '\n', result)
        # Merge consecutive `---` after other separators were removed
        result = re.sub(r'(\n---){2,}\n?', '\n---\n', result)
        # Trim excessive internal whitespace (6+ spaces) in any line
        result = re.sub(r' {6,}', ' ', result)
        result = result.strip()

        # Add document title at top if missing
        if not result.startswith('# '):
            pass  # First heading should be fine

        return result

def main():
    converter = DocxToMarkdown(DOCX_PATH)
    md_content = converter.convert()

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f'Written {len(md_content)} characters to {OUT_PATH}')
    print(f'\n=== Preview ===')
    print(md_content[:4000])

if __name__ == '__main__':
    main()
