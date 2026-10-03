#!/usr/bin/env python3
"""Fix parse_template.py: QR code recognition + denoise + remove matplotlib"""

path = '/workspace/wefont/src/parse_template.py'
with open(path, 'r') as f:
    content = f.read()

# ---------- 1. Remove matplotlib import ----------
content = content.replace('from matplotlib import pyplot as plt\n', '')

# ---------- 2. Replace verbose plotting with print (first occurrence) ----------
old_verbose = '''    if verbose:
        plt.imshow(img, cmap='gray', interpolation='bicubic')
        plt.xticks([]), plt.yticks([])
        plt.show()'''

new_verbose = '''    if verbose:
        print("Rotated image shape:", img.shape)'''

if old_verbose in content:
    content = content.replace(old_verbose, new_verbose)

# ---------- 3. Replace second plt block ----------
old_plt2 = '''        plt.imshow(color_img, cmap='gray', interpolation='bicubic')
        plt.xticks([]), plt.yticks([])
        plt.show()'''

new_plt2 = '''        print("Skipping image display")'''

if old_plt2 in content:
    content = content.replace(old_plt2, new_plt2)

# ---------- 4. Adjust binarization threshold ----------
content = content.replace('thres = 128', 'thres = 140')

# ---------- 5. Enhance decode_qrcode with multi-scale + multi-threshold retry ----------
old_func = '''def decode_qrcode(qrcode):
    decoded_obj = decode(qrcode)
    if decoded_obj:
        return decoded_obj[0].data.decode()'''

new_func = '''def decode_qrcode(qrcode):
    decoded_obj = decode(qrcode)
    if decoded_obj:
        return decoded_obj[0].data.decode()
    for scale in [2, 3]:
        bigger = cv2.resize(qrcode, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        decoded_obj = decode(bigger)
        if decoded_obj:
            return decoded_obj[0].data.decode()
    for t in [100, 140, 160, 180, 200]:
        _, binary = cv2.threshold(qrcode, t, 255, cv2.THRESH_BINARY)
        decoded_obj = decode(binary)
        if decoded_obj:
            return decoded_obj[0].data.decode()
    return None'''

if old_func not in content:
    raise SystemExit('ERROR: decode_qrcode not found')
content = content.replace(old_func, new_func)

# ---------- 6. Save original gray image before binarization ----------
old_start = '''def parse_template(img, verbose):
    ret, img = cv2.threshold(img, thres, 255, cv2.THRESH_BINARY)'''

new_start = '''def parse_template(img, verbose):
    original_gray = img.copy()
    ret, img = cv2.threshold(img, thres, 255, cv2.THRESH_BINARY)'''

if old_start not in content:
    raise SystemExit('ERROR: parse_template function header not found')
content = content.replace(old_start, new_start)

# ---------- 7. Fallback to original gray image if QR decode fails ----------
old_fallback = '''    qrdata = decode_qrcode(qrcode)
    if not qrdata:
        if verbose:
            print("Trying bigger qrcode")'''

new_fallback = '''    qrdata = decode_qrcode(qrcode)
    if not qrdata:
        qrdata = decode_qrcode(original_gray)
    if not qrdata:
        qrdata = decode_qrcode(img)
    if not qrdata:
        if verbose:
            print("Trying bigger qrcode")'''

if old_fallback not in content:
    raise SystemExit('ERROR: QR fallback code not found')
content = content.replace(old_fallback, new_fallback)

# ---------- 8. Denoise: remove small isolated connected components ----------
old_write = '''        char_img = cv2.equalizeHist(char_img)
        cv2.imwrite(glyname + '.png', char_img)'''

new_write = '''        char_img = cv2.equalizeHist(char_img)

        # Remove small isolated noise (connected component analysis)
        _, char_bin = cv2.threshold(char_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(char_bin, connectivity=8)
        areas = stats[1:, cv2.CC_STAT_AREA]
        if len(areas) > 0:
            max_area = areas.max()
            min_area = max(30, int(max_area * 0.05))
            for i in range(1, num_labels):
                if stats[i, cv2.CC_STAT_AREA] < min_area:
                    char_bin[labels == i] = 0
        char_img = cv2.bitwise_not(char_bin)

        cv2.imwrite(glyname + '.png', char_img)'''

if old_write not in content:
    raise SystemExit('ERROR: char_img imwrite not found')
content = content.replace(old_write, new_write)

with open(path, 'w') as f:
    f.write(content)

print('parse_template.py patched OK (QR + denoise)')