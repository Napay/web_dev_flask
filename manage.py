import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
	import coverage
	COV = coverage.coverage(branch=True, include='app/*')
	COV.start()

import sys
import click
from app import create_app, db
from app.models import User, Role, Post, Permission, Follow, Comment
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)


@app.shell_context_processor
def make_shell_context():
	return dict(db=db, User=User, Role=Role, Permission=Permission, Post=Post, Follow=Follow, Comment=Comment)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


# @app.cli.command()
# @click.argument('test_names', nargs=-1)
# def test(test_names):
# 	'''Run the unit tests.'''
# 	import unittest
# 	if test_names:
# 		tests = unittest.TestLoader().loadTestsFromNames(test_names)
# 	else:
# 		tests = unittest.TestLoader().discover('tests')
# 	unittest.TextTestRunner(verbosity=2).run(tests)

# @manager.command
# def test():
# 	'''Run the unit tests'''
# 	import unittest
# 	tests = unittest.TestLoader().discover('tests')
# 	unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def test(coverage=False):
	"""Run the unit tests"""
	if coverage and not os.environ.get('FLASK_COVERAGE'):
		import subprocess
		os.environ['FLASK_COVERAGE'] = '1'
		sys.exit(subprocess.call(sys.argv))

	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)
	if COV:
		COV.stop()
		COV.save()
		print('Coverage Summary:')
		COV.report()
		basedir = os.path.abspath(os.path.dirname(__file__))
		covdir = os.path.join(basedir, 'tmp/coverage')
		COV.html_report(directory=covdir)
		print('HTML version: file://%s/index.html' % covdir)
		COV.erase()

@manager.command
def profile(length=25, profile_dir=None):
	"""Start the application under the code profiler."""
	from werkzeug.contrib.profiler import ProfilerMiddleware
	app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
								profile_dir=profile_dir)
	app.run(debug=False)


if __name__=='__main__':
	manager.run()
