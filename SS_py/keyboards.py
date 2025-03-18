from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

main_menu = [
    [InlineKeyboardButton(text="Добавить компонент", callback_data="add_component")],
    [InlineKeyboardButton(text="Просмотр ячеек", callback_data="view_cells")]
]
main_menu = InlineKeyboardMarkup(inline_keyboard=main_menu)

return_button = [
    [InlineKeyboardButton(text="Вернуться назад", callback_data="return")],
    [InlineKeyboardButton(text="Главное меню", callback_data="main_menu")]
]
return_button = InlineKeyboardMarkup(inline_keyboard=return_button)

