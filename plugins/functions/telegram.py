# SCP-079-CAPTCHA - Provide challenges for new joined members
# Copyright (C) 2019-2020 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-CAPTCHA.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from typing import Generator, Iterable, List, Optional, Union

from pyrogram import Chat, ChatMember, ChatPermissions, ChatPreview, Client
from pyrogram import InputMediaPhoto, InlineKeyboardMarkup, Message
from pyrogram.api.types import InputPeerUser, InputPeerChannel
from pyrogram.errors import ChatAdminRequired, ButtonDataInvalid, ChannelInvalid, ChannelPrivate, FloodWait
from pyrogram.errors import MessageDeleteForbidden, PeerIdInvalid, QueryIdInvalid
from pyrogram.errors import UsernameInvalid, UsernameNotOccupied, UserNotParticipant

from .. import glovar
from .etc import delay, get_int, wait_flood

# Enable logging
logger = logging.getLogger(__name__)


def answer_callback(client: Client, callback_query_id: str, text: str, show_alert: bool = False) -> Optional[bool]:
    # Answer the callback
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.answer_callback_query(
                    callback_query_id=callback_query_id,
                    text=text,
                    show_alert=show_alert
                )
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except QueryIdInvalid:
                return False
    except Exception as e:
        logger.warning(f"Answer query to {callback_query_id} error: {e}", exc_info=True)

    return result


def delete_messages(client: Client, cid: int, mids: Iterable[int]) -> Optional[bool]:
    # Delete some messages
    result = None
    try:
        mids = list(mids)
        mids_list = [mids[i:i + 100] for i in range(0, len(mids), 100)]

        for mids in mids_list:
            try:
                flood_wait = True
                while flood_wait:
                    flood_wait = False
                    try:
                        result = client.delete_messages(chat_id=cid, message_ids=mids)
                    except FloodWait as e:
                        flood_wait = True
                        wait_flood(e)
            except MessageDeleteForbidden:
                return False
            except Exception as e:
                logger.warning(f"Delete message {mids} in {cid} for loop error: {e}", exc_info=True)
    except Exception as e:
        logger.warning(f"Delete messages in {cid} error: {e}", exc_info=True)

    return result


def download_media(client: Client, file_id: str, file_ref: str, file_path: str) -> Optional[str]:
    # Download a media file
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.download_media(message=file_id, file_ref=file_ref, file_name=file_path)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
    except Exception as e:
        logger.warning(f"Download media {file_id} to {file_path} error: {e}", exc_info=True)

    return result


def edit_message_photo(client: Client, cid: int, mid: int, photo: str, file_ref: str = None, caption: str = "",
                       markup: InlineKeyboardMarkup = None) -> Union[bool, Message, None]:
    # Edit the message's photo
    result = None
    try:
        media = InputMediaPhoto(
            media=photo,
            file_ref=file_ref,
            caption=caption,
            parse_mode="html"
        )

        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.edit_message_media(
                    chat_id=cid,
                    message_id=mid,
                    media=media,
                    reply_markup=markup
                )
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except ButtonDataInvalid:
                logger.warning(f"Edit message {mid} photo {photo} in {cid} - invalid markup: {markup}")
            except (ChatAdminRequired, PeerIdInvalid, ChannelInvalid, ChannelPrivate):
                return False
    except Exception as e:
        logger.warning(f"Edit message photo error: {e}", exc_info=True)

    return result


def edit_message_text(client: Client, cid: int, mid: int, text: str,
                      markup: InlineKeyboardMarkup = None) -> Union[bool, Message, None]:
    # Edit the message's text
    result = None
    try:
        if not text.strip():
            return None

        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.edit_message_text(
                    chat_id=cid,
                    message_id=mid,
                    text=text,
                    parse_mode="html",
                    disable_web_page_preview=True,
                    reply_markup=markup
                )
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except ButtonDataInvalid:
                logger.warning(f"Edit message {mid} text in {cid} - invalid markup: {markup}")
            except (ChatAdminRequired, PeerIdInvalid, ChannelInvalid, ChannelPrivate):
                return False
    except Exception as e:
        logger.warning(f"Edit message {mid} in {cid} error: {e}", exc_info=True)

    return result


