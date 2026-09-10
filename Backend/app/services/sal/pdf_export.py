"""Minimal PDF builder for quotation export (no external deps)."""

import base64
import binascii
import re
import struct
import zlib
from dataclasses import dataclass
from decimal import Decimal


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


@dataclass(frozen=True)
class PdfLogo:
    width: int
    height: int
    data: bytes
    image_format: str  # jpeg | png_rgb


def tenant_initials(tenant_name: str) -> str:
    tokens = [t for t in tenant_name.replace("(", " ").replace(")", " ").split() if t]
    if not tokens:
        return "EL"
    if len(tokens) == 1:
        return tokens[0][:2].upper()
    return f"{tokens[0][0]}{tokens[1][0]}".upper()


def _decode_png_rgb(png_bytes: bytes) -> tuple[int, int, bytes] | None:
    if png_bytes[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    offset = 8
    width = height = 0
    bit_depth = color_type = 0
    idat = bytearray()
    while offset + 8 <= len(png_bytes):
        length = struct.unpack(">I", png_bytes[offset : offset + 4])[0]
        chunk_type = png_bytes[offset + 4 : offset + 8]
        chunk_data = png_bytes[offset + 8 : offset + 8 + length]
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", chunk_data[:10])
        elif chunk_type == b"IDAT":
            idat.extend(chunk_data)
        elif chunk_type == b"IEND":
            break
        offset += 12 + length
    if width <= 0 or height <= 0 or bit_depth != 8 or color_type not in (2, 6):
        return None
    stride = width * (3 if color_type == 2 else 4)
    raw = zlib.decompress(bytes(idat))
    rgb = bytearray()
    pos = 0
    for _ in range(height):
        pos += 1  # filter byte
        row = raw[pos : pos + stride]
        pos += stride
        if color_type == 2:
            rgb.extend(row)
        else:
            for i in range(0, len(row), 4):
                rgb.extend(row[i : i + 3])
    return width, height, bytes(rgb)


def _jpeg_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i + 1 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        i += 2
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            if i + 7 <= len(data):
                height = struct.unpack(">H", data[i + 3 : i + 5])[0]
                width = struct.unpack(">H", data[i + 5 : i + 7])[0]
                if width > 0 and height > 0:
                    return width, height
            return None
        if marker in (0xD8, 0xD9):
            if marker == 0xD9:
                break
            continue
        if i + 2 > len(data):
            break
        seg_len = struct.unpack(">H", data[i : i + 2])[0]
        if seg_len < 2:
            break
        i += seg_len
    return None


def resolve_logo_for_pdf(logo_url: str | None) -> PdfLogo | None:
    if not logo_url:
        return None
    jpeg_match = re.match(r"^data:image/jpeg;base64,(.+)$", logo_url, re.IGNORECASE)
    if jpeg_match:
        try:
            data = base64.b64decode(jpeg_match.group(1), validate=True)
        except (ValueError, binascii.Error):
            return None
        dims = _jpeg_dimensions(data)
        if dims is None:
            return PdfLogo(width=1, height=1, data=data, image_format="jpeg")
        width, height = dims
        return PdfLogo(width=width, height=height, data=data, image_format="jpeg")
    png_match = re.match(r"^data:image/png;base64,(.+)$", logo_url, re.IGNORECASE)
    if png_match:
        try:
            png_bytes = base64.b64decode(png_match.group(1), validate=True)
        except (ValueError, binascii.Error):
            return None
        parsed = _decode_png_rgb(png_bytes)
        if parsed is None:
            return None
        width, height, rgb = parsed
        return PdfLogo(width=width, height=height, data=rgb, image_format="png_rgb")
    return None


def _hex_rgb(hex_color: str | None) -> tuple[float, float, float] | None:
    if not hex_color or len(hex_color) != 7 or not hex_color.startswith("#"):
        return None
    try:
        return (
            int(hex_color[1:3], 16) / 255.0,
            int(hex_color[3:5], 16) / 255.0,
            int(hex_color[5:7], 16) / 255.0,
        )
    except ValueError:
        return None


def build_quotation_pdf(
    quotation_number: str,
    currency_code: str,
    grand_total: str,
    status: str,
    subtotal: str,
    tax_total: str,
    lines: list[tuple[int, str, str, str]],
    *,
    tenant_name: str = "E-LinkUp CRM",
    generated_on: str | None = None,
    logo_initials: str | None = None,
    logo: PdfLogo | None = None,
    primary_color: str | None = None,
) -> bytes:
    footer = generated_on or ""
    rows = [
        tenant_name,
        "Powered by E-LinkUp CRM",
        "",
        f"Quotation: {quotation_number}",
        f"Status: {status}",
        "",
        "Line  Description              Qty    Amount",
        "----  -----------------------  -----  --------",
    ]
    for line_no, desc, qty, total in lines:
        rows.append(f"{line_no:>4}  {desc[:23]:<23}  {qty:>5}  {total:>8}")
    rows.extend(
        [
            "",
            f"Subtotal: {currency_code} {subtotal}",
            f"Tax:      {currency_code} {tax_total}",
            f"Total:    {currency_code} {grand_total}",
            "",
            f"Generated: {footer}" if footer else "",
            f"Confidential — {tenant_name}",
        ]
    )
    rows = [r for r in rows if r]
    initials = logo_initials or tenant_initials(tenant_name)
    text_x = 100
    y = 778
    parts: list[str] = []
    accent = _hex_rgb(primary_color)
    if accent is not None:
        r, g, b = accent
        parts.extend(["q", f"{r:.3f} {g:.3f} {b:.3f} rg", "0 784 612 8 re f", "Q"])
    if logo is not None:
        parts.extend(["q", "40 0 0 40 50 744 cm", "/Im1 Do", "Q"])
    else:
        parts.extend(
            [
                "q",
                "0.92 0.92 0.92 rg",
                "50 744 40 40 re f",
                "0.45 0.45 0.45 RG",
                "50 744 40 40 re S",
                "Q",
                f"BT /F1 14 Tf 58 758 Td ({_pdf_escape(initials)}) Tj ET",
            ]
        )
    parts.extend(
        [
            "BT /F1 11 Tf",
            f"1 0 0 1 {text_x} {y} Tm ({_pdf_escape(rows[0])}) Tj",
        ]
    )
    for row in rows[1:]:
        parts.append(f"0 -14 Td ({_pdf_escape(row)}) Tj")
    parts.append("ET")
    stream = "\n".join(parts)
    stream_bytes = stream.encode("latin-1", errors="replace")
    objects: list[bytes] = []
    offsets: list[int] = []

    def add(obj: bytes) -> None:
        offsets.append(sum(len(p) for p in objects) + 9)
        objects.append(obj)

    add(b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n")
    add(b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n")
    if logo is not None:
        add(
            b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources<< /Font<< /F1 5 0 R >> /XObject<< /Im1 6 0 R >> >> >>endobj\n"
        )
    else:
        add(
            b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources<< /Font<< /F1 5 0 R >> >> >>endobj\n"
        )
    add(
        b"4 0 obj<< /Length "
        + str(len(stream_bytes)).encode()
        + b" >>stream\n"
        + stream_bytes
        + b"\nendstream\nendobj\n"
    )
    add(b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n")
    if logo is not None:
        if logo.image_format == "jpeg":
            img_header = (
                f"/Type /XObject /Subtype /Image /Width {logo.width} /Height {logo.height} "
                f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length {len(logo.data)}"
            )
        else:
            img_header = (
                f"/Type /XObject /Subtype /Image /Width {logo.width} /Height {logo.height} "
                f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {len(logo.data)}"
            )
        add(
            f"6 0 obj<< {img_header} >>stream\n".encode()
            + logo.data
            + b"\nendstream\nendobj\n"
        )
    size = 7 if logo is not None else 6
    header = b"%PDF-1.4\n"
    body = b"".join(objects)
    xref_pos = len(header) + len(body)
    xref = f"xref\n0 {size}\n0000000000 65535 f \n".encode()
    for off in offsets:
        xref += f"{off:010d} 00000 n \n".encode()
    trailer = f"trailer<< /Size {size} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    return header + body + xref + trailer


def format_line_row(line_no: int, description: str, qty: Decimal, line_total: Decimal) -> tuple[int, str, str, str]:
    return (line_no, description, f"{qty}", f"{line_total}")
