"""Solver-checked rule set for UKLO 2017 Problem 4, "A little Tshiluba".

The grammar below is hand-derived from the puzzle's 12 context sentences
(plus the cimuma/bimuma vocabulary rows) and encoded as an ASP program.
clingo then certifies derivability: an integrity constraint requires every
context sentence to be regenerated *exactly* from its semantic frame, so
the program is UNSAT if any rule is wrong. The eight question cells are
derived from the same rules (questions 1-5: English -> Tshiluba generation;
questions 6-8: the claimed reading's frame must regenerate the given
Tshiluba string, and the English gloss is rendered from that frame).

Run:  uv run python experiments/04_hypothesis_search/tshiluba_2017/check_tshiluba.py
"""

import clingo

ASP = r"""
% ---------------------------------------------------------------------------
% LEXICON: stem, gender class, English sg/pl
% class h = human (mu-/ba-), a = animal (bare/ba-), t = thing (ci-/bi-)
% ---------------------------------------------------------------------------
noun(kaji,    h, "woman",   "women").
noun(luma,    h, "man",     "men").
noun(ana,     h, "child",   "children").
noun(lunda,   h, "friend",  "friends").
noun(kulu,    h, "adult",   "adults").
noun(mbwa,    a, "dog",     "dogs").
noun(ntambwe, a, "lion",    "lions").
noun(nzolu,   a, "chicken", "chickens").
noun(mbuji,   a, "goat",    "goats").
noun(muma,    t, "fruit",   "fruits").

stemstr(kaji,"kaji"). stemstr(luma,"luma"). stemstr(ana,"ana").
stemstr(lunda,"lunda"). stemstr(kulu,"kulu"). stemstr(mbwa,"mbwa").
stemstr(ntambwe,"ntambwe"). stemstr(nzolu,"nzolu"). stemstr(mbuji,"mbuji").
stemstr(muma,"muma").

verb(mona, "mona"). verb(peta, "peta").
tense(past, "vwa"). tense(pres, "di").

% ---------------------------------------------------------------------------
% R1  Noun-class number prefixes (inner layer)
%     human:  sg mu- / pl ba-;  animal: sg bare / pl ba-;  thing: sg ci- / pl bi-
% ---------------------------------------------------------------------------
base(N, sg, @cat("mu", S)) :- noun(N,h,_,_), stemstr(N,S).
base(N, pl, @cat("ba", S)) :- noun(N,h,_,_), stemstr(N,S).
base(N, sg, S)             :- noun(N,a,_,_), stemstr(N,S).
base(N, pl, @cat("ba", S)) :- noun(N,a,_,_), stemstr(N,S).
base(N, sg, @cat("ci", S)) :- noun(N,t,_,_), stemstr(N,S).
base(N, pl, @cat("bi", S)) :- noun(N,t,_,_), stemstr(N,S).

% ---------------------------------------------------------------------------
% R2  Diminutive prefixes (outer layer, added to the full base form)
%     sg ka- / pl tu-
% ---------------------------------------------------------------------------
nounform(N, Num, plain, B)            :- base(N, Num, B).
nounform(N, sg,  dim, @cat("ka", B))  :- base(N, sg, B).
nounform(N, pl,  dim, @cat("tu", B))  :- base(N, pl, B).

% ---------------------------------------------------------------------------
% R3  Subject concord, selected by the subject's outermost prefix class.
%     concord(Num, Dim, Gender, TensePrefix, VerbPrefix)
%     sg human/animal -> u- on the tense word, mu- on the verb
%     pl human/animal -> ba- / ba-
%     thing           -> ci-/ci- (sg), bi-/bi- (pl)
%     diminutive      -> ka-/ka- (sg), tu-/tu- (pl)   [overrides gender]
% ---------------------------------------------------------------------------
concord(sg, plain, h, "u",  "mu").  concord(sg, plain, a, "u",  "mu").
concord(pl, plain, h, "ba", "ba").  concord(pl, plain, a, "ba", "ba").
concord(sg, plain, t, "ci", "ci").  concord(pl, plain, t, "bi", "bi").
concord(sg, dim,   G, "ka", "ka") :- noun(_,G,_,_).
concord(pl, dim,   G, "tu", "tu") :- noun(_,G,_,_).

% ---------------------------------------------------------------------------
% R4  Word formation: tense word = concord + tense stem (vwa past / di pres)
%     verb word = concord + verb stem
% R5  Constituent order: Subject  TenseWord  VerbWord  Object .
% ---------------------------------------------------------------------------
sentence(F, @cat(SW, " ", TW, " ", VW, " ", OW, ".")) :-
    frame(F, N1,Num1,D1, T, V, N2,Num2,D2),
    nounform(N1,Num1,D1,SW), nounform(N2,Num2,D2,OW),
    noun(N1,G,_,_),
    concord(Num1,D1,G,TP,VP),
    tense(T,TS), verb(V,VS),
    TW = @cat(TP,TS), VW = @cat(VP,VS).

% ---------------------------------------------------------------------------
% CONTEXT: 12 sentences + 2 vocabulary rows, each with its semantic frame.
% Integrity constraints: the grammar must regenerate each attested string.
% ---------------------------------------------------------------------------
frame(c01, kaji,sg,plain,    past, mona, ana,sg,plain).
att(c01, "mukaji uvwa mumona muana.").
frame(c02, kaji,pl,plain,    past, mona, ana,sg,plain).
att(c02, "bakaji bavwa bamona muana.").
frame(c03, luma,sg,plain,    past, mona, kaji,pl,plain).
att(c03, "muluma uvwa mumona bakaji.").
frame(c04, luma,sg,plain,    past, mona, mbuji,pl,plain).
att(c04, "muluma uvwa mumona bambuji.").
frame(c05, luma,sg,plain,    pres, mona, mbuji,pl,plain).
att(c05, "muluma udi mumona bambuji.").
frame(c06, nzolu,pl,plain,   past, mona, ntambwe,pl,plain).
att(c06, "banzolu bavwa bamona bantambwe.").
frame(c07, mbwa,pl,dim,      past, mona, luma,pl,plain).
att(c07, "tubambwa tuvwa tumona baluma.").
frame(c08, mbwa,sg,plain,    past, mona, ntambwe,sg,plain).
att(c08, "mbwa uvwa mumona ntambwe.").
frame(c09, ntambwe,sg,plain, past, mona, nzolu,pl,dim).
att(c09, "ntambwe uvwa mumona tubanzolu.").
frame(c10, nzolu,sg,dim,     past, mona, ntambwe,pl,dim).
att(c10, "kanzolu kavwa kamona tubantambwe.").
frame(c11, kulu,pl,dim,      past, mona, mbwa,sg,plain).
att(c11, "tubakulu tuvwa tumona mbwa.").
frame(c12, lunda,sg,dim,     past, peta, ntambwe,sg,dim).
att(c12, "kamulunda kavwa kapeta kantambwe.").

attn(v01, muma,sg,plain, "cimuma").
attn(v02, muma,pl,plain, "bimuma").

:- att(F, A), sentence(F, S), S != A.
:- att(F, A), not sentence(F, A).
:- attn(_, N,Num,D, A), nounform(N,Num,D,S), S != A.
:- attn(_, N,Num,D, A), not nounform(N,Num,D,A).

% ---------------------------------------------------------------------------
% QUESTIONS. q1-q5: generate Tshiluba. q6-q8: the claimed frame must
% regenerate the given string (constraint), gloss rendered by the runner.
% ---------------------------------------------------------------------------
qnoun(q1, mbwa,sg,plain).                                   % "Dog"
frame(q2, luma,sg,plain,  past, mona, ana,sg,plain).        % man saw child
frame(q3, nzolu,sg,plain, past, mona, mbwa,pl,plain).       % chicken saw dogs
frame(q4, kulu,sg,plain,  past, peta, mbuji,sg,plain).      % adult found goat
frame(q5, mbuji,pl,dim,   past, peta, ana,sg,dim).          % small goats found small child

qnoun(q6, lunda,pl,plain).            given(q6, "balunda").
frame(q7, muma,sg,plain,    past, mona, ntambwe,sg,plain).
given(q7, "cimuma civwa cimona ntambwe.").
frame(q8, ntambwe,sg,plain, past, mona, muma,pl,dim).
given(q8, "ntambwe uvwa mumona tubimuma.").

:- given(Q,A), frame(Q,_,_,_,_,_,_,_,_), sentence(Q,S), S != A.
:- given(Q,A), qnoun(Q,N,Num,D), nounform(N,Num,D,S), S != A.

out(Q, S) :- sentence(Q, S), frame(Q,_,_,_,_,_,_,_,_).
out(Q, S) :- qnoun(Q, N,Num,D), nounform(N,Num,D,S).
#show out/2.
"""

