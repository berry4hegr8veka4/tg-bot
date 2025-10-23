import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = "8421088940:AAEi1hoa8Waeft18d5MU8tIuMA4hoasXee0"

# ID администратора
ADMIN_ID = 7669105039

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Хранилище данных
user_data = {}
achievements_data = {}
pending_submissions = {}

# Списки ачивок с наградами (пронумерованные)
ACHIEVEMENTS = {
    "ОБЩИЙ": {
        "1. Добро пожаловать!": {"reward": 2, "task": "Подписаться на тгк на 1 раз."},
        "2. Герои не носят плащи...": {"reward": 3, "task": "Помогите с набором."},
        "3. С далека если смотреть, то красиво.": {"reward": 1, "task": "Прийдите в мерче."},
        "4. Молодец возьми на полке кроны.": {"reward": 6, "task": "Проголосуйте за тгк проекта 1 раз."},
        "5. Да приветствует вас власть и иерархия!": {"reward": 10, "task": "Вступите в администрацию (как минимум побыть на наборах 3 раза)."},
        "6. Да приветствует вас НЕ власть и иерархия.": {"reward": 3, "task": "Встретить союзника лаборатории на рп/наборе."},
        "7. Again and again...": {"reward": 3, "task": "Вступите в ност 1 раз."},
        "8. Да.. да.. принято! В смысле там ещё 2 лимита тг.": {"reward": 10, "task": "Напишите анкету в носте/чате постояльцев 1 раз."},
        "9. Непростой Альянс.": {"reward": 3, "task": "Купите что-то в магазине Себастьяна впервые."},
        "10. Именно так лишаются девственности.": {"reward": 1, "task": "Напишите комментарий 1 раз."},
        "11. Лаборатория гордится тобою.": {"reward": 9, "task": "Не получать предупреждения 2 недели 1 раз(прийти на набор/рп как минимум 4 раза)."},
        "12. Просто Хороший Бизнес.": {"reward": 10, "task": "Купите всё в магазине Себастьяна 1 раз."},
        "13. Эта ачивка отстой!": {"reward": 1, "task": "Побудьте на экс 1 раз."},
        "14. И вновь добро пожаловать!": {"reward": 2, "task": "вступите в чат постояльцев 1 раз."},
        "15. Я говорю 'владелец', вы говорите 'лучший'.": {"reward": 6, "task": "Побудьте на ивенте."},
        "16. Поисковая группа.": {"reward": 5, "task": "Сообщить о нарушении администрации."},
        "17. Деньги все решают.": {"reward": 4, "task": "Дайте ценную вещь по типу клевера или жемчуга любому из администрации."},
        "18. Горько!": {"reward": 6, "task": "Побывайте на свадьбе 1 раз."},
        "19. Псс.. может это... К нам?...": {"reward": 8, "task": "При помощи с набором пригласите более 10 участников 1 раз."},
        "20. Потрогай траву чувак.": {"reward": 10, "task": "Побывайте на рп/наборе 10 раз."},
        "21. Назад пути нету.": {"reward": 15, "task": "Получите все одноразовые ачивки."},
    },
    "СУША": {
        "22. 5 минут полет нормальный!": {"reward": 10, "task": "Обывайте во всех комнатах за 1 рп 1 раз."},
        "23. :3": {"reward": 5, "task": "Погладьте глубоводного кролика в рп 1 раз."},
        "24. Absolute cinema!": {"reward": 4, "task": "Устройте драку или конфликт в рп 1 раз."},
        "25. Уф я бы такую малышку хотел бы...": {"reward": 3, "task": "Побудьте 1 раз на подводной лодке."},
        "26. Кто ты воин?!": {"reward": 8, "task": "При случаи драки в рп, сделайте так что-бы выйти из драки без ранений 1 раз."},
    },
    "ПОД ВОДОЙ": {
        "27. Ну... это рано или поздно бы случилось?...": {"reward": 4, "task": "Утопиться/задохнуться в рп 1 раз."},
        "28. ...Эйнштейн гордится тобою.": {"reward": 6, "task": "Разведите огонь в комнате которая полностью затоплена 1 раз."},
        "29. Тяжелые вздохи через загубник.": {"reward": 8, "task": "Провести практику под водой для группы персонала (от 3-... игроков)."},
        "30. Пузыри? Давление? Азотный наркоз?": {"reward": 10, "task": "Выполните успешно все условия практики."},
    },
    "ОБЪЕКТЫ": {
        "31. А дальше что?": {"reward": 5, "task": "Сбегите от допроса 1 раз."},
        "32. Революция!": {"reward": 6, "task": "Сбегите из камеры."},
        "33. РЕВОЛЮЦИЯЯЯЯ!!!": {"reward": 10, "task": "Сбегите из лаборатории."},
        "34. А так... Можно было?": {"reward": 6, "task": "Станьте огненным объектом 1 раз."},
    },
    "ПЕРСОНАЛ": {
        "35. Таковы будни ученых.": {"reward": 3, "task": "Проведите 1 допрос."},
        "36. Таковы будни ученых, привыкай.": {"reward": 6, "task": "Проведите 3 допроса."},
        "37. Чай, кофе, администрацию?": {"reward": 2, "task": "Поролльте за персонал."},
        "38. Разновидный.": {"reward": 8, "task": "Поролльте за все разновидности персонала 1 раз."},
        "39. У нас больше нету обьектов!": {"reward": 7, "task": "Опустошите камеру обьектов (уже пустые не считаются) 1 раз."},
    },
    "СЕКРЕТКИ": {
        "40. Бан скоро.": {"reward": 20, "task": "××× ×××××××× формировке ×× ××××××, присоединитесь × ××× 1 раз."},
        "41. Бан не скоро.": {"reward": 25, "task": "×××××××× комплимент ×××××× 1 раз :)."},
        "42. Потрошитель 'Урбан'.": {"reward": 25, "task": "Убить ××××××××× ×× ×-× ×× 1 раз."},
        "43. АХ ТЫ ГНИДА!": {"reward": 15, "task": "××××××× глубоководного ××××××× 1 раз."},
        "44. Почему он, а не я!? - ОН А НЕ Я!?": {"reward": 20, "task": "Договориться × ××××× ××××××××× ×× ролку, × увидеть ××× ×× ×××××× × другим 1 раз."},
        "45. Friend-fire round №2!": {"reward": 25, "task": "Утопите/××××××× ×××××××× ××× ××××× 1 раз."},
        "46. Самый умный игрок Урбана.": {"reward": 20, "task": "Забудьте ×××××××× × нырните ××× ×××× 1 раз."},
        "47. Пацифист": {"reward": 20, "task": "Сбегите ×× ×××××××××××, ×× ××××××× × бой 1 раз."},
        "48. I was in the hell, looking at heaven.": {"reward": 25, "task": "Убейте × ××××××××× 1 раз."},
        "49. Я здесь власть!": {"reward": 25, "task": "×××××××× × допросов ××× ×××× ×× умерев 1 раз."},
        "50. Friend fire.": {"reward": 25, "task": "×× ×××××××× убить другого ××××××××× ××××× обвинить × ×××× ××××××× 1 раз."},
    }
}

