from peewee import *
from datetime import datetime
"""
获取转发的原始html,没有经过任何处理
"""
# db = SqliteDatabase('basic_parse_res.sqlite')
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


class Basic_Weibo(BaseModel):
    id = BigIntegerField(null=False, primary_key=True, verbose_name='主键')
    current_page = IntegerField(null=True, verbose_name='当前页数')
    mid_id = BigIntegerField(null=True, verbose_name='评论mid')
    repost_html = TextField(null=True, verbose_name='单条评论的raw_html')
    repost_user_id = BigIntegerField(null=True, verbose_name='评论的用户id')
    repost_user = CharField(null=True, verbose_name='评论用户名')
    repost_content = TextField(null=True, verbose_name='单条评论内容')
    repost_time = CharField(null=True, verbose_name='评论时间')
    repost_num = IntegerField(null=True, verbose_name='转发数')
    upvote_num = IntegerField(null=True, verbose_name='点赞数')

    created_time = DateTimeField(default=datetime.now, verbose_name='创建时间')


if __name__ == '__main__':
    Basic_Weibo.create_table()
