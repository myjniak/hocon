from time import time

import pytest

import hocon


@pytest.mark.skip
def test_big():
    """To show we are FASTER than pyhocon :>"""
    data = """
    ############################################################
# ROOT OPTIONALS (all undefined on purpose)
############################################################

root {
  a = ${?UNDEF_A}
  b = ${?UNDEF_B}
  c = ${?UNDEF_C}
  d = ${?UNDEF_D}
}

############################################################
# CASE 1 — OPTIONAL COLLAPSE TO EMPTY OBJECT
############################################################

case1 {
  x: ${?root.a}
  x: ${?root.b}
  x: ${?root.c}
  x: ${?root.d}
  y: 1
}

############################################################
# CASE 1 NESTED / CASCADED
############################################################

case1-nested {
  level1 {
    x: ${?root.a}
    x: ${?root.b}

    level2 {
      x: ${?root.c}
      x: ${?root.d}

      level3 {
        x: ${case1.y}
        x: ${?root.a}
      }
    }
  }
}

############################################################
# CASE 2 — OBJECT VS SUBSTITUTION CONFLICT (ERROR)
############################################################

case2 {
  a: ${case1.y}
  a: xd
}

############################################################
# CASE 2 DEEP CONFLICT CHAIN
############################################################

case2-deep {
  level1 {
    a: ${case1.y}
    a: xd

    level2 {
      a: ${case2-deep.level1.a}
      a: xd

      level3 {
        a: ${case2-deep.level1.level2.a}
        a: xd
      }
    }
  }
}

############################################################
# CASE 3 — ARRAY OVERRIDE (VALID)
############################################################

case3 {
  a: ${case1.y}
  a: [1, 2, 3]
}

############################################################
# CASE 3 NESTED + CONCAT
############################################################

case3-nested {
  level1 {
    a: ${case1.y}
    a: [1,2]

    level2 {
      a: ${case3.level1.a}
      a: [3,4]

      level3 {
        a: ${case3-nested.level1.level2.a}
        a: [5,6]
      }
    }
  }
}

############################################################
# CASE 4 — OBJECT MERGE CASCADE
############################################################

case4 {
  a: {a: 1} {b: ${case1.y}} {c: ${case1.y}}
  a: {b: 2} {c: 3}
}

############################################################
# CASE 4 DEEP MERGE WITH OPTIONALS
############################################################

case4-nested {
  level1 {
    a: {a: 1} {b: ${?root.a}} {c: ${?root.b}}
    a: {b: 2}

    level2 {
      a: ${case4-nested.level1.a} {c: ${?root.c}}
      a: {c: 3}

      level3 {
        a: ${case4-nested.level1.level2.a} {d: ${?root.d}}
        a: {d: 4}
      }
    }
  }
}

############################################################
# MIXED CHAOS: ALL RULES COMBINED
############################################################

chaos {
  ##########################################################
  # Optional collapse feeding into merge
  ##########################################################
  x: ${?root.a}
  x: 3
  x: ${?root.b}

  ##########################################################
  # Object merge + optional disappearance
  ##########################################################
  obj: {a: 1} {b: ${chaos.x}} {c: ${chaos.x}}
  obj: {b: 2}

  ##########################################################
  # Array override after substitution
  ##########################################################
  arr: ${chaos.x}
  arr: [10,20,30]

  ##########################################################
  # Conflict branch (should fail)
  ##########################################################
  conflict {
    a: ${chaos.x}
    a: a
  }

  ##########################################################
  # Deep mixed nesting
  ##########################################################
  deep {
    level1 {
      v: ${?root.a}
      v: ${?root.b}

      level2 {
        v: ${chaos.deep.level1.v}
        v: [1,2,3]

        level3 {
          v: {x: 1} {y: ${chaos.deep.level1.level2.v}}
          v: {y: 2}

          level4 {
            v: ${chaos.deep.level1.level2.level3.v}
            v: {z: 3}

            level5 {
              v: ${chaos.deep.level1.level2.level3.level4.v}
              v: ${?root.c}
            }
          }
        }
      }
    }
  }
}

############################################################
# CROSS-REFERENCED CHAOS
############################################################

cross {
  a: ${case1.y}
  a: a

  b: ${case3.a}
  b: [100,200]

  c: ${case4.a}
  c: {extra: 999}

  d: ${case1-nested.level1.level2.level3.x}
  d: ${?root.a}

  e: {a: ${cross.a}} {b: ${cross.b}} {c: ${cross.c}}
}

############################################################
# FINAL AGGREGATION
############################################################

final {
  from-case1 = ${case1.y}
  from-case3 = ${case3.a}
  from-case4 = ${case4.a}

  combined {
    a: ${final.from-case1}
    a: [7,8,9]

    b: {x: ${final.from-case3}} {y: ${final.from-case4}}
  }
}

############################################################
# END
############################################################
    """
    import pyhocon
    start = time()
    for _ in range(100):
        hocon.loads(data)
    stop = time()
    hocon2_time = stop - start
    print(f"{hocon2_time=}")
    start = time()
    for _ in range(100):
        pyhocon.ConfigFactory.parse_string(data)
    stop = time()
    pyhocon_time = stop - start
    print(f"{pyhocon_time=}")
    print(f"hocon2 is {pyhocon_time/hocon2_time} faster than pyhocon!")
