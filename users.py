import logging
import threading
from datetime import datetime
from typing import List, Optional

import gspread

lock = threading.Lock()


class User:
    def __init__(self,
                 chat_id: gspread.Cell,
                 first_name: gspread.Cell,
                 token: gspread.Cell,
                 label: gspread.Cell,
                 amount: gspread.Cell,
                 last_sync: gspread.Cell):
        self.chat_id: gspread.Cell = chat_id
        self.first_name: gspread.Cell = first_name
        self.token: gspread.Cell = token
        self.label: gspread.Cell = label
        self.amount: gspread.Cell = amount
        self.last_sync: gspread.Cell = last_sync

    def __str__(self):
        return f'({self.last_sync}, {self.chat_id}, {self.token}, {self.label})'

    def get_last_sync(self) -> datetime:
        if self.last_sync is not None and self.last_sync.value != '':
            return datetime.strptime(self.last_sync.value, '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.utcnow().replace(microsecond=0)

    def is_first_sync(self) -> bool:
        return self.last_sync is None or self.last_sync.value == ''


class UserDatabase:
    def __init__(self, spreadsheet_id: str, gcp_credentials: str = None):
        self.gc = gspread.service_account(filename=gcp_credentials)
        self.wks = self.gc.open_by_key(spreadsheet_id).sheet1

    def get_users(self) -> list[User]:
        result = []
        # Iterate to get all records of each row and create a Record object
        for i in range(1, self.wks.row_count):
            row: List[gspread.Cell] = self.wks.range(i, 1, i, 7)
            if row is None:
                logging.error(f'Invalid row: {row}')
                continue
            if len(row) == 0 or row[0].value is None or row[0].value == '':
                break
            result.append(
                User(chat_id=row[2], first_name=row[1], token=row[3], label=row[4], amount=row[5], last_sync=row[6]))

        return result

    def get_user(self, user_id) -> Optional[User]:
        for user in self.get_users():
            if user.chat_id.value == user_id:
                return user
        return None

    def delete_user(self, chat_id) -> bool:
        user = self.get_user(chat_id)
        if user is not None:
            with lock:
                self.wks.delete_rows(user.chat_id.row)
                return True
        return False

    def save_user(self, chat_id: str, first_name: str, token: str, label: str, amount: int = 0,
                  last_sync: datetime = datetime.utcnow().replace(microsecond=0)):
        with lock:
            row = self._next_available_row()
            self.wks.update(values=[
                [datetime.utcnow().isoformat(),
                 first_name,
                 chat_id,
                 token,
                 label,
                 amount,
                 last_sync.isoformat()]],
                range_name=f'A{row}', value_input_option='USER_ENTERED')

    def _next_available_row(self):
        str_list = list(filter(None, self.wks.col_values(1)))
        return str(len(str_list) + 1)
