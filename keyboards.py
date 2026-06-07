from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def user_main_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🚀 Boshlash"))
    kb.row(KeyboardButton(text="📦 Sizning zakazlaringiz"))
    return kb.as_markup(resize_keyboard=True)

def start_inline_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="🍽 Menyu", callback_data="open_menu"),
        InlineKeyboardButton(text="❓ Yordam", callback_data="open_help")
    )
    return kb.as_markup()

def category_keyboard(categories: list):
    kb = InlineKeyboardBuilder()
    emoji_map = {
        "taom": "🍲", "ovqat": "🍲", "shirinlik": "🍰", "desert": "🍰",
        "ichimlik": "🥤", "salat": "🥗", "non": "🍞", "sho'rva": "🍜",
        "grill": "🥩", "pizza": "🍕", "burger": "🍔", "set": "🎁"
    }
    for cat in categories:
        em = "🍽"
        for key, val in emoji_map.items():
            if key.lower() in cat.lower():
                em = val
                break
        kb.row(InlineKeyboardButton(text=f"{em} {cat.capitalize()}", callback_data=f"cat_{cat}"))
    kb.row(InlineKeyboardButton(text="📋 Barchasi", callback_data="cat_all"))
    return kb.as_markup()

def items_keyboard(items: list, cart: dict = None):
    kb = InlineKeyboardBuilder()
    for item in items:
        count = cart.get(item['id'], 0) if cart else 0
        label = f"{'✅ ' if count>0 else ''}{item['name']} — {item['price']:,} so'm"
        if count > 0:
            label += f" (x{count})"
        kb.row(InlineKeyboardButton(text=label, callback_data=f"item_{item['id']}"))
    if cart and sum(cart.values()) > 0:
        kb.row(InlineKeyboardButton(text="🛒 Zakaz berish", callback_data="checkout"))
    kb.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="open_menu"))
    return kb.as_markup()

def item_detail_keyboard(item_id: int, count: int):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="➖", callback_data=f"minus_{item_id}"),
        InlineKeyboardButton(text=str(count), callback_data="noop"),
        InlineKeyboardButton(text="➕", callback_data=f"plus_{item_id}")
    )
    kb.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_items"))
    return kb.as_markup()

def location_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📍 Lokatsiyamni yuborish", request_location=True))
    kb.row(KeyboardButton(text="❌ Bekor qilish"))
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)

def cancel_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="❌ Bekor qilish"))
    return kb.as_markup(resize_keyboard=True)

def admin_main_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🍽 Menyu"))
    kb.row(KeyboardButton(text="👤 Admin qo'shish"), KeyboardButton(text="🚴 Dastavchi qo'shish"))
    kb.row(KeyboardButton(text="📢 Reklama kanali qo'shish"))
    kb.row(KeyboardButton(text="📣 Reklama yuborish"))
    kb.row(KeyboardButton(text="🚫 Zakaz bekor qilish (Admin)"))
    return kb.as_markup(resize_keyboard=True)

def admin_menu_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="➕ Menyu kiritish", callback_data="menu_add"))
    kb.row(InlineKeyboardButton(text="👁 Menyu ko'rish", callback_data="menu_view"))
    kb.row(InlineKeyboardButton(text="🗑 Menudan o'chirish", callback_data="menu_delete"))
    return kb.as_markup()

def admin_delete_menu_keyboard(items: list):
    kb = InlineKeyboardBuilder()
    for item in items:
        kb.row(InlineKeyboardButton(
            text=f"🗑 {item['name']} ({item['category']})",
            callback_data=f"del_item_{item['id']}"
        ))
    kb.row(InlineKeyboardButton(text="❌ Yopish", callback_data="close"))
    return kb.as_markup()

def confirm_delete_keyboard(item_id: int, category: str):
    category_lower = category.lower()
    if "ichimlik" in category_lower:
        word = "ichimlikni"
    elif "shirinlik" in category_lower or "desert" in category_lower:
        word = "shirinlikni"
    elif "salat" in category_lower:
        word = "salatni"
    else:
        word = "taomni"
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="✅ Ha", callback_data=f"confirm_del_{item_id}"),
        InlineKeyboardButton(text="❌ Yo'q", callback_data="menu_delete")
    )
    return kb.as_markup(), word

def admin_cancel_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="❌ Bekor qilish"))
    return kb.as_markup(resize_keyboard=True)

def category_select_keyboard():
    categories = ["Taom", "Shirinlik", "Ichimlik", "Salat", "Grill", "Pizza", "Burger", "Sho'rva", "Non", "Set"]
    kb = InlineKeyboardBuilder()
    for cat in categories:
        kb.button(text=cat, callback_data=f"newcat_{cat}")
    kb.adjust(3)
    return kb.as_markup()

def courier_main_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="🍽 Tushlik / Dam olish"))
    return kb.as_markup(resize_keyboard=True)

def order_action_keyboard(order_id: int):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_{order_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{order_id}")
    )
    return kb.as_markup()

def delivery_time_keyboard(order_id: int):
    kb = InlineKeyboardBuilder()
    for minutes in [15, 20, 30, 45, 60]:
        kb.button(text=f"⏱ {minutes} daqiqa", callback_data=f"time_{order_id}_{minutes}")
    kb.adjust(3)
    return kb.as_markup()

def complete_order_keyboard(order_id: int):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="✅ Zakaz yetkazildi", callback_data=f"complete_{order_id}"))
    return kb.as_markup()

def promo_cancel_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="❌ Bekor qilish"))
    return kb.as_markup(resize_keyboard=True)