# Магазин Себастьяна
SHOP_ITEMS = {
    "РОЛЛЫ": {
        "На 1 рп: +1 к роллу": 2,
        "На 1 рп: +3 к роллу": 6,
        "На 1 рп: +5 к роллу": 10,
        "На 1 рп: +7 к роллу": 14,
        "На 1 рп: +10 к роллу": 20,
        "На 2 рп: +1 к роллу": 3,
        "На 2 рп: +3 к роллу": 9,
        "На 2 рп: +5 к роллу": 15,
        "На 2 рп: +7 к роллу": 21,
        "На 2 рп: +10 к роллу": 30,
        "На 3 рп: +1 к роллу": 4,
        "На 3 рп: +3 к роллу": 12,
        "На 3 рп: +5 к роллу": 20,
        "На 3 рп: +7 к роллу": 28,
        "На 3 рп: +10 к роллу": 40,
    },
    "ПРЕДМЕТЫ": {
        "Карта 1 уровня": 50,
        "Карта 2 уровня": 65,
        "Игрушка-плюшка": 49,
        "Значок": 34,
    }
}

class Form(StatesGroup):
    waiting_for_proof = State()
    admin_add_krones = State()
    admin_remove_krones = State()

# Инициализация пользователя
def init_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "krones": 0,
            "achievements": [],
            "purchases": []
        }
    if user_id not in achievements_data:
        achievements_data[user_id] = []

# Клавиатуры
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start"), KeyboardButton(text="/send")],
            [KeyboardButton(text="/seba"), KeyboardButton(text="/krones")],
            [KeyboardButton(text="/achievements"), KeyboardButton(text="/myachievements")],
            [KeyboardButton(text="/icons")]
        ],
        resize_keyboard=True
    )

def get_achievements_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ОБЩИЙ", callback_data="ach_ОБЩИЙ")],
            [InlineKeyboardButton(text="СУША", callback_data="ach_СУША")],
            [InlineKeyboardButton(text="ПОД ВОДОЙ", callback_data="ach_ПОД ВОДОЙ")],
            [InlineKeyboardButton(text="ПЕРСОНАЛ", callback_data="ach_ПЕРСОНАЛ")],
            [InlineKeyboardButton(text="ОБЪЕКТЫ", callback_data="ach_ОБЪЕКТЫ")],
            [InlineKeyboardButton(text="ВСЕ", callback_data="ach_ВСЕ")],
            [InlineKeyboardButton(text="СЕКРЕТКИ", callback_data="ach_СЕКРЕТКИ")]
        ]
    )

def get_icons_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ОБЩИЕ", callback_data="icons_ОБЩИЙ")],
            [InlineKeyboardButton(text="СУША", callback_data="icons_СУША")],
            [InlineKeyboardButton(text="ПОД ВОДОЙ", callback_data="icons_ПОД ВОДОЙ")],
            [InlineKeyboardButton(text="ПЕРСОНАЛ", callback_data="icons_ПЕРСОНАЛ")],
            [InlineKeyboardButton(text="ОБЪЕКТЫ", callback_data="icons_ОБЪЕКТЫ")]
        ]
    )

