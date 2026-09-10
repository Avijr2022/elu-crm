from importlib import import_module


def main():
    m = import_module('app.api.v1.integrations.deepseek')
    print('Imported module:', m)
    print('Router prefix:', getattr(m.router, 'prefix', None))


if __name__ == '__main__':
    main()