def export_chat_invite_link(client: Client, cid: int) -> Union[bool, str, None]:
    # Generate a new link for a chat
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.export_chat_invite_link(chat_id=cid)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except (ChatAdminRequired, PeerIdInvalid, ChannelInvalid, ChannelPrivate):
                return ""
    except Exception as e:
        logger.warning(f"Export chat invite link in {cid} error: {e}", exc_info=True)

    return result


def get_admins(client: Client, cid: int) -> Optional[Union[bool, List[ChatMember]]]:
    # Get a group's admins
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.get_chat_members(chat_id=cid, filter="administrators")
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except (PeerIdInvalid, ChannelInvalid, ChannelPrivate):
                return False
    except Exception as e:
        logger.warning(f"Get admins in {cid} error: {e}", exc_info=True)

    return result


def get_chat(client: Client, cid: Union[int, str]) -> Union[Chat, ChatPreview, None]:
    # Get a chat
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.get_chat(chat_id=cid)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except (PeerIdInvalid, ChannelInvalid, ChannelPrivate):
                return None
    except Exception as e:
        logger.warning(f"Get chat {cid} error: {e}", exc_info=True)

    return result


def get_chat_member(client: Client, cid: int, uid: int) -> Union[bool, ChatMember, None]:
    # Get information about one member of a chat
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.get_chat_member(chat_id=cid, user_id=uid)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except UserNotParticipant:
                result = False
    except Exception as e:
        logger.warning(f"Get chat member {uid} in {cid} error: {e}", exc_info=True)

    return result


def get_group_info(client: Client, chat: Union[int, Chat], cache: bool = True) -> (str, str):
    # Get a group's name and link
    group_name = "Unknown Group"
    group_link = glovar.default_group_link
    try:
        if isinstance(chat, int):
            the_cache = glovar.chats.get(chat)

            if the_cache:
                chat = the_cache
            else:
                result = get_chat(client, chat)

                if cache and result:
                    glovar.chats[chat] = result

                chat = result

        if not chat:
            return group_name, group_link

        if chat.title:
            group_name = chat.title

        if chat.username:
            group_link = "https://t.me/" + chat.username
    except Exception as e:
        logger.info(f"Get group {chat} info error: {e}", exc_info=True)

    return group_name, group_link


def get_members(client: Client, cid: int, query: str = "all") -> Optional[Generator[ChatMember, None, None]]:
    # Get a members generator of a chat
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.iter_chat_members(chat_id=cid, filter=query)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
    except Exception as e:
        logger.warning(f"Get members in {cid} error: {e}", exc_info=True)

    return result


def get_messages(client: Client, cid: int, mids: Iterable[int]) -> Optional[List[Message]]:
    # Get some messages
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.get_messages(chat_id=cid, message_ids=mids)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
    except Exception as e:
        logger.warning(f"Get messages {mids} in {cid} error: {e}", exc_info=True)

    return result


def kick_chat_member(client: Client, cid: int, uid: Union[int, str]) -> Union[bool, Message, None]:
    # Kick a chat member in a group
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.kick_chat_member(chat_id=cid, user_id=uid)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
    except Exception as e:
        logger.warning(f"Kick chat member {uid} in {cid} error: {e}", exc_info=True)

    return result


def leave_chat(client: Client, cid: int, delete: bool = False) -> bool:
    # Leave a channel
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                client.leave_chat(chat_id=cid, delete=delete)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except (PeerIdInvalid, ChannelInvalid, ChannelPrivate):
                return False

        return True
    except Exception as e:
        logger.warning(f"Leave chat {cid} error: {e}", exc_info=True)

    return False


def resolve_peer(client: Client, pid: Union[int, str]) -> Union[bool, InputPeerChannel, InputPeerUser, None]:
    # Get an input peer by id
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.resolve_peer(pid)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except (PeerIdInvalid, UsernameInvalid, UsernameNotOccupied):
                return False
    except Exception as e:
        logger.warning(f"Resolve peer {pid} error: {e}", exc_info=True)

    return result


def resolve_username(client: Client, username: str, cache: bool = True) -> (str, int):
    # Resolve peer by username
    peer_type = ""
    peer_id = 0
    try:
        username = username.strip("@")

        if not username:
            return "", 0

        result = glovar.usernames.get(username)

        if result and cache:
            return result["peer_type"], result["peer_id"]

        result = resolve_peer(client, username)

        if result:
            if isinstance(result, InputPeerChannel):
                peer_type = "channel"
                peer_id = result.channel_id
                peer_id = get_int(f"-100{peer_id}")
            elif isinstance(result, InputPeerUser):
                peer_type = "user"
                peer_id = result.user_id

        glovar.usernames[username] = {
            "peer_type": peer_type,
            "peer_id": peer_id
        }
    except Exception as e:
        logger.warning(f"Resolve username {username} error: {e}", exc_info=True)

    return peer_type, peer_id


