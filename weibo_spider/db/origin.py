from peewee import *
from datetime import datetime
"""
获取转发的原始html,没有经过任何处理
"""
# db = SqliteDatabase('original_weibo_repost.sqlite')
mysql_db = MySQLDatabase('wuhan',
                          user='root',
                          password='',
                          host='localhost',
                          charset='utf8mb4')
mysql_db.connect()


class BaseModel(Model):
    class Meta:
        database = mysql_db
        # database = db


class Origin_Weibo(BaseModel):
    id = IntegerField(null=False, primary_key=True, verbose_name='主键')
    current_page = IntegerField(null=True, verbose_name='当前页数')
    raw_html = TextField(null=True, verbose_name='未经处理的raw_html')

    created_time = DateTimeField(default=datetime.now, verbose_name='创建时间')


if __name__ == '__main__':
    Origin_Weibo.create_table()
