#!/usr/bin/env python3
"""PDF 内容双通道提取：文本层优先，图片型页面自动渲染为 PNG 供多模态读取。

用法:
    python extract_pdf.py <pdf路径> [输出目录]

行为:
    1. 逐页提取文本层；文本有效(>10字符)则直接输出文本。
    2. 文本为空/极短的页面视为图片型页面，渲染为 PNG（150dpi）存到输出目录。
    3. 若整页既无文本也无图片对象，标记为 BLANK（常见于纯水印分隔页）。
    4. 输出目录默认为 <pdf同目录>/_pdf_extract/。

依赖: pymupdf (pip install pymupdf)
"""
import os
import sys

import fitz  # PyMuPDF

MIN_TEXT_LEN = 10


def main():
    if len(sys.argv) < 2:
        print("usage: extract_pdf.py <pdf> [out_dir]")
        sys.exit(1)
    pdf_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(os.path.abspath(pdf_path)), "_pdf_extract")
    os.makedirs(out_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    print(f"pages: {len(doc)}")
    results = []
    for i, page in enumerate(doc):
        text = (page.get_text() or "").strip()
        if len(text) >= MIN_TEXT_LEN:
            results.append(("TEXT", i + 1, None))
            print(f"===== PAGE {i+1} (text) =====")
            print(text)
            continue
        # 图片型页面：渲染成 PNG
        png = os.path.join(out_dir, f"page_{i+1}.png")
        pix = page.get_pixmap(dpi=150)
        pix.save(png)
        n_images = len(page.get_images(full=True))
        kind = "IMAGE" if n_images else "BLANK"
        results.append((kind, i + 1, png))
        print(f"===== PAGE {i+1} ({kind}) -> {png} =====")

    imgs = [r for r in results if r[0] == "IMAGE"]
    blanks = [r for r in results if r[0] == "BLANK"]
    print(f"\n[summary] text={len(results)-len(imgs)-len(blanks)} "
          f"image_pages={len(imgs)} blank_pages={len(blanks)} out_dir={out_dir}")
    if imgs:
        print("[hint] 图片型页面请用多模态读图工具逐张读取 PNG 内容")


if __name__ == "__main__":
    main()
