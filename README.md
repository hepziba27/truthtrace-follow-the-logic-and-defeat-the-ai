# TruthTrace

**Follow the logic. Defeat the AI.**

TruthTrace is a command-line deduction game built on the classic Knights and Knaves puzzle. Knights always tell the truth, knaves always lie, and every islander makes one statement. You race an AI opponent to work out who is who.

The AI plays fair and shows its work. Each turn it takes one statement, checks it against every possible world, and eliminates the ones that contradict it. If it narrows the possibilities down to a single world before you name the correct answer, it wins. If you trace the logic faster, you win.

## Features

- Randomly generated puzzles, each guaranteed to have exactly one solution
- Three difficulty levels (3, 4 or 5 islanders)
- A transparent AI that prints its reasoning every turn
- Six statement types: "X is a knight", "X is a knave", "same type", "different types", "both knights", "at least one knave"
- Reproducible games with a seed
- Zero dependencies, pure Python 3.8+

## Quick start

```bash
git clone https://github.com/<your-username>/truthtrace.git
cd truthtrace
python3 truthtrace.py
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `-n`, `--people` | Number of islanders: 3, 4 or 5 | 3 |
| `-r`, `--rounds` | Number of rounds | 3 |
| `--seed` | Random seed for reproducible puzzles | random |

Example:

```bash
python3 truthtrace.py -n 4 -r 5 --seed 42
```

## How to play

1. Read each islander's statement.
2. Type your guess as one letter per person, in order: `K` for knight, `N` for knave. For example, `KNK` means Alice and Carol are knights and Bob is a knave.
3. Press Enter to pass and let the AI take its turn.
4. Type `worlds` to see which assignments the AI still considers possible.
5. Type `q` to quit.

The core rule: a **knight's** statement must be true, a **knave's** statement must be false.

### Example

```
Alice says: "Bob is a knave."
Bob says: "Alice and Carol are the same type."
Carol says: "At least one of Alice and Bob is a knave."
```

Work out which combination makes every speaker consistent with their type. Can you get there before the AI prunes the last wrong world?

## How the AI works

The AI enumerates all 2^n knight/knave assignments. On each turn it processes one speaker's statement and removes every assignment where the speaker's type does not match the truth of their claim. It never guesses. It wins when exactly one assignment survives.

You have the advantage of intuition and of moving first each turn. The AI has the advantage of never making a mistake.

## Project structure

```
truthtrace/
├── truthtrace.py   # game, puzzle generator and AI solver
└── README.md
```

## Ideas for contributions

- Add new statement types (for example, "exactly one of us is a knave")
- Add a third type such as a "spy" who may do either
- Build a web or GUI front end
- Add a hint system or timed mode
- Add unit tests for the generator and solver

## License

MIT. Add a `LICENSE` file to your repository if you want to publish under this license.
