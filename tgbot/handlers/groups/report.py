# import asyncio
# import time
#
# from aiogram import types, exceptions, Dispatcher
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Command
# from aiogram.utils.markdown import hlink
# from loguru import logger
#
# from filters import IsGroup, IsReplyFilter
# from keyboards.inline.admin import report_reactions_keyboard, report_cb
# from loader import db
#
# report_command = Command("report", prefixes={"/", "!"})
#
#
# async def report_user(message: types.Message, state: FSMContext):
#     """Отправляет жалобу на пользователя админам"""
#
#     reply = message.reply_to_message
#
#     # Если юзер репортит на сообщение из канала, то пропускаем это
#     if reply.is_automatic_forward is True:
#         await message.delete()
#         return
#
#     # Проверка на то что реплай сообщение написано от имени канала
#     if reply.sender_chat:
#         mention = reply.sender_chat.title
#     else:
#         mention = reply.from_user.get_mention()
#
#     chat_id = message.chat.id
#
#     await message.answer(
#         f"Репорт на пользователя {mention} успешно отправлен.\n"
#         "Администрация предпримет все необходимые меры"
#     )
#
#     chat_admins = db.select_all_chat_admins(chat_id)
#
#     if not chat_admins:
#         # На всякий случай что бы не было спама
#         data = await state.storage.get_data(chat=chat_id)
#         if data.get('last_get_admins_time', 0) < time.time():
#             await state.storage.update_data(
#                 chat=chat_id,
#                 data={'last_get_admins_time': time.time() + 3600}
#             )
#
#             admins = await message.bot.get_chat_administrators(chat_id)
#             for admin in admins:
#                 if admin.user.is_bot is False:
#                     db.add_chat_admin(chat_id, admin.user.id)
#
#             chat_admins = db.select_all_chat_admins(chat_id)
#     chat_admins = {admin[0] for admin in chat_admins}
#     logger.info(f"Администраторам группы отправлено сообщение-жалоба {chat_id}: {chat_admins}")
#
#     for admin in chat_admins:
#         admin_id = admin
#         try:
#             await message.bot.send_message(
#                 chat_id=admin_id,
#                 text=f"Кинут репорт на пользователя {mention} "
#                      "за следующее " + hlink("сообщение", message.reply_to_message.url),
#                 reply_markup=report_reactions_keyboard(
#                     message.reply_to_message.from_user.id,
#                     message.reply_to_message.chat.id,
#                     message.reply_to_message.message_id)
#             )
#             await asyncio.sleep(0.05)
#         except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.CantTalkWithBots,
#                 exceptions.CantInitiateConversation):
#             db.del_chat_admin(chat_id, admin_id)
#         except Exception as err:
#             logger.exception("Не предвиденное исключение при рассылке сообщений админам чата при отправке репорта.")
#             logger.exception(err)
#
#
# async def report_user_if_command_is_not_reply(message: types.Message):
#     """Уведомляет, что репорт должен быть ответом"""
#     await message.reply(
#         "Сообщение с командой должно быть ответом на сообщение пользователя, "
#         "на которого вы хотите пожаловаться"
#     )
#
#
# async def report_user_callback(call: types.CallbackQuery, callback_data: dict):
#     action = callback_data.get('action')
#     message_id = callback_data.get('message_id')
#     user_id = callback_data.get('user_id')
#     chat_id = callback_data.get('chat_id')
#     try:
#         if action == 'ban':
#             await call.bot.kick_chat_member(
#                 chat_id, user_id, revoke_messages=False
#             )
#             await call.bot.delete_message(chat_id, message_id)
#         elif action == 'ban_delete':
#             await call.bot.kick_chat_member(
#                 chat_id, user_id, revoke_messages=True
#             )
#         elif action == 'delete':
#             await call.bot.delete_message(chat_id, message_id)
#     except Exception as e:
#         logger.exception(e)
#     finally:
#         await call.message.delete_reply_markup()
#
#
# def register_report_handlers(dp: Dispatcher):
#     dp.register_message_handler(
#         report_user,
#         IsGroup(), IsReplyFilter(True), report_command
#     )
#     dp.register_message_handler(report_user_if_command_is_not_reply,
#                                 IsGroup(), report_command)
#     dp.register_callback_query_handler(report_user_callback, report_cb.filter())
