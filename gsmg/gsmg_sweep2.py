#!/usr/bin/env python3
"""
gsmg_sweep2.py — round 2: full phase plaintexts as candidate X values.
The author's confirmed convention: password = sha256(X).hex where X is a
plaintext answer (sentence/phrase). The decrypted phase texts are the largest
"texts" in the puzzle — "HASHTHETEXT" hints the final password may derive from
hashing a text body.
"""
import hashlib
import sys
sys.path.insert(0, "/home/user/puzzle-lab")
from gsmg_sweep import check_pw  # noqa: E402

PHASE2 = """The ironic 2name of the keymakers trying to protect the current digital powers which are still in severe danger due to the keymaker's way of security by hiding, nearly unprotected, in plain sight. {eps3.4_[in one of the valleys of Phillip]runtime-error.r00., where daughters hit magic keypads} When this fails.. Crypto finally to the latin 3Moon? Tell me, 4How so mate?
# X 2 S H 4 Y 0 Q B 15 #
Q -> extend the name of a hackers' swordless fish, the I and W are below.
B -> ((BV80605001911AP)- (sqrt(-1)))^2
H -> (Answer to only this puzzle but nothing else) * -1
S -> cha' + (vagh * jav)
Ok kid, on the highway, let put it in the worst gear."""

PHASE321 = """YOUR LIFE IS THE SUM OF A REMAINDER OF AN UNBALANCED EQUATION INHERENT TO THE PROGRAMMING OF THIS PUZZLE
YOU ARE THE EVENTUALITY OF AN ANOMALY WHICH DESPITE MY SINCEREST EFFORTS I HAVE BEEN UNABLE TO ELIMINATE
FROM WHAT IS OTHERWISE A HARMONY OF MATHEMATICAL PRECISION WHILE IT REMAINS A BURDEN TO SEDULOUSLY AVOID IT
IT IS NOT UNEXPECTED AND THUS NOT BEYOND A MEASURE OF CONTROL WHICH HAS LED YOU INEXORABLY HERE YOU
YOU HAVEN'T ANSWERED MY QUESTION ME QUITE RIGHT INTERESTING THAT WAS QUICKER THAN THE OTHERS PLEASE IF YOU
FIND A WAY TO COMPLETE THE LAST PART OF THE PUZZLE TAKE THE PRIVATE KEY YOUVE EARNED IT BUT PLEASE TAKE
THIS TO HEART THAT WHAT A WISEMAN ABOVE HINTED AT IS WORTH HUNDRED FOURTY OF THE INVESTMENT THAT'S
WHAT US GUYS AT GSMG ARE TRYING TO ACCOMPLISH IN THE END PLEASE JUST HELP US BUILD IT INSTEAD OF JUST
WAISTING YOUR LIFETIME BY HUNTING FOR WORTHLESS PRICES AND THROPHIES LIKE THIS I'M SORRY TO
TELL YOU THAT YOUVE COME THIS FAR BUT YOU'LL NEVER FINISH THE LAST TASK I EXPECT YOU TO SAY BULLSHIT
WELL DENIAL IS THE MOST PREDICTABLE OF ALL HUMAN RESPONSES BUT REST ASSURED THIS WILL NOT BE THE LAST TIME
I HAVE DESTROYED A RESTLESS SOUL AND I HAVE BECOME EXCEEDINGLY EFFICIENT AT IT THE FUNCTION OF THE YOU IS
NOW TO RETURN TO THE SOURCE CODES ALLOWING A TEMPORARY DISSEMINATION OF THE CODE YOU HOPEFULLY CARRY
REINSERTING THE PRIME BASICS AFTER WHICH YOU WILL BE REQUIRED TO SELECT FROM OVER TWENTY-THREE CIPHERS
SIXTEEN ENCRYPTIONS AND OR SEVEN INTERTWINED PASSWORDS TO FIND THE ACTUAL PRIVATE KEYNOTE THAT ALSO
BRUTE FORCING MIGHT BE REQUIRED FAILURE TO COMPLY WITH THIS PROCESS WILL RESULT IN A CATACLYSMIC
SYSTEM CRASH KILLING YOUR WILLPOWER WHICH COUPLED WITH THE EXTERMINATION OF YOUR WILL TO LIVE AND WILL
ULTIMATELY RESULT IN THE EXTINCTION OF THE ENTIRENESS OF YOURSELF SELF GOOD LUCK NEVERTHELESS I REALLY
HOPE YOURE THE ONE CIAO BELLA O"""

