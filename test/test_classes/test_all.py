def test_all_by_variant(value_of_prog):
    from .test_simple_class import test_simple_class
    from .test_leaf_class import test_leaf_class
    from .test_color_class import test_color_class
    from .test_polygon import test_polygon
    from .test_class_scope import (
        test_class_scope1,
        test_class_scope2,
        test_super
    )
    from .test_queue import test_queue_class
    test_simple_class(value_of_prog)
    test_leaf_class(value_of_prog)
    test_color_class(value_of_prog)
    test_polygon(value_of_prog)
    test_class_scope1(value_of_prog)
    test_class_scope2(value_of_prog)
    test_super(value_of_prog)
    test_queue_class(value_of_prog)

def test_all():
    print("test class")
    from CLASSES import value_of_prog
    test_all_by_variant(value_of_prog)
    print("end of class test")