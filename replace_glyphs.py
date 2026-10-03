#!/usr/bin/env python3
"""Replace selected glyphs in base font with denoise version
Usage: python replace_glyphs.py base.ttf denoise.ttf filter.json output.ttf

filter.json format (simple array):
["的", "我", "了", "好", "一", "字"]
"""
import json
import sys
import copy
from fontTools.ttLib import TTFont


def main():
    if len(sys.argv) != 5:
        print("Usage: python replace_glyphs.py base.ttf denoise.ttf filter.json output.ttf")
        sys.exit(1)

    base_ttf, denoise_ttf, filter_json, output_ttf = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

    base_font = TTFont(base_ttf)
    denoise_font = TTFont(denoise_ttf)

    with open(filter_json, 'r', encoding='utf-8') as f:
        chars = json.load(f)

    if isinstance(chars, dict):
        chars = chars.get("chars", [])

    if not chars:
        print("No chars to replace, saving base as-is")
        base_font.save(output_ttf)
        return

    base_cmap = base_font.getBestCmap()
    denoise_cmap = denoise_font.getBestCmap()

    base_glyf = base_font['glyf']
    denoise_glyf = denoise_font['glyf']
    base_hmtx = base_font['hmtx']
    denoise_hmtx = denoise_font['hmtx']

    ok = skip = 0
    for char in chars:
        if len(char) != 1:
            print(f"  Skip '{char}': not a single character")
            skip += 1
            continue

        code = ord(char)
        if code not in base_cmap:
            print(f"  Skip '{char}' (U+{code:04X}): not in base font")
            skip += 1
            continue
        if code not in denoise_cmap:
            print(f"  Skip '{char}' (U+{code:04X}): not in denoise font")
            skip += 1
            continue

        base_glyph_name = base_cmap[code]
        denoise_glyph_name = denoise_cmap[code]

        base_glyf[base_glyph_name] = copy.deepcopy(denoise_glyf[denoise_glyph_name])

        d_adv, d_lsb = denoise_hmtx[denoise_glyph_name]
        base_hmtx[base_glyph_name] = (d_adv, d_lsb)

        print(f"  Replaced '{char}'")
        ok += 1

    base_font.save(output_ttf)
    print()
    print(f"Done: replaced {ok}, skipped {skip}")
    print(f"Output: {output_ttf}")


if __name__ == '__main__':
    main()