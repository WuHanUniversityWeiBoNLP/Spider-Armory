from peewee import *
from datetime import datetime
"""
获取转发的原始html,没有经过任何处理
"""
# db = SqliteDatabase('complete_parse_res.sqlite')
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


class Test_Recursive_Ancestor(BaseModel):
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

    is_crawl = BooleanField(null=False, verbose_name='页面是否已经爬过了')

    created_time = DateTimeField(default=datetime.now, verbose_name='创建时间')


class Test_Recursive_Descendant(BaseModel):
    """
    将所有转发得到的数据保存到另外一张表里面，用外键关联
    """
    id = BigIntegerField(null=False, primary_key=True, verbose_name='主键，由转发路径来决定')
    ancestor = ForeignKeyField(Test_Recursive_Ancestor, related_name='ancestor', verbose_name='连到有原本评论转发外键')
    repost_path = TextField(null=True, verbose_name='转发消息的层次关系:mid->mid->mid')
    depth = IntegerField(null=True, verbose_name='深度，主要是第几级')

    current_page = IntegerField(null=True, verbose_name='当前页数')
    mid_id = BigIntegerField(null=True, verbose_name='评论mid')
    repost_html = TextField(null=True, verbose_name='单条评论的raw_html')
    repost_user_id = BigIntegerField(null=True, verbose_name='评论的用户id')
    repost_user = CharField(null=True, verbose_name='评论用户名')
    repost_content = TextField(null=True, verbose_name='单条评论内容')
    repost_time = CharField(null=True, verbose_name='评论时间')
    repost_num = IntegerField(null=True, verbose_name='转发数')
    upvote_num = IntegerField(null=True, verbose_name='点赞数')

    is_crawl = BooleanField(null=False, verbose_name='页面是否已经爬过了')

    created_time = DateTimeField(default=datetime.now, verbose_name='创建时间')


if __name__ == '__main__':
    Test_Recursive_Ancestor.create_table()
    Test_Recursive_Descendant.create_table()
