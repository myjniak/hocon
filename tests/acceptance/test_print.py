from hocon import parser


def test_print():
    data = """{a: 1
    a: {c: 3}
    b: [${a.c}, 4]
    }
    """
    parsed = parser.parse(data)
    assert str(parsed) == "{'a': 【〈'1'〉, 〈{'c': 〈'3'〉}〉】, 'b': 〈[〈${a.c}〉, 〈'4'〉]〉}"
