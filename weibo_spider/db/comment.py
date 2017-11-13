from peewee import *
from datetime import datetime


mysql_db = MySQLDatabase('wuhan',
                          user='root',
                          password='',
                          host='localhost',
                          charset='utf8mb4')
mysql_db.connect()


class BaseModel(Model):
    class Meta:
        database = mysql_db


class Comment(BaseModel):
    id = BigIntegerField(null=False, primary_key=True, verbose_name='主键')
    current_page = CharField(null=True, verbose_name='当前页数')
    raw_html = TextField(null=True, verbose_name='评论所属的原始html')
    comment_id = CharField(null=True, verbose_name='评论id')
    user_id = CharField(null=True, verbose_name='用户id')
    comment_content = TextField(null=True, verbose_name='评论内容')
    comment_time = CharField(null=True, verbose_name='评论时间')
    up_vote_num = CharField(null=True, verbose_name='点赞数')

    created_time = DateTimeField(default=datetime.now, verbose_name='创建时间')


if __name__ == '__main__':
    Comment.create_table()