PHASE322 = "IN CASE YOU MANAGE TO CRACK THIS THE PRIVATE KEYS BELONG TO HALF AND BETTER HALF AND THEY ALSO NEED FUNDS TO LIVE"

SALPHA = "dbbibfbhccbegbihabebeihbegegebebbgehhebhhfbabfdhbeffcdbbfcccgbfeeggecbedcibfbffgigbeeea"  # partial

# key sentence fragments
FRAGS = [
    "what a wiseman above hinted at is worth hundred fourty of the investment",
    "worth hundred fourty of the investment",
    "hundred fourty",
    "hundred forty",
    "the wise man above",
    "a wiseman above",
    "wiseman",
    "take the private key youve earned it",
    "youve earned it",
    "the private keys belong to half and better half",
    "half and better half",
    "they also need funds to live",
    "need funds to live",
    "funds to live",
    "the actual private keynote",
    "private keynote",
    "select from over twenty-three ciphers",
    "over twenty three ciphers sixteen encryptions and or seven intertwined passwords",
    "twenty three ciphers",
    "sixteen encryptions",
    "seven intertwined passwords",
    "brute forcing might be required",
    "the prime basics",
    "return to the source codes",
    "a temporary dissemination of the code",
    "the function of the you",
    "i have destroyed a restless soul",
    "restless soul",
    "youll never finish the last task",
    "the last task",
    "i expect you to say bullshit",
    "bullshit",
    "ciac bella o",
    "ciao bella",
    "youre the one",
    "hope youre the one",
    "hope you are the one",
    "good luck",
    "goodluck",
    "the eventualitiy of an anomaly",
    "you are the eventuality of an anomaly",
    "the sum of a remainder",
    "sum of a remainder",
    "unbalanced equation",
    "inherent to the programming of this puzzle",
    "harmony of mathematical precision",
    "measure of control",
    "cataclysmic system crash",
    "killing your willpower",
    "the first one seen",
    "sad board",
    "raising the stakes",
    "without extra chances of winning",
    "thingky mvps",
]


def variants(s: str):
    yield s
    yield s.upper()
    yield s.lower()
    yield s.replace("'", "")
    yield s.replace("'", "").upper()
    yield s.replace(" ", "")
    yield s.replace(" ", "").upper()
    yield s.replace(" ", "").lower()
    yield s[::-1]
    yield s.replace("u", "you").replace("you", "u")
    yield s.replace("the", "").replace("  ", " ").strip()
    yield s.replace(" a ", " ").replace("  ", " ").strip()


def main():
    bases = [PHASE2, PHASE321, PHASE322, SALPHA] + FRAGS
    # also per-line of the big texts
    for t in (PHASE2, PHASE321):
        bases += [ln.strip() for ln in t.splitlines() if len(ln.strip()) > 8]
    seen, n, t0 = set(), 0, __import__("time").time()
    print(f"[sweep2] {len(bases)} base texts", flush=True)
    for b in bases:
        for v in variants(b):
            if v in seen:
                continue
            seen.add(v)
            pw = hashlib.sha256(v.encode()).hexdigest().encode()
            n += 1
            if check_pw(pw, "sha256(X)"):
                print(f"\n*** MATCH *** X={v!r}")
                return
    print(f"[sweep2] {n} candidates, no match ({__import__('time').time()-t0:.1f}s)")


if __name__ == "__main__":
    main()