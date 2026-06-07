import json
import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

import database as db
from keyboards import (
    courier_main_keyboard, order_action_keyboard,
    delivery_time_keyboard, complete_order_keyboard
)

router = Router()
logger = logging.getLogger(__name__)

active_timers = {}
break_votes_set = set()
break_task = None

@router.message(Command("courier"))
async def courier_panel(message: Message):
    if not await db.is_courier(message.from_user.id):
        await message.answer("❌ Sizda kuryer huquqi yo'q.")
        return
    await message.answer(
        "🚴 <b>Kuryer paneli</b>\n\nZakazlar bu yerga tushadi.",
        reply_markup=courier_main_keyboard(), parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("accept_"))
async def accept_order(call: CallbackQuery):
    order_id = int(call.data.replace("accept_", ""))
    order = await db.get_order(order_id)
    if not order:
        await call.answer("Zakaz topilmadi.", show_alert=True)
        return
    if order['status'] != 'pending':
        await call.answer("Bu zakaz allaqachon qayta ishlangan.", show_alert=True)
        return
    await call.message.edit_reply_markup(reply_markup=delivery_time_keyboard(order_id))
    await call.answer("⏱ Yetkazish vaqtini tanlang")

@router.callback_query(F.data.startswith("time_"))
async def set_delivery_time(call: CallbackQuery, bot: Bot):
    parts = call.data.split("_")
    order_id, minutes = int(parts[1]), int(parts[2])
    order = await db.get_order(order_id)
    if not order or order['status'] != 'pending':
        await call.answer("Zakaz allaqachon qayta ishlangan.", show_alert=True)
        return

    is_ok = await db.is_admin(call.from_user.id) or await db.is_courier(call.from_user.id)
    if not is_ok:
        await call.answer("Ruxsat yo'q.", show_alert=True)
        return

    await db.accept_order(order_id, call.from_user.id, minutes)

    items_data = json.loads(order['items'])
    items_text = "\n".join([f"• {it['name']} x{it['count']} — {it['price']*it['count']:,} so'm" for it in items_data])

    await call.message.edit_text(
        f"✅ <b>Zakaz #{order_id} qabul qilindi!</b>\n\n"
        f"👤 {order['user_name']} | 📞 {order['phone']}\n"
        f"📍 {order['location']}\n\n"
        f"🛒 {items_text}\n\n"
        f"💰 {order['total_price']:,} so'm | ⏱ {minutes} daqiqa",
        parse_mode="HTML", reply_markup=complete_order_keyboard(order_id)
    )

    try:
        await bot.send_message(
            order['user_id'],
            f"🚴 <b>Zakazingiz #{order_id} qabul qilindi!</b>\n\n"
            f"⏱ Taxminan <b>{minutes} daqiqa</b> ichida yetkaziladi.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Mijozga xabar ketmadi: {e}")

    if order_id in active_timers:
        active_timers[order_id].cancel()

    task = asyncio.create_task(
        delivery_timer(bot, order_id, order['user_id'], call.from_user.id, minutes)
    )
    active_timers[order_id] = task
    await call.answer(f"✅ Qabul! {minutes} daqiqa taymer boshlandi.")

async def delivery_timer(bot: Bot, order_id: int, user_id: int, courier_id: int, minutes: int):
    await asyncio.sleep(minutes * 60)
    order = await db.get_order(order_id)
    if not order or order['status'] != 'accepted':
        return
    late = 0
    while True:
        late += 1
        await asyncio.sleep(60)
        order = await db.get_order(order_id)
        if not order or order['status'] != 'accepted':
            break
        try:
            await bot.send_message(courier_id, f"⚠️ Zakaz #{order_id}: {late} daqiqa kechikmoqda!")
        except:
            pass
        if late >= 10:
            break

@router.callback_query(F.data.startswith("reject_"))
async def reject_order(call: CallbackQuery, bot: Bot):
    order_id = int(call.data.replace("reject_", ""))
    order = await db.get_order(order_id)
    if not order or order['status'] != 'pending':
        await call.answer("Allaqachon qayta ishlangan.", show_alert=True)
        return
    await db.reject_order(order_id)
    await call.message.edit_text(f"❌ <b>Zakaz #{order_id} rad etildi.</b>", parse_mode="HTML")
    try:
        await bot.send_message(order['user_id'], f"😔 #{order_id} zakazingiz rad etildi.")
    except:
        pass

@router.callback_query(F.data.startswith("complete_"))
async def complete_order(call: CallbackQuery, bot: Bot):
    order_id = int(call.data.replace("complete_", ""))
    order = await db.get_order(order_id)
    if not order:
        await call.answer("Topilmadi.", show_alert=True)
        return
    await db.complete_order(order_id)
    if order_id in active_timers:
        active_timers[order_id].cancel()
        del active_timers[order_id]
    await call.message.edit_text(f"✅ <b>Zakaz #{order_id} yetkazildi!</b>", parse_mode="HTML")
    try:
        await bot.send_message(order['user_id'], f"🎉 Zakazingiz #{order_id} yetkazildi! Rahmat 😊")
    except:
        pass

@router.message(F.text == "🍽 Tushlik / Dam olish")
async def lunch_break(message: Message, bot: Bot):
    global break_task
    if not await db.is_courier(message.from_user.id):
        return
    couriers = await db.get_couriers()
    if not couriers:
        return
    uid = message.from_user.id
    if uid in break_votes_set:
        await message.answer(f"✅ Ovoz berdingiz. ({len(break_votes_set)}/{len(couriers)}) Boshqalarni kuting.")
        return
    break_votes_set.add(uid)
    voted, total = len(break_votes_set), len(couriers)
    await message.answer(f"✅ Ovozingiz qabul qilindi! ({voted}/{total})")
    all_ids = {c['user_id'] for c in couriers}
    if break_votes_set >= all_ids:
        break_votes_set.clear()
        for c in couriers:
            try:
                await bot.send_message(c['user_id'],
                    "🍽 <b>Tushlik boshlandi! 1 soat dam olish.</b>\n"
                    "Bu vaqtda zakazlar qabul qilinmaydi.", parse_mode="HTML")
            except:
                pass
        if break_task:
            break_task.cancel()
        break_task = asyncio.create_task(break_timer(bot, [c['user_id'] for c in couriers]))

async def break_timer(bot: Bot, courier_ids: list):
    for left in range(60, 0, -1):
        await asyncio.sleep(60)
        if left in [30, 15, 5, 1]:
            for uid in courier_ids:
                try:
                    await bot.send_message(uid, f"⏰ Tushlikka <b>{left} daqiqa</b> qoldi!", parse_mode="HTML")
                except:
                    pass
    for uid in courier_ids:
        try:
            await bot.send_message(uid, "✅ <b>Tushlik tugadi! Ish boshlandi.</b>", parse_mode="HTML")
        except:
            pass