def restrict_chat_member(client: Client, cid: int, uid: int, permissions: ChatPermissions,
                         until_date: int = 0) -> Optional[Chat]:
    # Restrict a user in a supergroup
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.restrict_chat_member(
                    chat_id=cid,
                    user_id=uid,
                    permissions=permissions,
                    until_date=until_date
                )
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
    except Exception as e:
        logger.warning(f"Restrict chat member {uid} in {cid} error: {e}", exc_info=True)

    return result


def send_document(client: Client, cid: int, document: str, file_ref: str = None, caption: str = "", mid: int = None,
                  markup: InlineKeyboardMarkup = None) -> Union[bool, Message, None]:
    # Send a document to a chat
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.send_document(
                    chat_id=cid,
                    document=document,
                    file_ref=file_ref,
                    caption=caption,
                    parse_mode="html",
                    reply_to_message_id=mid,
                    reply_markup=markup
                )
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except ButtonDataInvalid:
                logger.warning(f"Send document {document} to {cid} - invalid markup: {markup}")
            except (ChatAdminRequired, PeerIdInvalid, ChannelInvalid, ChannelPrivate):
                return False
    except Exception as e:
        logger.warning(f"Send document {document} to {cid} error: {e}", exec_info=True)

    return result


def send_message(client: Client, cid: int, text: str, mid: int = None,
                 markup: InlineKeyboardMarkup = None) -> Union[bool, Message, None]:
    # Send a message to a chat
    result = None
    try:
        if not text.strip():
            return None

        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.send_message(
                    chat_id=cid,
                    text=text,
                    parse_mode="html",
                    disable_web_page_preview=True,
                    reply_to_message_id=mid,
                    reply_markup=markup
                )
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except ButtonDataInvalid:
                logger.warning(f"Send message to {cid} - invalid markup: {markup}")
            except (ChatAdminRequired, PeerIdInvalid, ChannelInvalid, ChannelPrivate):
                return False
    except Exception as e:
        logger.warning(f"Send message to {cid} error: {e}", exc_info=True)

    return result


def send_photo(client: Client, cid: int, photo: str, file_ref: str = None, caption: str = "", mid: int = None,
               markup: InlineKeyboardMarkup = None) -> Union[bool, Message, None]:
    # Send a photo to a chat
    result = None
    try:
        if not photo.strip():
            return None

        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.send_photo(
                    chat_id=cid,
                    photo=photo,
                    file_ref=file_ref,
                    caption=caption,
                    parse_mode="html",
                    reply_to_message_id=mid,
                    reply_markup=markup
                )
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except ButtonDataInvalid:
                logger.warning(f"Send photo {photo} to {cid} - invalid markup: {markup}")
            except (ChatAdminRequired, PeerIdInvalid, ChannelInvalid, ChannelPrivate):
                return False
    except Exception as e:
        logger.warning(f"Send photo {photo} to {cid} error: {e}", exc_info=True)

    return result


def send_report_message(secs: int, client: Client, cid: int, text: str, mid: int = None,
                        markup: InlineKeyboardMarkup = None) -> Optional[Message]:
    # Send a message that will be auto deleted to a chat
    result = None
    try:
        if not text.strip():
            return None

        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.send_message(
                    chat_id=cid,
                    text=text,
                    parse_mode="html",
                    disable_web_page_preview=True,
                    reply_to_message_id=mid,
                    reply_markup=markup
                )
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except ButtonDataInvalid:
                logger.warning(f"Send report message to {cid} - invalid markup: {markup}")

        if not result:
            return None

        mid = result.message_id
        mids = [mid]
        delay(secs, delete_messages, [client, cid, mids])
    except Exception as e:
        logger.warning(f"Send report message to {cid} error: {e}", exc_info=True)

    return result


def unban_chat_member(client: Client, cid: int, uid: Union[int, str]) -> Optional[bool]:
    # Unban a user in a group
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.unban_chat_member(chat_id=cid, user_id=uid)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
    except Exception as e:
        logger.warning(f"Unban chat member {uid} in {cid} error: {e}", exc_info=True)

    return result