def get_shop_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="РОЛЛЫ", callback_data="shop_РОЛЛЫ")],
            [InlineKeyboardButton(text="ПРЕДМЕТЫ", callback_data="shop_ПРЕДМЕТЫ")]
        ]
    )

def get_rolls_keyboard():
    keyboard = []
    for item, price in SHOP_ITEMS["РОЛЛЫ"].items():
        keyboard.append([InlineKeyboardButton(text=f"{item} - {price} кронов", callback_data=f"buy_{item}")])
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_shop")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_items_keyboard():
    keyboard = []
    for item, price in SHOP_ITEMS["ПРЕДМЕТЫ"].items():
        keyboard.append([InlineKeyboardButton(text=f"{item} - {price} кронов", callback_data=f"buy_{item}")])
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="back_to_shop")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_water_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="water_yes")],
            [InlineKeyboardButton(text="Нет", callback_data="water_no")]
        ]
    )

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    init_user(message.from_user.id)
    
    welcome_text = """- Здраствуйте наши дорогие постояльцы! Наша лаборатория отныне имеет такую функцию как ачивки.
🗣: Как их получать и считать?
Все просто! Есть разные разделы ачивок, они разделяются на 5 разделов: общие, на суше(объектам и персоналу), под водой, только объектам и только персоналу.
Если вы выполнили задачу ачивки, то отправьте скрин/видео с доказательствами по команде /send . Если их одобрят - вам засчитают кроны, если нет - вам отпишут что не так.
🗣: Что такое кроны?
Это наша единица валюты. За неё можно покупать разные предметы, бусты к роллу и т.д в магазине Себастьяна. Магазин Себастьяна -> /seba .
Мы будем благодарны если при использовании чего либо из магазина Себастьяна вы будете предупреждать об этом в лс администрации говоря свой юз в тг.
Список команд:
/start
/send
/seba
/krones
/achievements
/myachievements
/icons"""
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

# Команда /send
@dp.message(Command("send"))
async def cmd_send(message: types.Message, state: FSMContext):
    init_user(message.from_user.id)
    await message.answer("Отлично! Теперь отправьте скриншот/видео как доказательство ачивки и подпишите название ачивки которую вы выполняете. Ожидайте кроны в течении 24-х часов.")
    await state.set_state(Form.waiting_for_proof)

# Обработка доказательств
@dp.message(Form.waiting_for_proof)
async def process_proof(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    proof_text = message.caption or message.text or "Без описания"
    
    # Сохраняем отправку
    submission_id = f"{user_id}_{message.message_id}"
    pending_submissions[submission_id] = {
        "user_id": user_id,
        "proof_text": proof_text,
        "message_id": message.message_id
    }
    
    # Отправляем админу
    admin_text = f"Новая заявка на ачивку от пользователя {user_id}:\n\nТекст: {proof_text}\n\nДля одобрения ответьте на это сообщение текстом 'Одобрено'"
    
    try:
        if message.photo:
            sent_msg = await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text)
        elif message.video:
            sent_msg = await bot.send_video(ADMIN_ID, message.video.file_id, caption=admin_text)
        else:
            sent_msg = await bot.send_message(ADMIN_ID, f"{admin_text}\n\nДоказательство: {message.text}")
        
        pending_submissions[submission_id]["admin_message_id"] = sent_msg.message_id
        
    except Exception as e:
        await message.answer("Ошибка при отправке заявки администратору. Попробуйте позже.")
        logger.error(f"Error sending to admin: {e}")
        return
    
    await message.answer("Ваша заявка отправлена администратору. Ожидайте решения в течение 24 часов.")
    await state.clear()

