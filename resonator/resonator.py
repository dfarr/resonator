from __future__ import annotations

import os
import time
import uuid

from collections.abc import Generator
from typing import Any

from resonate import Resonate, Context
from resonate.task_sources import Poller

from resonator import parser


grp = os.getenv("GRP")
pid = os.getenv("PID")
resonate = Resonate(pid=pid, task_source=Poller(group=grp))

@resonate.register(name="+")
def add(ctx: Context, x: int, y: int) -> int:
    print(f"{grp}: {x} + {y}")
    return x + y

@resonate.register(name="-")
def sub(ctx: Context, x: int, y: int) -> int:
    print(f"{grp}: {x} - {y}")
    return x - y

@resonate.register(name="*")
def mul(ctx: Context, x: int, y: int) -> int:
    print(f"{grp}: {x} * {y}")
    return x * y

@resonate.register(name="=")
def clc(ctx: Context, expr: parser.Expr) -> Generator[Any, Any, int]:
    if grp:
        print(f"{grp}/{pid}: {expr}")

    match expr:
        case (op, lhs, rhs):
            # Send the expressions to the exp task queue with
            # preference.
            #
            # The expressions are sent to the task queue as invocations
            # which return a handle so we can wait for the result later.
            px = yield ctx.rfi(clc, lhs).options(send_to="poll://exp/lhs")
            py = yield ctx.rfi(clc, rhs).options(send_to="poll://exp/rhs")

            # Wait for results from the lhs and rhs tasks.
            vx = yield px
            vy = yield py

            # Send the operation to the ops task queue.
            #
            # The operation is sent to the task queue as a call which returns
            # the result directly.
            return (yield ctx.rfc(op, vx, vy).options(send_to="poll://ops"))

        case x:
            return x

def run():
    if not grp:
        print("""\
RRRR   EEEEE  SSSSS   OOO   N   N  AAAAA  TTTTT  OOO   RRRR
R   R  E      S      O   O  NN  N  A   A    T   O   O  R   R
RRRR   EEEE   SSSSS  O   O  N N N  AAAAA    T   O   O  RRRR
R  R   E          S  O   O  N  NN  A   A    T   O   O  R  R
R   R  EEEEE  SSSSS   OOO   N   N  A   A    T    OOO   R   R

Resonator is a distributed calculator that can calculate basic
arithmetic expressions that contain numbers and the following
symbols:
    ( ) + - *

Resonator splits an expression into tasks (sub expressions) and
distributes those tasks to workers to calculate.

Give it a try by typing an expression such as:
    (1 + 2)
    (1 + 2) * 3
    (1 + 2) * (3 - 4)
""")

    while True:
        try:
            # worker loop
            if grp:
                time.sleep(60)
                continue

            # main loop
            if expr := input("❯ "):
                # calculate the expression
                h = clc.run(str(uuid.uuid4()), parser.parse(expr))

                # print the result
                print(f"""
{expr}
= {h.result()}
""")
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Something went wrong: {e}")


if __name__ == "__main__":
    run()
