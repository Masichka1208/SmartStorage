from aiogram import Router, F, html
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto, FSInputFile
from aiogram.filters import Command
from pathlib import Path
import random
import os

import config
import db_handler
import keyboards
import text
import i2c_connect

router = Router()

@router.message(Command("start"))  # /start command handler
async def start_handler(msg: Message):
    tg_id = msg.from_user.id
    raw_data = db_handler.get_user_info(tg_id)
    tg_id, rights, state = raw_data
    if tg_id == "none":
        await msg.answer(text=text.UNKNOWN_USER)
        await db_handler.set_state(msg.from_user.id, "reg")
    else:
        await msg.answer(text=text.KNOWN_USER, reply_markup=keyboards.main_menu)
        await db_handler.set_state(tg_id, "active")


@router.message()  # Message handler
async def message_handler(msg: Message):
    tg_id = msg.from_user.id
    tg_id, rights, state = db_handler.get_user_info(tg_id)
    if state == "reg": # Проверка ключа доступа
        if msg.text == config.ADMIN_PASSWORD:
            await db_handler.change_rights(tg_id, "granted")
            await db_handler.set_state(tg_id, "active")
            await msg.answer(text=text.ACES_GRANTED, reply_markup=keyboards.main_menu)
        else:
            await msg.answer(text=text.ACES_DENIED)
    elif state == "add_component" and rights == "granted": # Получение номера ячейки для добавления комплектующих
        if msg.text.isnumeric():
            await msg.answer(text=text.ADD_COMPONENT_2, reply_markup=keyboards.return_button)
            i2c_connect.pre_select(int(msg.text))
            await db_handler.set_state(msg.from_user.id, f"add_component_2__{msg.text}")
    elif "add_component_2" in state and rights == "granted": # Получение названия добавляемого комплектующего
        data = state.split("__")
        i2c_connect.select(int(data[1]))
        await (msg.answer(f"Отлично! Укажите количество '{msg.text}' и положите компоненты в выделенную ячейку. "
                          f"После ввода количества ячейка потухнет автоматически!", reply_markup=keyboards.return_button))
        await db_handler.set_state(msg.from_user.id, "add_component_3__"+data[1]+"__"+msg.text)
    elif "add_component_3" in state and rights == "granted":  # Получение количества добавляемого комплектующего
        if msg.text.isnumeric():
            await msg.answer(text=text.DATA_COLLECTED, reply_markup=keyboards.return_button)
            data = state.split("__")
            res = db_handler.add_component(int(data[1]), data[2], int(msg.text))
            i2c_connect.turn_off()
            await db_handler.set_state(msg.from_user.id, "active")
            if res:
                await msg.answer(text=text.COMPONENT_ADDED)
            else:
                await msg.answer(text=text.COMPONENT_ERROR)
            await msg.answer(text=text.MAIN_MENU, reply_markup=keyboards.main_menu)

    elif state == "active" and rights == "granted":
        await msg.answer("Начинаю поиск! Пожалуйста подождите.")
        values = db_handler.get_all_components(msg.text, msg.from_user.id)
        if values:
            s_res = ""
            for num in list(values.keys()):
                quantity, name = values.get(num)
                s_res += f"{num}. {name} ({quantity})\n"
            await msg.answer(text="Для выбора компонента напишите в следующем сообщении его номер в списке:\n"+s_res, reply_markup=keyboards.return_button)
            await db_handler.set_state(msg.from_user.id, "num_requested")
        else:
            await msg.answer("К сожалению ничего не найдено. Попробуйте снова!", reply_markup=keyboards.main_menu)

    elif state == "num_requested" and rights == "granted":
        if msg.text.isnumeric():
            data = db_handler.get_item(int(msg.text), msg.from_user.id)
            if data == "None":
                await msg.answer("К сожалению ничего не найдено. Попробуйте снова!", reply_markup=keyboards.return_button)
            else:
                num, gID, quantity, name = data
                ceil = int(gID.split("_")[0])
                i2c_connect.search_res(ceil)
                await msg.answer(f"{name} находится в ячейке, выделенной фиолетовым цветом! Укажите количество изъятого комопнента в следующем сообщении (текущее количество в ячейке {quantity}). После отправки числа ячейка погаснет автоматически.", reply_markup=keyboards.return_button)
                await db_handler.set_state(msg.from_user.id, f"loos_of_goods__{gID}")
        else:
            await msg.answer("В сообщении должно быть только число без других символов!", reply_markup=keyboards.return_button)

    elif "loos_of_goods__" in state and rights == "granted":
        if msg.text.isnumeric():
            if db_handler.update_quantity( state.split("__")[1], int(msg.text), msg.from_user.id):
                await msg.answer("Данные внесены!")
                await msg.answer(text=text.MAIN_MENU, reply_markup=keyboards.main_menu)
            else:
                await msg.answer("Данные устарели! Возвращаю в главное меню!")
                await msg.answer(text=text.MAIN_MENU, reply_markup=keyboards.main_menu)
            i2c_connect.turn_off()
            await db_handler.set_state(msg.from_user.id, "active")
        else:
            await msg.answer("В сообщении должно быть только число без других символов!", reply_markup=keyboards.return_button)




@router.callback_query(F.data == "add_component")
async def get_name(clbck: CallbackQuery):
    await clbck.message.answer(text=text.ADD_COMPONENT, reply_markup=keyboards.return_button)
    await db_handler.set_state(clbck.from_user.id, "add_component")


@router.callback_query(F.data == "return")
async def get_name(clbck: CallbackQuery):
    tg_id, rights, cur_state = db_handler.get_user_info(clbck.from_user.id)
    if rights == "granted":
        if cur_state == "add_component":
            await db_handler.set_state(clbck.from_user.id, "active")
            await clbck.message.answer(text=text.ACES_GRANTED, reply_markup=keyboards.main_menu)
        elif "add_component_2" in cur_state:
            i2c_connect.turn_off()
            await db_handler.set_state(clbck.from_user.id, "add_component")
            await clbck.message.answer(text=text.ADD_COMPONENT, reply_markup=keyboards.return_button)
        elif "add_component_3" in cur_state:
            data = cur_state.split("__")
            i2c_connect.pre_select(int(data[1]))
            await db_handler.set_state(clbck.from_user.id, f"add_component_2__{data[1]}")
            await clbck.message.answer(text=text.ADD_COMPONENT_2, reply_markup=keyboards.return_button)

        elif cur_state == "num_requested":
            db_handler.clear_search(clbck.from_user.id)
            await db_handler.set_state(clbck.from_user.id, "active")
            await clbck.message.answer(text=text.MAIN_MENU, reply_markup=keyboards.main_menu)
        elif "loos_of_goods__" in cur_state:
            i2c_connect.turn_off()
            await db_handler.set_state(clbck.from_user.id, "num_requested")


@router.callback_query(F.data == "main_menu")
async def get_name(clbck: CallbackQuery):
    db_handler.clear_search(clbck.from_user.id)
    i2c_connect.turn_off()
    await db_handler.set_state(clbck.from_user.id, "active")
    await clbck.message.answer(text=text.MAIN_MENU, reply_markup=keyboards.main_menu)


@router.callback_query(F.data == "view_cells")
async def get_name(clbck: CallbackQuery):
    pass


