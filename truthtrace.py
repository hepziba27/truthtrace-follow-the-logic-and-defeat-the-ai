#!/usr/bin/env python3
"""
TruthTrace - follow the logic, defeat the AI.

A Knights & Knaves deduction game. Knights always tell the truth, knaves
always lie. Each islander makes one statement. You and the AI race to work
out who is who. The AI reasons honestly, one statement at a time, pruning
every "world" (assignment of knight/knave) that contradicts the statement.
Name the correct solution before the AI narrows things down to one world
and you win.

No third-party dependencies. Python 3.8+.
"""

import argparse
import itertools
import random
import sys

NAMES = ["Alice", "Bob", "Carol", "Dave", "Eve"]


# --------------------------------------------------------------------------
# Statements
# --------------------------------------------------------------------------
# A statement is a tuple: (kind, a) or (kind, a, b), where a and b are
# indexes of people. A world is a tuple of booleans: True = knight.

def evaluate(stmt, world):
    """Return whether the statement is true in the given world."""
    kind = stmt[0]
    if kind == "is_knight":
        return world[stmt[1]]
    if kind == "is_knave":
        return not world[stmt[1]]
    if kind == "same":
        return world[stmt[1]] == world[stmt[2]]
    if kind == "diff":
        return world[stmt[1]] != world[stmt[2]]
    if kind == "both_knights":
        return world[stmt[1]] and world[stmt[2]]
    if kind == "one_knave":  # at least one of the two is a knave
        return (not world[stmt[1]]) or (not world[stmt[2]])
    raise ValueError(f"unknown statement kind: {kind}")


def describe(stmt, names):
    kind = stmt[0]
    a = names[stmt[1]]
    b = names[stmt[2]] if len(stmt) > 2 else None
    return {
        "is_knight": f"{a} is a knight.",
        "is_knave": f"{a} is a knave.",
        "same": f"{a} and {b} are the same type.",
        "diff": f"{a} and {b} are different types.",
        "both_knights": f"{a} and {b} are both knights.",
        "one_knave": f"At least one of {a} and {b} is a knave.",
    }[kind]


def consistent(speaker, stmt, world):
    """A speaker's statement fits a world if knights speak truth, knaves lie."""
    return world[speaker] == evaluate(stmt, world)


def all_worlds(n):
    return list(itertools.product([True, False], repeat=n))


# --------------------------------------------------------------------------
# Puzzle generation
# --------------------------------------------------------------------------

def random_statement(speaker, n, rng):
    kind = rng.choice(
        ["is_knight", "is_knave", "same", "diff", "both_knights", "one_knave"]
    )
    others = [i for i in range(n) if i != speaker]
    if kind in ("is_knight", "is_knave"):
        return (kind, rng.choice(others))
    a, b = rng.sample(range(n), 2)
    return (kind, a, b)


def generate_puzzle(n, rng, max_tries=20000):
    """Return (statements, solution) where the solution is unique."""
    worlds = all_worlds(n)
    for _ in range(max_tries):
        stmts = [random_statement(i, n, rng) for i in range(n)]
        sols = [
            w for w in worlds
            if all(consistent(i, s, w) for i, s in enumerate(stmts))
        ]
        if len(sols) == 1:
            return stmts, sols[0]
    raise RuntimeError("Could not generate a uniquely solvable puzzle.")


# --------------------------------------------------------------------------
# Display helpers
# --------------------------------------------------------------------------

def world_str(world):
    return "".join("K" if w else "N" for w in world)


def world_pretty(world, names):
    return ", ".join(
        f"{names[i]}={'Knight' if w else 'Knave'}" for i, w in enumerate(world)
    )


def parse_guess(text, n):
    cleaned = text.replace(" ", "").replace(",", "").upper()
    if len(cleaned) != n or any(c not in "KN" for c in cleaned):
        return None
    return tuple(c == "K" for c in cleaned)


# --------------------------------------------------------------------------
# Game
# --------------------------------------------------------------------------

def play_round(n, rng, ask=input, out=print):
    names = NAMES[:n]
    stmts, solution = generate_puzzle(n, rng)

    out("\n" + "=" * 60)
    out("TRUTHTRACE: Knights always tell the truth. Knaves always lie.")
    out("=" * 60)
    for i, s in enumerate(stmts):
        out(f"  {names[i]} says: \"{describe(s, names)}\"")
    out(f"\nGuess format: {n} letters, K = knight, N = knave, "
        f"in order {', '.join(names)}.  Example: {'K' * n}")
    out("Commands: 'worlds' shows what the AI still considers possible, "
        "'q' quits.\n")

    remaining = all_worlds(n)

    for step, (speaker, stmt) in enumerate(enumerate(stmts), start=1):
        # ----- Player turn -----
        while True:
            raw = ask(f"[Turn {step}] Your guess (Enter to pass): ").strip()
            if raw.lower() in ("q", "quit", "exit"):
                out(f"\nYou quit. The answer was {world_str(solution)}: "
                    f"{world_pretty(solution, names)}")
                return "quit"
            if raw.lower() == "worlds":
                out(f"  AI is still considering {len(remaining)} world(s):")
                for w in remaining[:16]:
                    out(f"    {world_str(w)}")
                if len(remaining) > 16:
                    out(f"    ... and {len(remaining) - 16} more")
                continue
            if raw == "":
                break
            guess = parse_guess(raw, n)
            if guess is None:
                out(f"  Please enter exactly {n} letters using K and N.")
                continue
            if guess == solution:
                out("\nYOU WIN! You traced the logic before the AI did.")
                out(f"  {world_pretty(solution, names)}")
                return "player"
            out("  Not the right assignment. The AI keeps reasoning...")
            break

        # ----- AI turn -----
        before = len(remaining)
        remaining = [w for w in remaining if consistent(speaker, stmt, w)]
        cut = before - len(remaining)
        out(f"\n  AI examines {names[speaker]}'s claim: "
            f"\"{describe(stmt, names)}\"")
        out(f"  If {names[speaker]} is a knight the claim must be true; "
            f"if a knave it must be false.")
        out(f"  Eliminated {cut} world(s). {len(remaining)} remain.\n")

        if len(remaining) == 1:
            out("AI WINS. It narrowed the possibilities to a single world:")
            out(f"  {world_pretty(remaining[0], names)}")
            return "ai"

    # Unreachable for uniquely solvable puzzles, kept as a safety net.
    out("Round ended.")
    return "draw"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="TruthTrace: follow the logic, defeat the AI."
    )
    parser.add_argument("-n", "--people", type=int, default=3,
                        choices=range(3, 6), metavar="{3,4,5}",
                        help="number of islanders (difficulty), default 3")
    parser.add_argument("-r", "--rounds", type=int, default=3,
                        help="number of rounds, default 3")
    parser.add_argument("--seed", type=int, default=None,
                        help="random seed for reproducible puzzles")
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    score = {"player": 0, "ai": 0, "draw": 0, "quit": 0}

    try:
        for r in range(1, args.rounds + 1):
            print(f"\n--- Round {r} of {args.rounds} ---")
            result = play_round(args.people, rng)
            score[result] += 1
            if result == "quit":
                break
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")

    print("\n" + "=" * 60)
    print(f"FINAL SCORE  You: {score['player']}   AI: {score['ai']}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
