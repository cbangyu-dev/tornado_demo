#!/usr/bin/python3.5
# author == 'caibangyu'

import logging
import mysql.connector as sql
import json

import tornado.web
import tornado.gen


mysql_config = {}


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self):
        self._logger = logging.getLogger(__name__)
        self._mysql_config = mysql_config
        self._sql_cnx = sql.connect(**self._mysql_config)


class UserHandler(BaseHandler):
    _table = "users"
    _common_columns = ["id", "name", "email", "location", "about_me"]
    _detail_columns = ["id", "name", "email", "location", "about_me", "role_id", "confirmed", "member_since", "last_seen"]
    _fields_open_for_modification = ["name", "email", "location", "about_me"]
    _post_open_fields_base = ["role_id", "name", "username", "password_hash"]

    @tornado.gen.coroutine
    def get(self, user_id):
        self._logger.info("user_id: %s", user_id)
        columns = []
        if "detail" in self.request.arguments:
            if self.get_argument("detail") == "true":
                columns = self._detail_columns
        else:
            columns = self._common_columns
        operation = "SELECT {columns} FROM {table} WHERE id={user_id}".format(
            columns=",".join(columns),
            table=self._table,
            user_id=user_id,
        )
        try:
            cursor = self._sql_cnx.cursor(buffered=True)
            cursor.execute(operation)
            user = [dict(zip(columns, row)) for row in cursor]
            result = {'data': user}
            self.set_status(200)
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.write(json.dumps(result))
        except Exception as e:
            self.set_status(400)
            self._logger.info(e)
            self.set_header('message', str(e))

    @tornado.gen.coroutine
    def post(self):
        columns = []
        values = []
        formats = []
        data = json.loads(self.request.body.decode())
        for k, v in data.items():
            if k in self._post_open_fields_base:
                columns.append(k)
                values.append(v)
                formats.append("%s")
        if columns != self._post_open_fields_base:
            self._logger.info("Can not regist a user with data: %s", data)
            self.set_status(400)
            self.set_header("message", "Can not regist a user with post data")
        else:
            operation = "INSERT {table} ({keys}) values ({values})".format(
                table=self._table,
                keys=",".join(columns),
                values=",".join(formats)
            )
            try:
                self._logger.info("sql: %s", operation)
                cursor = self._sql_cnx.cursor(buffered=True)
                cursor.execute(operation, values)
                self._sql_cnx.commit()
                result = {"data": "Create OK"}
                self.set_status(200)
                self.set_header("Content-Type", "application/json; charset=UTF-8")
                self.write(json.dumps(result))
            except Exception as e:
                self.set_status(400)
                self._logger.info(e)
                self.set_header('message', str(e))

    @tornado.gen.coroutine
    def put(self, user_id):
        data = json.loads(self.request.body.decode())
        self._logger.info('Try to update user info: %s.', data)
        modify_columns = []
        modify_values = []
        for k, v in data.items():
            if k in self._fields_open_for_modification:
                modify_columns.append(k)
                modify_values.append(v)
        if len(modify_columns) == 0:
            self.set_status(400)
            self.set_header("message", "fields not open for modify")
        else:
            operation = "UPDATE {table} SET {keyvalue} WHERE id={user_id}".format(
                table=self._table,
                keyvalue=",".join([u"{}=%s".format(modify_columns[i]) for i in range(len(modify_columns))]),
                user_id=user_id,
            )
            self._logger.info("Update operation: %s", operation)
            try:
                cursor = self._sql_cnx.cursor(buffered=True)
                cursor.execute(operation, modify_values)
                self._sql_cnx.commit()

                result = {'data': "Update OK"}
                self.set_status(200)
                self.set_header("Content-Type", "application/json; charset=UTF-8")
                self.write(json.dumps(result))
            except Exception as e:
                self.set_status(400)
                self._logger.info(e)
                self.set_header('message', str(e))

    @tornado.gen.coroutine
    def delete(self, user_id):
        operation = "DELET FROM {table} WHERE id={user_id}".format(
            table=self._table,
            user_id=user_id,
        )
        try:
            cursor = self._sql_cnx.cursor(buffered=True)
            cursor.execute(operation)
            self._sql_cnx.commit()
        except Exception as e:
            self.set_status(400)
            self._logger.info(e)
            self.set_header('message', str(e))
