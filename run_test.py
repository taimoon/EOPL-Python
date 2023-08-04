if __name__ == '__main__':
    from test import (test_let_lang,
        test_typed_modules,
        test_modules,
        test_class,
        test_checked,
    )
    
    test_let_lang.test_all()
    test_checked.test_all()
    test_modules.test_all()
    test_typed_modules.test_all()
    test_class.test_all()
    
