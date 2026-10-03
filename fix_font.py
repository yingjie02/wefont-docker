#!/usr/bin/env python3
"""Fix font name table and OS/2 table for Chinese support in Word
Usage: python fix_font.py input.ttf output.ttf family_name
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord

if len(sys.argv) != 4:
    print('Usage: python fix_font.py input.ttf output.ttf family_name')
    sys.exit(1)

input_ttf, output_ttf, family_name = sys.argv[1], sys.argv[2], sys.argv[3]
font = TTFont(input_ttf)

# ---------- Fix name table ----------
name_table = font['name']
name_table.names = [r for r in name_table.names if r.nameID not in (1, 4, 6)]

for nameID in (1, 4, 6):
    # Windows Unicode BMP
    rec = NameRecord()
    rec.nameID = nameID
    rec.platformID = 3
    rec.platEncID = 1
    rec.langID = 0x409
    rec.string = family_name.encode('utf-16-be')
    name_table.names.append(rec)

    # Mac Roman
    rec2 = NameRecord()
    rec2.nameID = nameID
    rec2.platformID = 1
    rec2.platEncID = 0
    rec2.langID = 0
    rec2.string = family_name.encode('latin-1', errors='replace')
    name_table.names.append(rec2)

# ---------- Fix OS/2 table: add GB2312 and GBK ----------
os2 = font['OS/2']
os2.ulCodePageRange1 |= (1 << 18) | (1 << 19)
os2.ulUnicodeRange2 |= (1 << 0) | (1 << 1) | (1 << 2)

font.save(output_ttf)
print('Font fixed: ' + output_ttf)