# Обработка ответов админа
@dp.message(F.reply_to_message)
async def handle_admin_reply(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    reply_to = message.reply_to_message.message_id
    submission_id = None
    
    # Ищем соответствующую заявку
    for sub_id, sub_data in pending_submissions.items():
        if sub_data.get("admin_message_id") == reply_to:
            submission_id = sub_id
            break
    
    if not submission_id:
        return
    
    user_id = pending_submissions[submission_id]["user_id"]
    proof_text = pending_submissions[submission_id]["proof_text"]
    
    if message.text and message.text.lower() == "одобрено":
        # Ищем ачивку по любому совпадающему слову
        awarded_achievement = None
        awarded_krones = 0
        
        # Создаем список всех слов из доказательства
        proof_words = proof_text.lower().split()
        
        for category, achievements in ACHIEVEMENTS.items():
            for achievement_name, data in achievements.items():
                # Проверяем каждое слово в названии ачивки
                achievement_words = achievement_name.lower().replace(".", "").replace("!", "").split()
                for a_word in achievement_words:
                    if len(a_word) > 3 and a_word in proof_text.lower():  # Ищем слова длиннее 3 символов
                        awarded_achievement = achievement_name
                        awarded_krones = data["reward"]
                        break
                if awarded_achievement:
                    break
            if awarded_achievement:
                break
        
        if awarded_achievement and awarded_achievement not in achievements_data[user_id]:
            # Начисляем кроны и ачивку
            user_data[user_id]["krones"] += awarded_krones
            achievements_data[user_id].append(awarded_achievement)
            
            await bot.send_message(
                user_id, 
                f"Поздравляем! Ваша ачивка '{awarded_achievement}' одобрена! Вы получили {awarded_krones} кронов."
            )
            await message.answer(f"Ачивка одобрена! Пользователь {user_id} получил {awarded_krones} кронов.")
        else:
            await message.answer("Ачивка не найдена в доказательстве или уже получена.")
    else:
        await bot.send_message(user_id, f"Ваша заявка на ачивку отклонена. Причина: {message.text}")
        await message.answer("Пользователю отправлен отказ.")
    
    # Удаляем обработанную заявку
    if submission_id in pending_submissions:
        del pending_submissions[submission_id]

# Команда /seba
@dp.message(Command("seba"))
async def cmd_seba(message: types.Message):
    init_user(message.from_user.id)
    
    shop_text = """Приветствую тебя дорогой игрок в моем магазине. Располагайся как дома и обязательно прикупи себе что-то перед уходом."""
    
    await message.answer(shop_text, reply_markup=get_shop_keyboard())

# Обработка кнопок магазина
@dp.callback_query(F.data.startswith("shop_"))
async def process_shop_callback(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    
    if category == "РОЛЛЫ":
        rolls_text = """• РОЛЛЫ •
Бусты к роллу не суммируются!!!
→Непостоянный ролл:
На 1 рп:
+1 к роллу: 2 крона.
+3 к роллу: 6 кронов.
+5 к роллу: 10 кронов.
+7 к роллу: 14 кронов.
+10 к роллу: 20 кронов.

На 2 рп:
+1 к роллу: 3 крона.
+3 к роллу: 9 крона.
+5 к роллу: 15 кронов.
+7 к роллу: 21 крон.
+10 к роллу: 30 кронов.

На 3 рп:
+1 к роллу: 4 крона.
+3 к роллу: 12 крона.
+5 к роллу: 20 кронов.
+7 к роллу: 28 крона.
+10 к роллу: 40 крона."""
        
        await callback.message.edit_text(rolls_text, reply_markup=get_rolls_keyboard())
    
    elif category == "ПРЕДМЕТЫ":
        items_text = """• ПРЕДМЕТЫ •

Различные предметы по рп, не очень примечательные. В плане итак понятно что они будут давать, например аптечки верёвки и т.д. Их будет лимит на неделю.

• Карты доступа.

1 и 2 уровень Себастьян может продать объектам. Но будет уточнять что что-то повредилось, и вряд ли они помогут открыть двери, там уже шанс с роллом больше 60 работает на одно открытие, меньше - не сработало. Попыток: 2 раза.
Карта 1 уровня: 50 кронов.
Карта 2 уровня: 65 кронов.
Карты 3 уровня говорят не существуют...

• Игрушки-плюшки.

Игрушка самого себя с специальной пометкой лаборатории которая работает как артефакт.

Может давать способность. Работает как русская рулетка меньше 50 – будет дебафф, больше – бафф / способность, 100 / 1 – уменьшение начального ролла на 10 (НА ОДИН ЛЮБОЙ ПОСТ). Команда /roll 10-100.
Цена: 49 кронов.

• Значок.

Значок у себя самодельные. Они будут давать буст лишь на одно рп / один пост.

Работает как увлечение начальной силы. Команда – /roll (начальная цифра увеличенной начальной силы, например)10-100).
34 крона."""
        
        await callback.message.edit_text(items_text, reply_markup=get_items_keyboard())
    
    await callback.answer()

# Обработка покупок
@dp.callback_query(F.data.startswith("buy_"))
async def process_buy_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    init_user(user_id)
    
    item_name = callback.data[4:]  # Убираем "buy_"
    
    # Ищем товар и его цену
    item_price = None
    for category, items in SHOP_ITEMS.items():
        if item_name in items:
            item_price = items[item_name]
            break
    
    if item_price is None:
        await callback.answer("Товар не найден!")
        return
    
    if user_data[user_id]["krones"] >= item_price:
        # Списание кронов
        user_data[user_id]["krones"] -= item_price
        user_data[user_id]["purchases"].append(item_name)
        
        # Проверяем ачивки магазина
        if "9. Непростой Альянс." not in achievements_data[user_id]:
            achievements_data[user_id].append("9. Непростой Альянс.")
            user_data[user_id]["krones"] += 3  # Награда за ачивку
            await callback.message.answer("🎉 Вы получили ачивку 'Непростой Альянс.' и 3 крона!")
        
        # Проверяем ачивку "Просто Хороший Бизнес"
        all_purchased = all(item in user_data[user_id]["purchases"] for category in SHOP_ITEMS.values() for item in category)
        if all_purchased and "12. Просто Хороший Бизнес." not in achievements_data[user_id]:
            achievements_data[user_id].append("12. Просто Хороший Бизнес.")
            user_data[user_id]["krones"] += 10  # Награда за ачивку
            await callback.message.answer("🎉 Вы получили ачивку 'Просто Хороший Бизнес.' и 10 кронов!")
        
        await callback.message.answer(f"Спасибо за покупку! У тебя осталось {user_data[user_id]['krones']} кронов.")
        await callback.answer("Покупка успешна!")
    else:
        await callback.answer(f"Своровать удумал? ")
        # Команда /krones
@dp.message(Command("krones"))
async def cmd_krones(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id)
    
    await message.answer(f"- У вас {user_data[user_id]['krones']} кронов.")
    # Команда /achievements
@dp.message(Command("achievements"))
async def cmd_achievements(message: types.Message):
    init_user(message.from_user.id)
    
    achievements_text = "- И какой бы раздел ачивок вы бы хотели посмотреть? Обычно людишки боятся раздела с водой..."
    
    await message.answer(achievements_text, reply_markup=get_achievements_keyboard())

# Обработка кнопок ачивок
@dp.callback_query(F.data.startswith("ach_"))
async def process_achievements_callback(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    
    if category == "ВСЕ":
        response_text = "• ОБЩИЕ •\n\nЭтот раздел заключает в себе те ачивки которые можно сделать вне рп/на наборе.\n\n"
        
        response_text += "Добро пожаловать!\nЗадача: Подписаться на тгк на 1 раз.\nНаграда: 2 крона.\n\n"
        response_text += "Герои не носят плащи...\nЗадача: Помогите с набором.\nНаграда: 3 крона.\n\n"
        response_text += "С далека если смотреть, то красиво.\nЗадача: Прийдите в мерче.\nНаграда: 1 крон.\n\n"
        response_text += "Молодец возьми на полке кроны.\nЗадача: Проголосуйте за тгк проекта 1 раз.\nНаграда: 6 кронов.\n\n"
        response_text += "Да приветствует вас власть и иерархия!\nЗадача: Вступите в администрацию (как минимум побыть на наборах 3 раза).\nНаграда: 10 кронов.\n\n"
        response_text += "Да приветствует вас НЕ власть и иерархия.\nЗадача: встретить союзника лаборатории на рп/наборе.\nНаграда: 3 крона.\n\n"
        response_text += "Again and again...\nЗадача: Вступите в ност 1 раз.\nНаграда: 3 крона\n\n"
        response_text += "Да.. да.. принято! В смысле там ещё 2 лимита тг.\nЗадача: Напишите анкету в носте/чате постояльцев 1 раз.\nНаграда: 10 кронов.\n\n"
        response_text += "Непростой Альянс.\nЗадача: Купите что-то в магазине Себастьяна впервые.\nНаграда: 3 крона.\n\n"
        response_text += "Именно так лишаются девственности.\nЗадача: Напишите комментарий 1 раз.\nНаграда: 1 крон.\n\n"
        response_text += "Лаборатория гордится тобою.\nЗадача: Не получать предупреждения 2 недели 1 раз(прийти на набор/рп как минимум 4 раза).\nНаграда: 9 кронов.\n\n"
        response_text += "Просто Хороший Бизнес.\nЗадача: Купите всё в магазине Себастьяна 1 раз.\nНаграда: 10 кронов.\n\n"
        response_text += "Эта ачивка отстой!\nЗадача: Побудьте на экс 1 раз.\nНаграда: 1 крон.\n\n"
        response_text += "И вновь добро пожаловать!\nЗадача: вступите в чат постояльцев 1 раз.\nНаграда: 2 крона.\n\n"
        response_text += "Я говорю 'владелец', вы говорите 'лучший'.\nЗадача: Побудьте на ивенте.\nНаграда: 6 кронов.\n\n"
        response_text += "Поисковая группа.\nЗадача: Сообщить о нарушении администрации.\nНаграда: 5 кронов.\n\n"
        response_text += "Деньги все решают.\nЗадача: Дайте ценную вещь по типу клевера или жемчуга любому из администрации.\nНаграда: 4 крона.\n\n"
        response_text += "Горько!\nЗадача: Побывайте на свадьбе 1 раз.\nНаграда: 6 кронов.\n\n"
        response_text += "Псс.. может это... К нам?...\nЗадача: При помощи с набором пригласите более 10 участников 1 раз.\nНаграда: 8 кронов.\n\n"
        response_text += "Потрогай траву чувак.\nЗадача: Побывайте на рп/наборе 10 раз.\nНаграда: 10 кронов.\n\n"
        response_text += "Назад пути нету.\nЗадача: Получите все одноразовые ачивки.\nНаграда: 15 кронов.\n\n"

        response_text += "• НА СУШЕ(ОБЪЕКТАМ И ПЕРСОНАЛУ) •\n\n"
        response_text += "5 минут полет нормальный!\nЗадача: Побывайте во всех комнатах за 1 рп 1 раз.\nНаграда: 10 кронов.\n\n"
        response_text += ":3\nЗадача: Погладьте глубоводного кролика в рп 1 раз.\nНаграда: 5 крона.\n\n"
        response_text += "Absolute cinema!\nЗадача: Устройте драку или конфликт в рп 1 раз.\nНаграда: 4 крона.\n\n"
        response_text += "Уф я бы такую малышку хотел бы...\nЗадача: Побудьте 1 раз на подводной лодке.\nНаграда: 3 крона.\n\n"
        response_text += "Кто ты воин?!\nЗадача: При случаи драки в рп, сделайте так что-бы выйти из драки без ранений 1 раз.\nНаграда: Если без ран: 8 кронов. С ранами: 3 крона.\n\n"

        response_text += "• ПОД ВОДОЙ •\n\n"
        response_text += "Ну... это рано или поздно бы случилось?...\nЗадача: Утопиться/задохнуться в рп 1 раз.\nНаграда: 4 крона.\n\n"
        response_text += "...Эйнштейн гордится тобою.\nЗадача: Разведите огонь в комнате которая полностью затоплена 1 раз.\nНаграда: 6 кронов.\n\n"
        response_text += "Тяжелые вздохи через загубник.\nЗадача: Провести практику под водой для группы персонала (от 3-... игроков).\nНаграда: 8 кронов.\n\n"
        response_text += "Пузыри? Давление? Азотный наркоз?\nЗадача: Выполните успешно все условия практики.\nНаграда: 10 кронов.\n\n"

        response_text += "• ЧИСТО ОБЪЕКТАМ •\n\n"
        response_text += "А дальше что?\nЗадача: Сбегите от допроса 1 раз.\nНаграда: 5 крона.\n\n"
        response_text += "Революция!\nЗадача: Сбегите из камеры.\nНаграда: 6 кронов.\n\n"
        response_text += "РЕВОЛЮЦИЯЯЯЯ!!!\nЗадача: Сбегите из лаборатории.\nНаграда: 10 кронов.\n\n"
        response_text += "А так... Можно было?\nЗадача: Станьте огненным объектом 1 раз.\nНаграда: 6 кронов.\n\n"

        response_text += "• ЧИСТО ПЕРСОНАЛУ •\n\n"
        response_text += "Таковы будни ученых.\nЗадача: Проведите 1 допрос.\nНаграда: 3 крона.\n\n"
        response_text += "Таковы будни ученых, привыкай.\nЗадача: Проведите 3 допроса.\nНаграда: 6 кронов.\n\n"
        response_text += "Чай, кофе, администрацию?\nЗадача: Поролльте за персонал.\nНаграда: 2 крона.\n\n"
        response_text += "Разновидный.\nЗадача: Поролльте за все разновидности персонала 1 раз.\nНаграда: 8 кронов.\n\n"
        response_text += "У нас больше нету обьектов!\nЗадача: Опустошите камеру обьектов (уже пустые не считаются) 1 раз.\nНаграда: 7 кронов.\n"
        
        await callback.message.edit_text(response_text, reply_markup=get_achievements_keyboard())
    
    elif category == "ПОД ВОДОЙ":
        await callback.message.edit_text("вы знаете как пользоваться аквалангом?", reply_markup=get_water_keyboard())
    
    elif category == "СЕКРЕТКИ":
        response_text = "=====Секретные:\n\nВне рп:\n\n"
        response_text += "Бан скоро.\nЗадача: ××× ×××××××× формировке ×× ××××××, присоединитесь × ××× 1 раз.\nНаграда: 20 кронов.\n\n"
        response_text += "Бан не скоро.\nЗадача: ×××××××× комплимент ×××××× 1 раз :).\nНаграда: 25 кронов.\n\n"
        response_text += "Суша:\n\n"
        response_text += "Потрошитель 'Урбан'.\nЗадача: Убить ××××××××× ×× ×-× ×× 1 раз.\nНаграда: 25 кронов.\n\n"
        response_text += "АХ ТЫ ГНИДА!\nЗадача: ××××××× глубоководного ××××××× 1 раз.\nНаграда: 15 кронов.\n\n"
        response_text += "Почему он, а не я!? - ОН А НЕ Я!?\nЗадача: Договориться × ××××× ××××××××× ×× ролку, × увидеть ××× ×× ×××××× × другим 1 раз.\nНаграда: 20 кронов.\n\n"
        response_text += "Под водой:\n\n"
        response_text += "Friend-fire round №2!\nЗадача: Утопите/××××××× ×××××××× ××× ××××× 1 раз.\nНаграда: 25 кронов.\n\n"
        response_text += "Самый умный игрок Урбана.\nЗадача: Забудьте ×××××××× × нырните ××× ×××× 1 раз.\nНаграда: 20 кронов.\n\n"
        response_text += "Объектам:\n\n"
        response_text += "Пацифист\nЗадача: Сбегите ×× ×××××××××××, ×× ××××××× × бой 1 раз.\nНаграда: 20 кронов.\n\n"
        response_text += "I was in the hell, looking at heaven.\nЗадача: Убейте × ××××××××× 1 раз.\nНаграда: 25 кронов.\n\n"
        response_text += "Персоналу:\n\n"
        response_text += "Я здесь власть!\nЗадача: ×××××××× × допросов ××× ×××× ×× умерев 1 раз.\nНаграда: 25 кронов\n\n"
        response_text += "Friend fire.\nЗадача: ×× ×××××××× убить другого ××××××××× ××××× обвинить × ×××× ××××××× 1 раз.\nНаграда: 25 кронов.\n"
        
        await callback.message.edit_text(response_text, reply_markup=get_achievements_keyboard())
    
    else:
        # Для других разделов используем данные из ACHIEVEMENTS
        if category in ACHIEVEMENTS:
            response_text = f"• {category} •\n\n"
            for achievement, data in ACHIEVEMENTS[category].items():
                response_text += f"{achievement}\nЗадача: {data['task']}\nНаграда: {data['reward']} кронов.\n\n"
            
            await callback.message.edit_text(response_text, reply_markup=get_achievements_keyboard())
    
    await callback.answer()
    # Обработка кнопок под водой
@dp.callback_query(F.data.startswith("water_"))
async def process_water_callback(callback: types.CallbackQuery):
    answer = callback.data.split("_")[1]
    
    if answer == "no":
        water_instructions = """> Использование полного снаряжения (персонал).
- Выбор маски.
Маска одна из главных частей акваланга — от её выбора зависит ваш ориентир, удобство обзора и надежность воздушной прослойки.
Чтобы ее подобрать надо выполнить пару действий:
1. Выберите любую.
2. Прислоните к лицу.
3. Сделайте вдох опустив руки
4.1. - Если маска прилипла, слегка давит и не падает от простых движений это ваш вариант.
4.2. - Маска отлипла/сильно давит/падает от любых движений. Повторите все с первого пункта.

- Снаряжение баллонами.
Баллоны самая важная вещь в всем снаряжение. Без нее не было бы совсем началу подводных исследований. Выбирать баллоны уже не надо, они подготовлены изначально. Используемые баллоны отставлять в ящик под столом.
Стоит понимать использование:
1. Зафиксировать 3 лямки. Две на плечах и одну на туловище.
2. Вытянуть трубку под комфортный размер.
3.1. - Проверить поток кислорода. Если идет перейти к пункту 4.
3.2. - Проверить поток кислорода. Если он не идет проверить открыт ли регулятор и исправен ли загубник / кислородная трубка.
4. Проверить исправность датчиков: глубины, время нахождения под водой, запас сжатого воздуха (кислорода).
5. Опустится под воду. Аккуратно.

- Ласты (необязательно для подводных исследований).
Ласты это дополнительная часть в снаряжение. Одевать или нет решает дайвер при погружении. В практике работы с снаряжением  ласты используются обязательно. Важно отметить, что ласты могут встречаться встроенные в гидрокостюм. Чтобы их использовать достаточно войти в воду коснувшись вогнутой части слева. Если на персонаже одеты ласты его передвижение станет намного длительнее. Ласты немного мешают передвижению на поверхности. 
Чтобы использовать ласты много действий не надо:
1. Возьмите отогнув задние "язычки".
2. Запустите ногу в прорез.

- Гидрокостюм.
Гидрокостюм сразу носит персонаж-персонал. Ученые/охрана/медики носят гидрокостюм под формой. У дайверов он открыт, сверху те часто прикрывают кофтой/металлическим комбинезоном.

> Использование кислородной маски (ЗАКЛЮЧЁННЫЕ).
- Кислородная маска.
Данный прибор создан исключительно для заключённых. Дается чаще в исследование (заключённого отправляют в любой вольер объекта тем самым дается КМЗ для более благоприятного нахождения в комнате содержания).

Чтобы одеть надо выполнить немного действий:
1. Прижмите маску к лицу.
2. Опрокиньте лямки назад за голову отрегулировав под себя.
3. Проверьте герметичность, можно немного опустить лицо в воду, проверив.
4. Если подача воздуха слишком редкая покрутите нижний регулятор.

> Встроенный акваланг (объектам).

- Встроенные баллоны.
В частности данное снаряжение встроенной в комбинезон объекта. Работают как обычные баллоны, но без датчиков. Кислород пополняется за счет нахождения на суше/использование фильтров прямо под водой."""
        
        await callback.message.edit_text(water_instructions)
    else:
        # Если нажали "Да", показываем ачивки под водой
        response_text = "• ПОД ВОДОЙ •\n\n"
        response_text += "Ну... это рано или поздно бы случилось?...\nЗадача: Утопиться/задохнуться в рп 1 раз.\nНаграда: 4 крона.\n\n"
        response_text += "...Эйнштейн гордится тобою.\nЗадача: Разведите огонь в комнате которая полностью затоплена 1 раз.\nНаграда: 6 кронов.\n\n"
        response_text += "Тяжелые вздохи через загубник.\nЗадача: Провести практику под водой для группы персонала (от 3-... игроков).\nНаграда: 8 кронов.\n\n"
        response_text += "Пузыри? Давление? Азотный наркоз?\nЗадача: Выполните успешно все условия практики.\nНаграда: 10 кронов.\n"
        
        await callback.message.edit_text(response_text, reply_markup=get_achievements_keyboard())
    
    await callback.answer()
    # Команда /myachievements
@dp.message(Command("myachievements"))
async def cmd_myachievements(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id)
    
    user_achievements = achievements_data.get(user_id, [])
    
    if user_achievements:
        achievements_text = "Это список твоих выполненных ачивок:\n\n"
        for achievement in user_achievements:
            achievements_text += f"• {achievement}\n"
    else:
        achievements_text = "У вас пока нет выполненных ачивок. Выполните задания и отправьте доказательства через /send"
    
    await message.answer(achievements_text)
      # Команда /icons
@dp.message(Command("icons"))
async def cmd_icons(message: types.Message):
    await message.answer("- Проверьте домик постояльцев :3")
# АДМИНСКИЕ КОМАНДЫ

class Form(StatesGroup):
    waiting_for_proof = State()
    admin_add_krones = State()
    admin_remove_krones = State()

# Команда /admin
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет прав администратора.")
        return
    
    admin_text = """Админ панель:
/add_krones - начислить кроны
/remove_krones - снять кроны
/users - список пользователей"""
    await message.answer(admin_text)

# Команда /add_krones
@dp.message(Command("add_krones"))
async def cmd_add_krones(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer("Введите ID пользователя и количество крон через пробел:\nПример: 123456789 100")
    await state.set_state(Form.admin_add_krones)

# Команда /remove_krones
@dp.message(Command("remove_krones"))
async def cmd_remove_krones(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer("Введите ID пользователя и количество крон для снятия через пробел:\nПример: 123456789 50")
    await state.set_state(Form.admin_remove_krones)

# Команда /users
@dp.message(Command("users"))
async def cmd_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    if not user_data:
        await message.answer("❌ Нет зарегистрированных пользователей.")
        return
    
    users_text = "📊 Список пользователей:\n\n"
    for user_id, data in user_data.items():
        users_text += f"👤 ID: {user_id}\n💰 Кроны: {data['krones']}\n🏆 Ачивок: {len(achievements_data.get(user_id, []))}\n\n"
    
    await message.answer(users_text)

# Обработка начисления крон
@dp.message(Form.admin_add_krones)
async def process_add_krones(message: types.Message, state: FSMContext):
    try:
        user_id_str, amount_str = message.text.split()
        user_id = int(user_id_str)
        amount = int(amount_str)
        
        init_user(user_id)
        user_data[user_id]["krones"] += amount
        
        response_text = f"✅ Пользователю {user_id} начислено {amount} кронов. Теперь у него {user_data[user_id]['krones']} кронов."
        await message.answer(response_text)
        print(f"DEBUG: {response_text}")  # Для отладки
        
        # Уведомляем пользователя
        try:
            user_notification = f"🎉 Вам начислено {amount} кронов администратором! Теперь у вас {user_data[user_id]['krones']} кронов."
            await bot.send_message(user_id, user_notification)
            print(f"DEBUG: Уведомление отправлено пользователю {user_id}")
        except Exception as e:
            error_msg = f"⚠ Не удалось уведомить пользователя {user_id}: {e}"
            await message.answer(error_msg)
            print(f"DEBUG: {error_msg}")
        
    except ValueError:
        error_text = "❌ Неверный формат. Используйте: ID количество\nПример: 123456789 100"
        await message.answer(error_text)
        print(f"DEBUG: {error_text}")
    except Exception as e:
        error_text = f"❌ Ошибка: {e}"
        await message.answer(error_text)
        print(f"DEBUG: {error_text}")
    
    await state.clear()

# Обработка снятия крон
@dp.message(Form.admin_remove_krones)
async def process_remove_krones(message: types.Message, state: FSMContext):
    try:
        user_id_str, amount_str = message.text.split()
        user_id = int(user_id_str)
        amount = int(amount_str)
        
        init_user(user_id)
        
        if user_data[user_id]["krones"] >= amount:
            user_data[user_id]["krones"] -= amount
            
            response_text = f"✅ С пользователя {user_id} снято {amount} кронов. Теперь у него {user_data[user_id]['krones']} кронов."
            await message.answer(response_text)
            print(f"DEBUG: {response_text}")  # Для отладки
            
            # Уведомляем пользователя
            try:
                user_notification = f"⚠ С вас снято {amount} кронов администратором. Теперь у вас {user_data[user_id]['krones']} кронов."
                await bot.send_message(user_id, user_notification)
                print(f"DEBUG: Уведомление отправлено пользователю {user_id}")
            except Exception as e:
                error_msg = f"⚠ Не удалось уведомить пользователя {user_id}: {e}"
                await message.answer(error_msg)
                print(f"DEBUG: {error_msg}")
        else:
            error_text = f"❌ У пользователя {user_id} только {user_data[user_id]['krones']} кронов, нельзя снять {amount}."
            await message.answer(error_text)
            print(f"DEBUG: {error_text}")
        
    except ValueError:
        error_text = "❌ Неверный формат. Используйте: ID количество\nПример: 123456789 50"
        await message.answer(error_text)
        print(f"DEBUG: {error_text}")
    except Exception as e:
        error_text = f"❌ Ошибка: {e}"
        await message.answer(error_text)
        print(f"DEBUG: {error_text}")
    
    await state.clear()
        # Запуск бота для Pydroid 3
if __name__ == "__main__":
    print("Бот запускается...")
    try:
        asyncio.get_event_loop().run_until_complete(dp.start_polling(bot))
    except Exception as e:
        print(f"Ошибка: {e}")
