import logging
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# আপনার টেলিগ্রাম বটের টোকেন এখানে বসান
API_TOKEN = '9007270138:AAFpLNlbxzAZpADhRGXbE00aZrzyoEVmDv0'

# আপনার নিজের টেলিগ্রাম ইউজার আইডি এখানে বসান (অ্যাডমিন নোটিফিকেশনের জন্য)
ADMIN_ID = 123456789  # <--- এখানে আপনার টেলিগ্রাম আইডি বসাবেন

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

user_balances = {}
user_referrals = {}

# পাসওয়ার্ড সবার জন্য একই থাকবে, শুধু ইউনিক ইউজারনেমগুলোর লিস্ট
SHARED_PASSWORD = "Rafiq@07"

INSTAGRAM_USERNAMES_POOL = [
    "ronaldwzj6t607",
    "johndoe99x88",
    "smith_kvin44",
    "alex_turner77b",
    "david_miller33k",
    "michael_scott88v",
    "chris_hems99p",
    "robert_downey55j",
    "william_smith22x",
    "james_bond007z"
]

# ইউজারদের ইতিমধ্যে কোন অ্যাকাউন্ট দেওয়া হয়েছে তা ট্র্যাক করার জন্য ডিকশনারি
assigned_ig_accounts = {}

# স্টেট ক্লাস
class FBTaskSteps(StatesGroup):
    waiting_for_uid = State()
    waiting_for_cookie = State()

class IGTaskSteps(StatesGroup):
    waiting_for_2fa_key = State()

# নিচের ফিক্সড মেনু কিবোর্ড (Reply Keyboard)
def get_reply_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("💰 ব্যালেন্স"),
        KeyboardButton("📋 কাজ"),
        KeyboardButton("💼 উত্তোলন"),
        KeyboardButton("🟢 সাপোর্ট"),
        KeyboardButton("👥 আমার রেফারেল"),
        KeyboardButton("💬 আমি নতুন"),
        KeyboardButton("🛒 প্রক্সি কিনুন"),
        KeyboardButton("🌐 ভাষা পরিবর্তন")
    )
    return keyboard

