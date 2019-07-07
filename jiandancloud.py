import os
import click
from flask_migrate import Migrate, upgrade
from app import create_app, db
from app.models import User, Follow, Role, Permission, Post, Comment, Uploadfile

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Follow=Follow, Role=Role,
                Permission=Permission, Post=Post, Comment=Comment,
                Uploadfile=Uploadfile)


@app.cli.command()
@click.option('--drop', is_flag=True, help='数据库创建、修改、删除')
@click.password_option()
def initdb(drop, password):
    '''初始化数据库'''
    if drop:
        click.confirm('这会删除数据库，你确定吗？')
        db.drop_all()
        click.echo('删除成功。')
    db.create_all()

    # 创建或更新用户角色
    Role.insert_roles()
    click.echo('初始化数据库成功。')

    from datetime import datetime
    # 添加管理员账号
    admin = User(email=app.config['JIANDANCLOUD_ADMIN'],
                 username='Admin',
                 password=password,
                 confirmed=True,
                 name='管理员',
                 location='中国',
                 about_me='我是简单云管理员')
    db.session.add(admin)
    db.session.commit()
    User.add_self_follows()
    click.echo('添加管理员完成。')


@app.cli.command()
def deploy():
    '''运行部署任务'''
    # 把数据库迁移到最新修订版本
    upgrade()

    # 创建或更新用户角色
    Role.insert_roles()

    # 确保所有用户都关注了自己
    User.add_self_follows()


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
@click.option('--count', default=100, help='随机生成虚拟用户及文章，默认=100.')
def forge(count):
    """随机生成虚拟用户及文章."""
    from random import randint
    from sqlalchemy.exc import IntegrityError
    from faker import Faker
    fake = Faker('zh-CN')
    click.echo('准备生成随机虚拟数据...')
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
            User.add_self_follows()
        except IntegrityError:
            db.session.rollback()
    click.echo('创建 %d 个用户完毕.' % count)

    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(),
                 timestamp=fake.past_date(),
                 author=u)
        db.session.add(p)
    db.session.commit()
    click.echo('创建 %d 条信息完毕.' % count)
