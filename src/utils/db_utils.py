#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import os
import sqlite3


def get_conn(path):
    """获取到数据库的连接对象，参数为数据库文件的绝对路径
    如果传递的参数是存在，并且是文件，那么就返回硬盘上面改
    路径下的数据库文件的连接对象；否则，返回内存中的数据接
    连接对象"""
    conn = sqlite3.connect(path)
    if os.path.exists(path) and os.path.isfile(path):
        return conn
    else:
        conn = None
        return sqlite3.connect(':memory:')


def get_cursor(conn):
    """该方法是获取数据库的游标对象，参数为数据库的连接对象
    如果数据库的连接对象不为None，则返回数据库连接对象所创
    建的游标对象；否则返回一个游标对象，该对象是内存中数据
    库连接对象所创建的游标对象"""
    if conn is not None:
        return conn.cursor()
    else:
        return get_conn('').cursor()


###############################################################
####            创建|删除表操作     START
###############################################################
def drop_table(conn, table):
    """如果表存在,则删除表，如果表中存在数据的时候，使用该方法的时候要慎用！"""
    if table is not None and table != '':
        sql = 'DROP TABLE IF EXISTS ' + table
        print('drop_table ' + sql)
        cu = get_cursor(conn)
        cu.execute(sql)
        conn.commit()
        close_all(conn, cu)
    else:
        print('drop_table：the sql error!')


def create_table(conn, sql):
    """创建数据库表"""
    if sql is not None and sql != '':
        cu = get_cursor(conn)
        print('create_table ' + sql)
        cu.execute(sql)
        conn.commit()
        close_all(conn, cu)
    else:
        print('create_table: the sql error!')


###############################################################
####            创建|删除表操作     END
###############################################################

def close_all(conn, cu):
    """关闭数据库游标对象和数据库连接对象"""
    try:
        if cu is not None:
            cu.close()
    finally:
        if cu is not None:
            cu.close()


###############################################################
####            数据库操作CRUD     START
###############################################################

def save(conn, sql, data):
    """插入数据"""
    if sql is not None and sql != '':
        if data is not None:
            cu = get_cursor(conn)
            for d in data:
                print('save: sql:[{}],data:[{}]'.format(sql, d))
                cu.execute(sql, d)
                conn.commit()
            close_all(conn, cu)
    else:
        print('save: the sql error!')


def fetchall(conn, sql):
    """查询所有数据"""
    if sql is not None and sql != '':
        cu = get_cursor(conn)
        print('fetchall : sql:[{}]'.format(sql))
        cu.execute(sql)
        r = cu.fetchall()
        if len(r) > 0:
            for e in range(len(r)):
                print(r[e])
    else:
        print('fetchall: the sql error!')


def fetchone(conn, sql, data):
    '''查询一条数据'''
    if sql is not None and sql != '':
        if data is not None:
            # Do this instead
            d = (data,)
            cu = get_cursor(conn)
            print('fetchone：sql:[{}],data:[{}]'.format(sql, data))
            cu.execute(sql, d)
            r = cu.fetchall()
            if len(r) > 0:
                for e in range(len(r)):
                    print(r[e])
        else:
            print('fetchone：the data equal None!')
    else:
        print('fetchone：the sql error!')


def update(conn, sql, data):
    """更新数据"""
    if sql is not None and sql != '':
        if data is not None:
            cu = get_cursor(conn)
            for d in data:
                print('update:执行sql:[{}],参数:[{}]'.format(sql, d))
                cu.execute(sql, d)
                conn.commit()
            close_all(conn, cu)
    else:
        print('update:the sql error!')


def delete(conn, sql, data):
    """删除数据"""
    if sql is not None and sql != '':
        if data is not None:
            cu = get_cursor(conn)
            for d in data:
                print('delete: 执行sql:[{}],参数:[{}]'.format(sql, d))
                cu.execute(sql, d)
                conn.commit()
            close_all(conn, cu)
    else:
        print('delete: the sql error!')
###############################################################