# /start কমান্ড হ্যান্ডলার
@dp.message_handler(commands=['start'], state="*")
async def send_welcome(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    
    if user_id not in user_balances:
        user_balances[user_id] = 0.0
    if user_id not in user_referrals:
        user_referrals[user_id] = 0

    welcome_text = (
        f"স্বাগতম, {message.from_user.first_name}!

"
        "আমাদের অফিসিয়াল ফেসবুক ও ইনস্টাগ্রাম আইডি বাই-সেল এবং আর্নিং বটে আপনাকে স্বাগতম।\n"
        "নিচে দেওয়া অপশনগুলো থেকে কাজ শুরু করুন:"
    )
    await message.answer(welcome_text, reply_markup=get_reply_menu())

# "📋 কাজ" চাপলে টাস্ক ক্যাটাগরি আসবে
@dp.message_handler(text="📋 কাজ", state="*")
async def show_task_categories(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Fb Cookies (4.00 BDT)", callback_data="fb_task"),
        InlineKeyboardButton("Instagram 2FA (3.20 BDT)", callback_data="ig_task"),
        InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")
    )
    await message.answer("🔻 **যেকোনো একটি কাজ সিলেক্ট করুন:**", reply_markup=keyboard, parse_mode="Markdown")

# অন্যান্য মেনু অপশন
@dp.message_handler(text="💰 ব্যালেন্স", state="*")
async def show_balance(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    balance = user_balances.get(user_id, 0.0)
    await message.answer(f"💳 **আপনার বর্তমান ব্যালেন্স:** ৳ {balance:.2f}", parse_mode="Markdown")

@dp.message_handler(text="💼 উত্তোলন", state="*")
async def show_withdraw(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("💸 **উইথড্র করার নিয়ম:**\nন্যূনতম ব্যালেন্স ২০০ টাকা হলে পেমেন্ট নিতে পারবেন। পেমেন্ট রিকোয়েস্ট দিতে অ্যাডমিনের সাথে যোগাযোগ করুন।", parse_mode="Markdown")

@dp.message_handler(text="👥 আমার রেফারেল", state="*")
async def show_referral(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
    ref_count = user_referrals.get(user_id, 0)
    await message.answer(f"👥 **আপনার রেফারেল লিংক:**\n{ref_link}\n\n📊 মোট রেফার: {ref_count} জন", parse_mode="Markdown")

# প্রক্সি কিনুন বাটন (স্ক্রিনশটের লিস্ট অনুযায়ী ২০ টাকা বাড়িয়ে দেখানো হয়েছে)
@dp.message_handler(text="🛒 প্রক্সি কিনুন", state="*")
async def show_proxies(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("ABC [GB] - 290.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("711 Proxy [key🔑] - 105.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("9 Proxy [key🔑] - 130.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("Cli Proxy [key🔑] - 120.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("Nov Proxy [key🔑] - 140.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("Proxy 001 [key🔑] - 130.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("DATAMPLUS [key🔑] - 150.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("Repaid Proxy [key🔑] - 130.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("Helodata Proxy [key🔑] - 140.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("Loki Proxy [key🔑] - 130.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("B2 Proxy [1GB key🔑] - 120.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("Evomi Proxy [1GB key🔑] - 150.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("IPRocket Proxy [2GB key🔑] - 230.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("ThorData Proxy [2 GB key🔑] - 230.0 BDT", callback_data="proxy_buy"),
        InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")
    )
    await message.answer("🌐 **প্রক্সি লিস্ট (অটো ডেলিভারি):**\nনিচের প্যাকেজগুলো থেকে পছন্দমত সিলেক্ট করুন:", reply_markup=keyboard, parse_mode="Markdown")

@dp.message_handler(text=["🟢 সাপোর্ট", "💬 আমি নতুন", "🌐 ভাষা পরিবর্তন"], state="*")
async def general_buttons(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(f"আপনি '{message.text}' অপশনটি সিলেক্ট করেছেন। এটি খুব শীঘ্রই আপডেট করা হবে।", reply_markup=get_reply_menu())


# --- ফেসবুক টাস্ক ---
@dp.callback_query_handler(text="fb_task")
async def fb_task_start(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("❌ বাতিল", callback_data="cancel_task"))
    
    await bot.answer_callback_query(callback_query.id)
    await FBTaskSteps.waiting_for_uid.set()
    
    task_info_text = (
        "📘 **Facebook Account Creation Info:**\n\n"
        "🔹 **First Name:** Scott\n"
        "🔹 **Last Name:** Flores\n"
        "🔒 **Password:** Samir@06\n\n"
        "🟢 **অ্যাকাউন্ট তৈরি করা হয়ে গেলে, আপনার Facebook User ID (UID) লিখে পাঠান:**"
    )
    
    await bot.edit_message_text(
        task_info_text,
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.message_handler(state=FBTaskSteps.waiting_for_uid)
async def receive_fb_uid(message: types.Message, state: FSMContext):
    uid_text = message.text.strip()

    is_valid_uid = False
    if uid_text.isdigit() and len(uid_text) >= 5:
        is_valid_uid = True
    elif "facebook.com" in uid_text or "profile.php" in uid_text:
        is_valid_uid = True

    if not is_valid_uid:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("❌ বাতিল", callback_data="cancel_task"))
        
        await message.answer(
            "❌ **ভুল UID দিয়েছেন!**\n\n"
            "💬 দয়া করে আপনার সঠিক এবং আসল Facebook UID-টি দেখে আবার লিখে পাঠান:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        return

    async with state.proxy() as data:
        data['fb_uid'] = uid_text

    await FBTaskSteps.waiting_for_cookie.set()

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("❌ বাতিল", callback_data="cancel_task"))

    await message.answer(
        "✅ **Facebook Task - Step 2/2:**\n\n"
        "এবার আপনার ব্রাউজার থেকে কপি করা ফেসবুক অ্যাকাউন্টের **Cookies** কোডটি এখানে পেস্ট করে পাঠিয়ে দিন:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.message_handler(state=FBTaskSteps.waiting_for_cookie)
async def receive_fb_cookie(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    cookie_text = message.text.strip()

    if "c_user" not in cookie_text:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("❌ বাতিল", callback_data="cancel_task"))
        
        await message.answer(
            "❌ **ভুল Cookies দিয়েছেন!**\n\n"
            "💬 দয়া করে ব্রাউজার থেকে সঠিক কুকিজ (যাতে `c_user` থাকে) কপি করে আবার পাঠান:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        return

    async with state.proxy() as data:
        fb_uid = data.get('fb_uid')

    await state.finish()

    admin_text = (
        f"📥 **নতুন ফেসবুক টাস্ক সাবমিশন!**\n\n"
        f"👤 ইউজার: {user_name} (ID: `{user_id}`)\n"
        f"🆔 UID: `{fb_uid}`\n"
        f"🍪 Cookies:\n`{cookie_text}`\n\n"
        f"💵 রেট: ৳ ৪.০০"
    )
    
    try:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("✅ Approve & Send ৳4", callback_data=f"app_fb_{user_id}_4"),
            InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")
        )
        await bot.send_message(ADMIN_ID, admin_text, reply_markup=keyboard, parse_mode="Markdown")
    except:
        pass

    await message.answer(
        "⏳ আপনার ফেসবুক তথ্য সফলভাবে সাবমিট হয়েছে!\n"
        "অ্যাডমিন চেক করার পর আপনার অ্যাকাউন্টে **৳ ৪.০০** যোগ করে দেওয়া হবে।",
        reply_markup=get_reply_menu(),
        parse_mode="Markdown"
    )


# --- ইনস্টাগ্রাম টাস্ক (একই পাসওয়ার্ড এবং ইউনিক ইউজারনেম অ্যাসাইনমেন্ট সিস্টেম) ---
@dp.callback_query_handler(text="ig_task")
async def ig_task_start(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id in assigned_ig_accounts:
        selected_username = assigned_ig_accounts[user_id]
    else:
        available_usernames = [uname for uname in INSTAGRAM_USERNAMES_POOL if uname not in assigned_ig_accounts.values()]
        
        if not available_usernames:
            await bot.answer_callback_query(callback_query.id, "দুঃখিত, এই মুহূর্তে নতুন কোনো ইনস্টাগ্রাম অ্যাকাউন্ট খালি নেই!", show_alert=True)
            return
        
        selected_username = random.choice(available_usernames)
        assigned_ig_accounts[user_id] = selected_username

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🟢 2FA Set", callback_data="ig_set_2fa"),
        InlineKeyboardButton("❓ কিভাবে কাজ করব", callback_data="ig_help"),
        InlineKeyboardButton("❌ বাতিল", callback_data="cancel_task")
    )
    
    await bot.answer_callback_query(callback_query.id)
    
    ig_text = (
        "📸 **Instagram 2FA (Reward: ৳৩.২০):**\n\n"
        f"👤 **Username:** `{selected_username}`\n"
        f"🔒 **Password:** `{SHARED_PASSWORD}`\n\n"
        "📌 **উপরের ইউনিক ইউজারনেম এবং পাসওয়ার্ড দিয়ে অ্যাকাউন্ট খুলুন। তারপর নিচে 2FA Set বাটনে ক্লিক করুন 👇**"
    )
    
    await bot.edit_message_text(
        ig_text,
        callback_query.from_user.id,
        callback_query.message.message_id,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query_handler(text="ig_set_2fa")
async def ig_set_2fa_click(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("❌ বাতিল", callback_data="cancel_task"))
    
    await bot.answer_callback_query(callback_query.id)
    await IGTaskSteps.waiting_for_2fa_key.set()
    
    await bot.send_message(
        callback_query.from_user.id,
        "⚠️ **সঠিক 2FA Key দিন (অবশ্যই ১৬ বা ৩২ অক্ষরের এবং বড় হাতের অক্ষরে হতে হবে):** 👇",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query_handler(text="ig_help")
async def ig_help_click(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, "ইনস্টাগ্রাম অ্যাকাউন্ট খুলে 2FA সেটআপ করার পর Key এখানে দিন।", show_alert=True)

@dp.callback_query_handler(text="proxy_buy")
async def proxy_buy_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id, "প্রক্সি ক্রয়ের জন্য পর্যাপ্ত ব্যালেন্স নেই অথবা ডিপোজিট করুন।", show_alert=True)

@dp.message_handler(state=IGTaskSteps.waiting_for_2fa_key)
async def receive_ig_2fa_key(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    fa_key = message.text.strip()

    if len(fa_key) < 10:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("❌ বাতিল", callback_data="cancel_task"))
        
        await message.answer(
            "❌ **ভুল 2FA Key দিয়েছেন!**\n\n"
            "💬 দয়া করে সঠিক 2FA Key আবার লিখে পাঠান:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        return

    ig_username = assigned_ig_accounts.get(user_id, "Unknown")
    await state.finish()

    admin_text = (
        f"📥 **নতুন ইনস্টাগ্রাম 2FA টাস্ক সাবমিশন!**\n\n"
        f"👤 ইউজার: {user_name} (ID: `{user_id}`)\n"
        f"📸 Username: `{ig_username}`\n"
        f"🔒 Password: `{SHARED_PASSWORD}`\n"
        f"🛡️ 2FA Key:\n`{fa_key}`\n\n"
        f"💵 রেট: ৳ ৩.২০"
    )
    
    try:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("✅ Approve & Send ৳3.20", callback_data=f"app_ig_{user_id}_3.2"),
            InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user_id}")
        )
        await bot.send_message(ADMIN_ID, admin_text, reply_markup=keyboard, parse_mode="Markdown")
    except:
        pass

    await message.answer(
        "⏳ আপনার ইনস্টাগ্রাম 2FA Key সফলভাবে সাবমিট হয়েছে!\n"
        "অ্যাডমিন চেক করার পর আপনার অ্যাকাউন্টে **৳ ৩.২০** যোগ করে দেওয়া হবে।",
        reply_markup=get_reply_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query_handler(text="cancel_task", state="*")
async def cancel_task(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.answer_callback_query(callback_query.id)
    try:
        await bot.edit_message_text("❌ টাস্ক বাতিল করা হয়েছে।", callback_query.from_user.id, callback_query.message.message_id)
    except:
        pass
    await bot.send_message(callback_query.from_user.id, "আপনাকে প্রধান মেনুতে ফিরিয়ে আনা হয়েছে!", reply_markup=get_reply_menu())

@dp.callback_query_handler(lambda c: c.data.startswith('app_') or c.data.startswith('rej_'))
async def admin_action(callback_query: types.CallbackQuery):
    data_parts = callback_query.data.split('_')
    action = data_parts[0]
    target_user_id = int(data_parts[2])

    await bot.answer_callback_query(callback_query.id)

    if action == 'app':
        amount = float(data_parts[3])
        user_balances[target_user_id] = user_balances.get(target_user_id, 0.0) + amount
        
        try:
            await bot.send_message(target_user_id, f"🎉 অভিনন্দন! আপনার টাস্ক অ্যাডমিন কর্তৃক অনুমোদিত হয়েছে। আপনার ব্যালেন্সে **৳ {amount}** যোগ করা হয়েছে।", parse_mode="Markdown")
        except:
            pass

        await bot.edit_message_text(
            f"{callback_query.message.text}\n\n✅ **Status: Approved (৳ {amount} added)**",
            callback_query.from_user.id,
            callback_query.message.message_id
        )
    elif action == 'rej':
        try:
            await bot.send_message(target_user_id, "❌ দুঃখিত, আপনার টাস্কটি সঠিক না হওয়ায় অ্যাডমিন কর্তৃক বাতিল করা হয়েছে।")
        except:
            pass

        await bot.edit_message_text(
            f"{callback_query.message.text}\n\n❌ **Status: Rejected**",
            callback_query.from_user.id,
            callback_query.message.message_id
        )

@dp.callback_query_handler(text="main_menu", state="*")
async def back_to_main(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.answer_callback_query(callback_query.id)
    try:
        await bot.edit_message_text("মূল মেনুতে ফিরে যাওয়া হয়েছে:", callback_query.from_user.id, callback_query.message.message_id)
    except:
        pass
    await bot.send_message(callback_query.from_user.id, "নিচের অপশনগুলো ব্যবহার করুন:", reply_markup=get_reply_menu())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
