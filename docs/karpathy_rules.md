# Karpathy Coding Rules — Applied to This Build

Source: Andrej Karpathy's LLM coding guidelines. Enforced for all code in `src/`.

## 1. Think Before Coding
- State assumptions before implementing. If the PRD is ambiguous, check `docs/` first.
- If multiple approaches exist, pick the simpler one and say why.
- If something is unclear, stop and ask — don't guess under time pressure.

## 2. Simplicity First
- No features beyond what the PRD specifies.
- No abstractions for single-use code (this is a one-day build).
- No "flexibility" or "configurability" that wasn't requested.
- If you write 200 lines and it could be 50, rewrite it.
- **Test:** "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes
- Touch only what you must. Don't "improve" adjacent code.
- Match existing style. Don't refactor things that aren't broken.
- Every changed line traces directly to a user request or a failing test.

## 4. Goal-Driven Execution
- Every component has a verifiable test before the next one starts:
  1. `proxy.py` → verify: hard ceiling trips on burst, normal traffic passes
  2. `simulator.py` → verify: all 3 burst patterns fire correctly
  3. `classifier.py` → verify: correct classification for each pattern
  4. `dashboard.py` → verify: state change visible within 1 second
  5. Full rehearsal → verify: 90-second script runs clean 3x in a row

## Applied to Hackathon Time Pressure
- Don't spend time on code beauty. Spend time on *working*.
- Don't add type hints to internal functions. Do add them to API boundaries.
- Don't write docstrings for obvious functions. Do write them for the proxy's decision logic.
- Terminal dashboard (rich) before web dashboard. Always.
- If the model API is slow, cache a known-good response for the demo. Label it honestly.

_Last updated: 2026-09-27_