# English rendering for the decode questions (q6-q8), from the same frames.
ENG_N = {"kaji": ("woman","women"), "luma": ("man","men"),
         "ana": ("child","children"), "lunda": ("friend","friends"),
         "kulu": ("adult","adults"), "mbwa": ("dog","dogs"),
         "ntambwe": ("lion","lions"), "nzolu": ("chicken","chickens"),
         "mbuji": ("goat","goats"), "muma": ("fruit","fruits")}
ENG_V = {("mona","past"): "saw", ("mona","pres"): "sees",
         ("peta","past"): "found", ("peta","pres"): "finds"}

def eng_np(stem, num, dim):
    n = ENG_N[stem][0 if num == "sg" else 1]
    return ("small " if dim == "dim" else "") + n

class Ctx:
    """Grounding context: @cat concatenates clingo strings."""

    def cat(self, *args):
        return clingo.String("".join(a.string for a in args))


def main():
    ctl = clingo.Control(["0"])
    ctl.add("base", [], ASP)
    ctl.ground([("base", [])], context=Ctx())
    models = []
    ctl.solve(on_model=lambda m: models.append(
        {str(a.arguments[0]): a.arguments[1].string
         for a in m.symbols(shown=True)}))
    if not models:
        print("UNSAT: the rule set fails to regenerate the context exactly.")
        return 1
    assert len(models) == 1, "grammar should be deterministic"
    out = models[0]
    print("CERTIFIED: all 12 context sentences + 2 vocabulary forms "
          "regenerate exactly; questions derive as:\n")
    print(f"  1  'Dog'                                   -> {out['q1']}")
    for q in ("q2", "q3", "q4", "q5"):
        print(f"  {q[1]}  (English->Tshiluba)                     -> {out[q]}")
    # Decode questions: frames verified by constraints above; gloss here.
    print(f"  6  balunda                                 -> "
          f"(the) {eng_np('lunda','pl','plain')}")
    print(f"  7  cimuma civwa cimona ntambwe.            -> The "
          f"{eng_np('muma','sg','plain')} saw the "
          f"{eng_np('ntambwe','sg','plain')}.")
    print(f"  8  ntambwe uvwa mumona tubimuma.           -> The "
          f"{eng_np('ntambwe','sg','plain')} saw the "
          f"{eng_np('muma','pl','dim')}.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
