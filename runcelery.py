from essoadmin.app import create_app, make_celery

app = create_app(register_all=False)
celery = make_celery(app)

if __name__ == '__main__':
    with app.app_context():
        celery.start()