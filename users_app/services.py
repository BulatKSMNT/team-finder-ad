import hashlib
import io

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import (
    AVATAR_BACKGROUND_COLORS,
    AVATAR_FALLBACK_FONT_NAME,
    AVATAR_FILE_HASH_LENGTH,
    AVATAR_FONT_NAME,
    AVATAR_FONT_SIZE,
    AVATAR_GENERATED_PREFIX,
    AVATAR_IMAGE_EXTENSION,
    AVATAR_IMAGE_FORMAT,
    AVATAR_IMAGE_MODE,
    AVATAR_IMAGE_SIZE,
    AVATAR_TEXT_COLOR,
    AVATAR_TEXT_VERTICAL_OFFSET,
)


def normalize_phone(phone):
    if not phone:
        return None

    phone = str(phone).strip()

    if phone.startswith("8"):
        return "+7" + phone[1:]

    return phone


def get_phone_uniqueness_variants(phone):
    normalized_phone = normalize_phone(phone)

    if not normalized_phone:
        return []

    variants = {normalized_phone}

    if normalized_phone.startswith("+7") and len(normalized_phone) == 12:
        variants.add("8" + normalized_phone[2:])

    return list(variants)


def get_avatar_font():
    try:
        return ImageFont.truetype(AVATAR_FONT_NAME, AVATAR_FONT_SIZE)
    except OSError:
        try:
            return ImageFont.truetype(
                AVATAR_FALLBACK_FONT_NAME,
                AVATAR_FONT_SIZE,
            )
        except OSError:
            return ImageFont.load_default(size=AVATAR_FONT_SIZE)


def generate_initial_avatar_content(email, name):
    letter_source = name or email or "U"
    letter = letter_source[0].upper()

    hash_value = int(
        hashlib.sha256(letter_source.encode("utf-8")).hexdigest(),
        16,
    )
    background_color = AVATAR_BACKGROUND_COLORS[
        hash_value % len(AVATAR_BACKGROUND_COLORS)
    ]

    image = Image.new(
        AVATAR_IMAGE_MODE,
        (AVATAR_IMAGE_SIZE, AVATAR_IMAGE_SIZE),
        background_color,
    )
    draw = ImageDraw.Draw(image)
    font = get_avatar_font()

    text_bbox = draw.textbbox((0, 0), letter, font=font)

    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    x = (AVATAR_IMAGE_SIZE - text_width) / 2 - text_bbox[0]
    y = (
        (AVATAR_IMAGE_SIZE - text_height) / 2
        - text_bbox[1]
        - AVATAR_TEXT_VERTICAL_OFFSET
    )

    draw.text(
        (x, y),
        letter,
        fill=AVATAR_TEXT_COLOR,
        font=font,
    )

    buffer = io.BytesIO()
    image.save(buffer, format=AVATAR_IMAGE_FORMAT)

    file_hash = hashlib.sha256(
        (email or letter_source).encode("utf-8")
    ).hexdigest()[:AVATAR_FILE_HASH_LENGTH]

    filename = (
        f"{AVATAR_GENERATED_PREFIX}_{file_hash}."
        f"{AVATAR_IMAGE_EXTENSION}"
    )

    return filename, ContentFile(buffer.getvalue())
