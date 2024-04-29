from hocon._main import parse, preresolve, resolve


def test_what():
    data = """
    d = {e: amen "jea", f.g: [hihi, {253: 78, 156: ${x}}, 2]}      ,
    d = {e: egzakra}
    a = ${d.f.g.1.156}
    x = ${d.e}
    """
    x = parse(data)
    # print(x)
    y = preresolve(x)
    z = resolve(y)
    print(z["a"])
