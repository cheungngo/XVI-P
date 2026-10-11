#!/usr/bin/env python3
"""XVI-P p14r: OPERATIONAL dimensional reduction (DRED) for the P.5 prescription.

Index algebra, lifting rule for the exported integrands, tensor reduction with ghat projections, and the
Laurent / MS-bar finite-part extraction with d kept symbolic.  NO loop integral is evaluated: scalar integrals
  +>  stay
symbols J_<graph>[a,b]; the toy checks use GENERIC Laurent placeholders  a/eps + b + c*eps  (not values of any
integral of this theory).

Background literature (cited as background only; nothing is imported from it): W. Siegel, Phys. Lett. B84 (197
  +> 9)
193 and B94 (1980) 37; D. Stockinger, JHEP 0503 (2005) 076, hep-ph/0503129; A. Signer, D. Stockinger,
Nucl. Phys. B808 (2009) 88, arXiv:0807.4424.

R1 spaces.  Q4S (quasi-4-dimensional; metric g4, tr g4 = 4) = QdS (metric ghat, tr ghat = d) (+) Q(4-d)S (metr
  +> ic
   gtilde, tr gtilde = 4 - d = 2 eps):  g4 = ghat + gtilde,  ghat.ghat = ghat,  gtilde.gtilde = gtilde,
   ghat.gtilde = 0,  g4.X = X.
R2 momenta.  The loop momentum l lies in QdS.  The external momenta p lie in QdS as well (stated choice:
   p.gtilde = 0).  Field, vertex and external-polarisation indices are Q4S indices.
R3 lifting.  The exported numerators are polynomials in LOWER components l_r, p_r (r = 0..3) at fixed external
   component indices.  l_r is read as l.e_(r), with e_(r) the fixed eta-orthonormal basis of Q4S
   (e_(r).e_(s) = eta_rs), so l_r = l.ehat_(r); p_r = p.e_(r) = p.ehat_(r).  The vertex tensors (built from et
  +> a and
   momenta) are lifted with eta -> g4, so the exported component polynomials ARE the lifted objects at fixed
   Q4S components; nothing is truncated.
R4 reduction.  int l^{mu1..mun} F(l^2, l.p) = sum_k C_k B_k, where B_k are the symmetric tensors built from gh
  +> at and
   p.  C_k comes from the Gram (Passarino-Veltman) projection, exact in symbolic d.  Contracting with the lift
  +> ed
   e_(r) gives  ghat_rs := ehat_(r).ehat_(s) = eta_rs - Gt_rs,  with  Gt_rs := etilde_(r).etilde_(s)  evanesce
  +> nt:
   eta^{rs} Gt_rs = 4 - d,  Gt_rs p^s = 0.
R5 order.  Every index contraction, including the external 4D projection (Gt traces), is done BEFORE the Laure
  +> nt
   expansion.  d stays symbolic through MS-bar subtraction and finite-part extraction, so (d-4) x pole finite 
  +> terms
   are retained.  Substituting d = 4 before the expansion is a rule violation.
   p15 CONTRACT CORRECTION (disclosed; finding F1 of the p14r independent rebuild, reproducibility/
   independent_rebuild_report_p14r.json): the p14r safeguard was a HEURISTIC ("the reduction introduced d but 
  +> d is
   absent before the Laurent expansion").  It gave a FALSE POSITIVE on eta^{rs} int l_r l_s/(l^2-m^2) = J (a c
  +> orrect
   d-free result) and a FALSE NEGATIVE under the package's own premature_d4 mutation on the same integral
   (eta_trace_Gt reintroduces d via tr gtilde = 4-d: d J/4, finite error -m^4/2).  The p14r docstring claim th
  +> at
   premature d = 4 "is detected" did not hold in general.  It is replaced by a STRUCTURAL, provenance-based
   safeguard: d is an OPAQUE dimension symbol (OpaqueDimension) that cannot be substituted by subs/xreplace at
  +>  all;
   the only substitution path is substitute_d(expr, value, reason), used by Pipeline.laurent (d -> 4 - 2 eps) 
  +> and by
   explicitly declared post-expansion/report uses, each recorded in D_PROVENANCE.  Any other substitution of d
  +>  raises
   PrematureD4Substitution AT THE SUBSTITUTION SITE, whatever the later shape of the expression.  Numeric trac
  +> es of
   ghat/gtilde (Rules(trace_hat=...)) are refused by the contraction engine (NumericTraceForbidden) unless con
  +> structed
   display_only=True for a mutation display.  Released p14r values are unaffected: in p14r Pipeline.laurent wa
  +> s used
   only on the toy placeholders (no loop integral was evaluated).
   p16 CONTRACT REVISION (disclosed; finding F3 of the p15 independent rebuild, reproducibility/
   independent_rebuild_report_p15.json): expr.replace(d, 4) and sympy.lambdify bypassed the opaque d.  OpaqueD
  +> imension
   now also refuses pattern matching on d (matches: closes expr.replace / expr.match) and the lambdify / code-
  +> printer
   hooks outside substitute_d.  Value paths that never call back into the symbol (Poly(expr, d).eval, string
   round-trips) are excluded by a static scan of the package (tests/test_p16.py).  Rules R1-R6 unchanged; no r
  +> eleased
   value affected (no package code used these paths).
   p17 CONTRACT REVISION (disclosed; findings G1-G3 of the p16 independent rebuild, reproducibility/
   independent_rebuild_report_p16.json).  G2: sympify of a stored string yields a PLAIN Symbol('d') that is no
  +> t the
   opaque d (subs/has against dred.d then silently do nothing).  New guarded loader parse_d(text) parses with
   locals {'d': opaque d} and refuses any result still containing a plain symbol named d; assert_opaque_d(expr
  +> )
   checks an expression.  G3 (wording): the runtime guard refuses subs, xreplace, replace(d, value), evalf(sub
  +> s), N,
   limit, series in d, Lambda(d, .)(value), Subs.doit, lambdify (python/math/mpmath/sympy printers) and
   expr.match(d) with d itself as the pattern; it does NOT refuse a Wild pattern containing d ((d+1).match(d+w
  +> )
   substitutes no value) nor C/Fortran-type code printers (string output).  G1: value paths with no hook --
   replace with ANY function query (lambda or named function), string round-trips (sympify/parse_expr/S of str
  +> (e),
   builtin eval/exec of srepr), Poly(.., d).eval and hand-written expression-tree rebuilds (e.func(*args)) -- 
  +> are
   excluded by a static AST scan of code/p5_calc and code/p5_entry (tests/test_p17.py); the scan is a pattern 
  +> check
   (not a proof): a path written outside these patterns (e.g. dynamic getattr) would not be caught.
   p18 (findings H1/H3/H5 of the p17 independent rebuild; documentation only, no executable statement changed)
  +> : the
   scan (tests/test_p18.py) now also flags Poly(e, d)(4) / e.as_poly(d)(4) calls, all_coeffs (Horner evaluatio
  +> n),
   type(x)(*args) and x.__class__(*args) rebuilds, getattr with a non-literal or hazardous attribute name, ali
  +> ased
   imports or assignments of sympify/S/parse_expr, sympify locals whose 'd' value is not the opaque dred.d, an
  +> d plain
   Symbol('d') / symbols('d') creation -- still a pattern check, not a proof.  parse_d accepts sympy's str() f
  +> orm
   only: parse_d(srepr(e)) RAISES PlainDimensionSymbol (srepr spells Symbol('d') explicitly), i.e. it fails cl
  +> osed.
R6 evanescent.  Evanescent remainders DO arise in general: Gt structures, and (4-d) x pole terms after contrac
  +> tion.
   They are kept and never dropped.  The p14 statement that none arise is withdrawn.
"""
from __future__ import annotations
import itertools
import json
import sys
import time
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "code" / "classical"))

class PrematureD4Substitution(Exception):
    """d was substituted outside the authorised path (substitute_d), i.e. before the Laurent expansion."""


class NumericTraceForbidden(Exception):
    """a numeric trace of ghat/gtilde (e.g. tr ghat = 4) was requested in an enforced contraction."""


import threading  # noqa: E402

_AUTH = threading.local()
D_PROVENANCE = {}          # every authorised substitution of d: reason -> number of calls


class OpaqueDimension(sp.Symbol):
    """the DRED dimension d: opaque -- subs/xreplace of d raise unless issued by substitute_d (structural R5).
  +> """

    def _xreplace(self, rule):
        if self in rule and rule[self] != self:
            if not getattr(_AUTH, "active", False):
                raise PrematureD4Substitution(f"d -> {rule[self]} outside substitute_d (R5: d is opaque before
  +>  the "
                                              "Laurent expansion)")
            return rule[self], True
        return self, False

    def _subs(self, old, new, **hints):
        if old == self and new != self and not getattr(_AUTH, "active", False):
            raise PrematureD4Substitution(f"d -> {new} via subs outside substitute_d (R5)")
        return super()._subs(old, new, **hints)

    # p16 contract revision (finding F3 of the p15 independent rebuild): expr.replace(d, value) and pattern qu
  +> eries on
    # d go through d.matches; lambdify and the code printers go through the printmethod hooks below.  Both rai
  +> se
    # outside substitute_d.  (Value paths that bypass sympy substitution altogether -- Poly(expr, d).eval(4), 
  +> string
    # round-trips -- cannot be intercepted by the symbol; the static scan, tests/test_p18.py since p18 (p16/p1
  +> 7:
    # tests/test_p16.py, tests/test_p17.py), checks the package code for them: a pattern check, not a proof.)
    def matches(self, expr, repl_dict=None, old=False):
        if not getattr(_AUTH, "active", False):
            raise PrematureD4Substitution("pattern matching on d (expr.replace(d, ...) / expr.match(d)) outsid
  +> e "
                                          "substitute_d (R5)")
        return super().matches(expr, repl_dict, old)

    def _refuse_code(self, printer, *args, **kwargs):
        if not getattr(_AUTH, "active", False):
            raise PrematureD4Substitution("lambdify / code printing of d outside substitute_d (R5: a numerical
  +>  function "
                                          "of d would evaluate it before the Laurent expansion)")
        return printer._print_Symbol(self)

    _lambdacode = _numpycode = _scipycode = _mpmathcode = _pythoncode = _refuse_code
    _cupycode = _jaxcode = _tensorflowcode = _numexprcode = _refuse_code


class PlainDimensionSymbol(ValueError):
    """a plain Symbol('d') (e.g. from sympify of a stored string) where the opaque d is required (p17, G2)."""


def assert_opaque_d(expr, where=""):
    """raise PlainDimensionSymbol if expr contains a symbol named 'd' that is not the opaque d (p17, G2)."""
    bad = [x for x in sp.sympify(expr).free_symbols if x.name == "d" and not isinstance(x, OpaqueDimension)]
    if bad:
        raise PlainDimensionSymbol(f"plain Symbol('d') in {where or 'expression'}: re-parse with dred.parse_d"
  +> )
    return expr


def parse_d(text, extra_locals=None):
    """the guarded loader for stored strings (p17, G2): 'd' parses to the OPAQUE d; a result that still contai
  +> ns a
    plain symbol named d (impossible unless extra_locals shadows it) is refused.  Input format: sympy str() fo
  +> rm only;
    an srepr string (Symbol('d') spelled out) yields a plain d and RAISES PlainDimensionSymbol (H5, p18: fails
    closed; srepr round-trips are not supported)."""
    loc = dict(extra_locals or {})
    if "d" in loc and loc["d"] is not d:
        raise PlainDimensionSymbol("extra_locals must not rebind 'd'")
    loc["d"] = d
    return assert_opaque_d(sp.sympify(text, locals=loc), f"parse_d({str(text)[:40]!r})")


def substitute_d(expr, value, reason):
    """the ONLY authorised substitution of d (recorded with its reason in D_PROVENANCE)."""
    _AUTH.active = True
    try:
        out = sp.sympify(expr).xreplace({d: sp.sympify(value)})
    finally:
        _AUTH.active = False
    D_PROVENANCE[reason] = D_PROVENANCE.get(reason, 0) + 1
    return out


d = OpaqueDimension("d")


# ======================================================================================= p22 CONTRACT REVISIO
  +> N: runtime d guard
# (finding d_guard_power_base_hole + scan_misses_p21 of the p21 independent rebuild).  p21 relied on hooks of 
  +> the symbol
# itself (_xreplace/_subs/matches/printers); sympy reaches values of d without calling them (Pow._eval_subs on
  +>  a power
# base, Basic.xreplace's top-level rule lookup on a bare d, Poly.eval, Expr.coeff reconstruction, evalf(subs))
  +> .  p22 guards
# the ENTRY POINTS instead, installed once at import of dred (every package module imports dred):
#   * Basic.subs / Basic.xreplace / Basic.replace / evalf(subs=..) whose rule has a key containing d;
#   * Poly.eval / __call__ / as_expr(values) and every Poly coefficient accessor (all_coeffs, coeffs, terms, a
  +> ll_terms,
#     as_dict, as_list, coeff_monomial, nth, LC, TC, EC) when d is a generator;
#   * Expr.coeff / as_independent / as_coeff_exponent / series / collect when the target contains d;
#   * d == d (an equality test against d) -- the hook of hand-written e.args rebuilds.
# Rule: from code OUTSIDE sympy/mpmath (package, tests, user code) every such call raises PrematureD4Substitut
  +> ion unless
# issued through substitute_d / authorised_d (recorded in D_PROVENANCE).  From INSIDE sympy (cancel, factor, s
  +> olve,
# Lambda.__call__, Subs.doit, limit ...) polynomial algebra over d is allowed, but a substitution of d by anyt
  +> hing that is
# not a bare symbol (a rename to a Dummy) raises -- so Lambda(d, e)(4), Subs(e, d, 4).doit(), limit(e, d, 4) a
  +> ll raise.
# Irreducible residue (disclosed; the static allow-list scan remains as the SECONDARY barrier): identity / nam
  +> e / type
# tests (`x is d`, x.name == 'd', isinstance) in hand-written tree rebuilds, string round-trips (str(e).replac
  +> e),
# low-level polynomial representations (Poly.rep, DMP, polyutils dict builders), and code that disguises its m
  +> odule name
# as sympy.  These are code-review matters, not runtime-interceptable without breaking sympy itself.
import sys as _sys  # noqa: E402
import contextlib as _contextlib  # noqa: E402
from sympy.core.basic import Basic as _Basic  # noqa: E402
from sympy.core.expr import Expr as _Expr  # noqa: E402
from sympy.core.evalf import EvalfMixin as _EvalfMixin  # noqa: E402
from sympy.polys.polytools import Poly as _Poly  # noqa: E402

GUARD_REVISION = "p22"
GUARDED_ENTRY_POINTS = []


def _internal(depth):
    """True iff the frame `depth` levels above the caller of the wrapper belongs to sympy/mpmath (or to dred i
  +> tself)."""
    try:
        f = _sys._getframe(depth + 1)
    except ValueError:
        return False
    mod = f.f_globals.get("__name__", "") or ""
    return mod.startswith(("sympy.", "mpmath.")) or mod in ("sympy", "mpmath") or mod == __name__


def _has_d(x):
    if x is d or isinstance(x, OpaqueDimension):     # any OpaqueDimension instance (e.g. Symbol.__new__ cache
  +>  miss)
        return True
    if isinstance(x, _Basic) and not x.is_Atom:
        return x.has(d) or bool(x.atoms(OpaqueDimension))
    return False


def _deny(what):
    raise PrematureD4Substitution(f"{what} outside substitute_d (R5, p22 runtime guard: d is opaque before the
  +>  "
                                  "Laurent expansion)")


def _check_rule(pairs, what, depth=2):
    if getattr(_AUTH, "active", False):
        return
    for old, new in pairs:
        if _has_d(old):
            if not _internal(depth):
                _deny(f"{what} of {old} (caller outside sympy)")
            nb = new if isinstance(new, _Basic) else sp.sympify(new, strict=False) if isinstance(new, (int, fl
  +> oat)) else new
            if not (isinstance(nb, _Basic) and (nb.is_Symbol or _has_d(nb))):
                _deny(f"{what}: {old} -> {new} inside sympy (d-free value)")


def _pairs_of_subs(args, kwargs):
    if len(args) == 2:
        return [(args[0], args[1])]
    if len(args) == 1:
        seq = args[0]
        if isinstance(seq, dict):
            return list(seq.items())
        try:
            return [tuple(x) for x in seq]
        except TypeError:
            return []
    return []


_DEFER = threading.local()          # nested-check suspension while a deferred original call runs


def _deferred(check, call):
    """Guard ordering (p22): if the rule is violated, run the ORIGINAL call first with nested guard checks sus
  +> pended,
    so a pre-existing (p14..p18) hook that raises keeps its own message; if the original call does not raise, 
  +> the
    guard raises afterwards.  Either way a violating call raises PrematureD4Substitution (the calls are pure).
  +> """
    if getattr(_DEFER, "on", False):
        return call()
    try:
        check()
    except PrematureD4Substitution as err:
        _DEFER.on = True
        try:
            call()
        except PrematureD4Substitution:
            raise
        except Exception:
            pass
        finally:
            _DEFER.on = False
        raise err
    return call()


def _install():
    o_subs, o_xrep, o_repl, o_evalf = _Basic.subs, _Basic.xreplace, _Basic.replace, _EvalfMixin.evalf

    def subs(self, *args, **kwargs):
        if getattr(_AUTH, "active", False):
            return o_subs(self, *args, **kwargs)
        return _deferred(lambda: _check_rule(_pairs_of_subs(args, kwargs), "subs", 4),
                         lambda: o_subs(self, *args, **kwargs))

    def xreplace(self, rule, *a, **k):
        if not getattr(_AUTH, "active", False) and isinstance(rule, dict) and rule:
            if d in rule or any(_has_d(key) for key in rule if not getattr(key, "is_Atom", True)):
                return _deferred(lambda: _check_rule(rule.items(), "xreplace", 4),
                                 lambda: o_xrep(self, rule, *a, **k))
        return o_xrep(self, rule, *a, **k)

    def replace(self, query, value, *a, **k):
        if not getattr(_AUTH, "active", False) and isinstance(query, _Basic) and _has_d(query):
            return _deferred(lambda: _deny(f"replace({query}, ...)"), lambda: o_repl(self, query, value, *a, *
  +> *k))
        return o_repl(self, query, value, *a, **k)

    def evalf(self, n=15, subs=None, *a, **k):
        if subs and not getattr(_AUTH, "active", False):
            return _deferred(lambda: _check_rule(subs.items(), "evalf(subs=...)", 4),
                             lambda: o_evalf(self, n, subs, *a, **k))
        return o_evalf(self, n, subs, *a, **k)

    _Basic.subs, _Basic.xreplace, _Basic.replace = subs, xreplace, replace
    from sympy.core.basic import Atom as _Atom
    o_axrep = _Atom.xreplace

    def atom_xreplace(self, rule, *a, **k):
        if self is d and not getattr(_AUTH, "active", False) and isinstance(rule, dict) and d in rule:
            return _deferred(lambda: _check_rule([(d, rule[d])], "xreplace on d", 4),
                             lambda: o_axrep(self, rule, *a, **k))
        return o_axrep(self, rule, *a, **k)
    _Atom.xreplace = atom_xreplace
    GUARDED_ENTRY_POINTS.append("Atom.xreplace (bare d)")
    _EvalfMixin.evalf = evalf
    _EvalfMixin.n = evalf
    GUARDED_ENTRY_POINTS.extend(["Basic.subs", "Basic.xreplace", "Basic.replace", "evalf/n(subs=...)"])

    def poly_guard(name, value_args=False):
        orig = getattr(_Poly, name)

        def w(self, *args, **kwargs):
            if not getattr(_AUTH, "active", False) and d in self.gens and (not value_args or args or kwargs):
                if not _internal(1):
                    _deny(f"Poly.{name} with d as a generator (caller outside sympy)")
                if name in ("eval", "__call__"):
                    _deny(f"Poly.{name} with d as a generator inside sympy")
            return orig(self, *args, **kwargs)
        w.__name__ = name
        setattr(_Poly, name, w)
        GUARDED_ENTRY_POINTS.append(f"Poly.{name}")
    for nm in ("eval", "__call__", "all_coeffs", "coeffs", "terms", "all_terms", "as_dict", "as_list",
               "coeff_monomial", "nth", "LC", "TC", "EC"):
        poly_guard(nm)
    poly_guard("as_expr", value_args=True)

    def expr_guard(name, pick):
        orig = getattr(_Expr, name)

        def w(self, *args, **kwargs):
            if not getattr(_AUTH, "active", False) and any(_has_d(x) for x in pick(args, kwargs)) and not _int
  +> ernal(1):
                _deny(f"Expr.{name} targeting d (caller outside sympy)")
            return orig(self, *args, **kwargs)
        w.__name__ = name
        setattr(_Expr, name, w)
        GUARDED_ENTRY_POINTS.append(f"Expr.{name}")
    expr_guard("coeff", lambda a, k: a[:1] + tuple(k.get(x) for x in ("x",) if x in k))
    expr_guard("as_independent", lambda a, k: a)
    expr_guard("as_coeff_exponent", lambda a, k: a[:1])
    expr_guard("series", lambda a, k: a[:1] + tuple(k.get(x) for x in ("x",) if x in k))

    import importlib
    import sympy as _sp
    _rad = importlib.import_module("sympy.simplify.radsimp")
    _simp = importlib.import_module("sympy.simplify")
    o_collect = _rad.collect

    def collect(expr, syms, *a, **k):
        ss = syms if isinstance(syms, (list, tuple, set)) else [syms]
        if not getattr(_AUTH, "active", False) and any(_has_d(_sp.sympify(x)) for x in ss) and not _internal(1
  +> ):
            _deny("collect(.., d) (caller outside sympy)")
        return o_collect(expr, syms, *a, **k)
    _rad.collect = _simp.collect = _sp.collect = collect
    GUARDED_ENTRY_POINTS.append("collect")
    _lim = importlib.import_module("sympy.series.limits")
    o_limit = _lim.limit

    def limit(e, z, z0, *a, **k):
        if not getattr(_AUTH, "active", False) and _has_d(_sp.sympify(z)) and not _internal(1):
            _deny("limit in d (caller outside sympy)")
        return o_limit(e, z, z0, *a, **k)
    _lim.limit = _sp.limit = limit
    from sympy.core.function import Lambda as _Lambda
    o_lnew = _Lambda.__new__

    def lambda_new(cls, signature, expr, *a, **k):
        sig = signature if isinstance(signature, (tuple, list)) else (signature,)
        if not getattr(_AUTH, "active", False) and any(_has_d(_sp.sympify(v)) for v in sig if isinstance(v, _B
  +> asic)) \
                and not _internal(1):
            _deny("Lambda with d as a bound variable (caller outside sympy)")
        return o_lnew(cls, signature, expr, *a, **k)
    _Lambda.__new__ = lambda_new
    GUARDED_ENTRY_POINTS.extend(["limit", "Lambda(d, ...)"])


def _d_eq(self, other):
    if other is self and not getattr(_AUTH, "active", False) and not _internal(1):
        _deny("equality test against d (hand-written expression-tree rebuild)")
    return _sp_Symbol_eq(self, other)


_sp_Symbol_eq = sp.Symbol.__eq__
OpaqueDimension.__eq__ = _d_eq
OpaqueDimension.__hash__ = sp.Symbol.__hash__
GUARDED_ENTRY_POINTS.append("OpaqueDimension.__eq__ (d == d)")
if not getattr(_Basic.subs, "_xvi_p22", False):
    _install()
    _Basic.subs._xvi_p22 = True


@_contextlib.contextmanager
def authorised_d(reason):
    """p22: the only other authorised access to d's value paths (recorded in D_PROVENANCE like substitute_d)."
  +> ""
    prev = getattr(_AUTH, "active", False)
    _AUTH.active = True
    try:
        yield
    finally:
        _AUTH.active = prev
    D_PROVENANCE[reason] = D_PROVENANCE.get(reason, 0) + 1
# ======================================================================================= end p22 runtime d gu
  +> ard
eps = sp.Symbol("epsilon")
ETA = (1, -1, -1, -1)
VSPACE = {"l": "h", "p": "h"}          # R2: loop and external momenta in QdS


class UncontractedObjects(Exception):
    """a Laurent expansion was requested on an expression that still carries open index objects (Gt_rs, e-vect
  +> ors)."""


class Rules:
    """trace rules; trace_hat is overridable ONLY for the mutation test (tr ghat = 4 must be rejected)."""

    def __init__(self, trace_hat=None, display_only=False):
        th = d if trace_hat is None else sp.sympify(trace_hat)
        self.trace = {"4": sp.Integer(4), "h": th, "t": sp.Integer(4) - th}
        self.mutated = trace_hat is not None
        self.display_only = bool(display_only)        # p15: a numeric trace may only be used to DISPLAY a mut
  +> ation

    def enforce_symbolic(self):
        if self.trace["h"] != d and not self.display_only:
            raise NumericTraceForbidden(f"tr ghat = {self.trace['h']} (must be the opaque d; R1/R5)")

    def check(self):
        tr = self.trace
        res = {"tr_g4_is_4": tr["4"] == 4,
               "tr_ghat_is_symbolic_d": tr["h"] == d,
               "tr_ghat_plus_tr_gtilde_is_4": sp.simplify(tr["h"] + tr["t"] - 4) == 0,
               "tr_gtilde_is_4_minus_d_nonzero": sp.simplify(tr["t"] - (4 - d)) == 0 and tr["t"] != 0}
        res["pass"] = all(res.values())
        return res


# ---------------------------------------------------------------- vectors, metrics, contraction engine
def vspace(name):
    if name.endswith("^"):
        return "h"
    if name.endswith("~"):
        return "t"
    return VSPACE.get(name, "4")


def project(kind, name):
    s = vspace(name)
    if kind == "4" or kind == s:
        return name
    if s == "4":
        return name + ("^" if kind == "h" else "~")
    return None                                           # orthogonal subspaces


def mcomb(k1, k2):
    if k1 == "4":
        return k2
    if k2 == "4":
        return k1
    return k1 if k1 == k2 else None


def dot(a, b):
    sa, sb = vspace(a), vspace(b)
    if {sa, sb} == {"h", "t"}:
        return sp.Integer(0)
    if sa == "4" and sb != "4":
        a = project(sb, a)
    if sb == "4" and sa != "4":
        b = project(sa, b)
    x, y = sorted([a, b])
    return sp.Symbol(f"{x}.{y}")


def _canon(facs):
    out = []
    for f in facs:
        if f[0] == "g":
            i, j = sorted((f[2], f[3]))
            out.append(("g", f[1], i, j))
        else:
            out.append(f)
    return tuple(sorted(out))


def contract_term(coeff, facs, rules):
    """facs: ('g', kind, i, j) | ('v', name, i).  Repeated indices are contracted with R1/R2."""
    facs = list(facs)
    while True:
        occ = {}
        for fi, f in enumerate(facs):
            for ix in (f[2:] if f[0] == "g" else (f[2],)):
                occ.setdefault(ix, []).append(fi)
        rep = next(((ix, fl) for ix, fl in occ.items() if len(fl) >= 2), None)
        if rep is None:
            return coeff, _canon(facs)
        ix, fl = rep
        assert len(fl) == 2, f"index {ix} occurs more than twice"
        a, b = fl
        if a == b:                                        # trace of one metric
            coeff = coeff * rules.trace[facs[a][1]]
            facs.pop(a)
            continue
        fa, fb = facs[a], facs[b]
        if fa[0] == "v" and fb[0] == "g":
            fa, fb = fb, fa
        rest = [f for k, f in enumerate(facs) if k not in (a, b)]
        if fa[0] == "g" and fb[0] == "g":
            kc = mcomb(fa[1], fb[1])
            if kc is None:
                return sp.Integer(0), ()
            o1 = fa[3] if fa[2] == ix else fa[2]
            o2 = fb[3] if fb[2] == ix else fb[2]
            facs = rest + [("g", kc, o1, o2)]
        elif fa[0] == "g":
            nv = project(fa[1], fb[1])
            if nv is None:
                return sp.Integer(0), ()
            o = fa[3] if fa[2] == ix else fa[2]
            facs = rest + [("v", nv, o)]
        else:
            coeff = coeff * dot(fa[1], fb[1])
            facs = rest
        if coeff == 0:
            return sp.Integer(0), ()


def contract(terms, rules):
    rules.enforce_symbolic()
    out = {}
    for c, facs in terms:
        cc, ff = contract_term(c, facs, rules)
        if cc != 0:
            out[ff] = sp.expand(out.get(ff, 0) + cc)
    return {k: v for k, v in out.items() if v != 0}


# ---------------------------------------------------------------- R4 tensor reduction (Gram / PV projection)
def _matchings(items):
    if not items:
        yield []
        return
    a = items[0]
    for k in range(1, len(items)):
        rest = items[1:k] + items[k + 1:]
        for m in _matchings(rest):
            yield [(a, items[k])] + m


def sym_basis(idx, with_p):
    """B_k: symmetric tensors with k ghat's and (n-2k) p's over the free indices idx."""
    n, out = len(idx), []
    for k in range(n // 2 + 1):
        if not with_p and 2 * k != n:
            continue
        terms = []
        for sub in itertools.combinations(idx, 2 * k):
            for m in _matchings(list(sub)):
                rest = [i for i in idx if i not in sub]
                terms.append(tuple(("g", "h", a, b) for a, b in m) + tuple(("v", "p", i) for i in rest))
        out.append({"k": k, "terms": terms})
    return out


def _integral_functional(expr, tag):
    """polynomial in l.l, l.p (coefficients may carry p.p, d) -> sum coeff * J_tag[a,b]   (NOT evaluated)."""
    ll, lp = sp.Symbol("l.l"), sp.Symbol("l.p")
    P = sp.Poly(sp.expand(expr), ll, lp)
    return sp.expand(sum(cf * sp.Symbol(f"J_{tag}[{m[0]},{m[1]}]") for m, cf in P.terms()))


_RED = {}


def reduce_tensor(n, with_p, rules, tag="G"):
    """int l^{mu_1..mu_n} F = sum_k C_k B_k ; returns (basis, C) with C exact rational functions of d, p.p and
  +>  J."""
    key = (n, with_p, str(rules.trace["h"]), tag)
    if key in _RED:
        return _RED[key]
    idx = [f"m{i}" for i in range(n)]
    B = sym_basis(idx, with_p)
    if not B:
        _RED[key] = (B, [])
        return _RED[key]
    G = sp.zeros(len(B), len(B))
    for j, bj in enumerate(B):
        for k, bk in enumerate(B):
            tot = contract([(sp.Integer(1), tj + tk) for tj in bj["terms"] for tk in bk["terms"]], rules)
            G[j, k] = sp.expand(tot.get((), 0))
    R = []
    for bj in B:
        tot = contract([(sp.Integer(1), tj + tuple(("v", "l", i) for i in idx)) for tj in bj["terms"]], rules)
        R.append(_integral_functional(tot.get((), 0), tag))
    Cs = G.LUsolve(sp.Matrix(R))
    Cs = [sp.factor(sp.cancel(c)) for c in Cs]
    _RED[key] = (B, Cs)
    return _RED[key]


# ---------------------------------------------------------------- R3 lifting of component monomials
def Gt(r, s):
    a, b = sorted((r, s))
    return sp.Symbol(f"Gt_{a}{b}")


def _lift_symbols(expr):
    """e_(r)^.e_(s)^ -> eta_rs - Gt_rs ; e_(r)~.e_(s)~ -> Gt_rs ; e_(r)^.p -> p_r (p in QdS) ; e_(r).e_(s) -> 
  +> eta_rs."""
    rep = {}
    for s in expr.free_symbols:
        nm = s.name
        if "." not in nm or not nm.startswith("e"):
            continue
        a, b = nm.split(".")
        if a.startswith("e") and b.startswith("e"):
            r, q = int(a[1]), int(b[1])
            eta = ETA[r] if r == q else 0
            if a.endswith("^") and b.endswith("^"):
                rep[s] = eta - Gt(r, q)
            elif a.endswith("~") and b.endswith("~"):
                rep[s] = Gt(r, q)
            else:
                rep[s] = eta
        elif b == "p" and a.startswith("e"):
            rep[s] = sp.Symbol(f"p{int(a[1])}")
    return sp.expand(expr.xreplace(rep))


_LIFT = {}


def lift_reduce_monomial(comps, with_p, rules, tag):
    """int l_{r1}..l_{rn} F  ->  scalar in eta, Gt_rs, p_r, d, J_tag   (R3 + R4)."""
    key = (tuple(sorted(comps)), with_p, str(rules.trace["h"]), tag)
    if key in _LIFT:
        return _LIFT[key]
    n = len(comps)
    if n == 0:
        _LIFT[key] = sp.Symbol(f"J_{tag}[0,0]")
        return _LIFT[key]
    B, Cs = reduce_tensor(n, with_p, rules, tag)
    idx = [f"m{i}" for i in range(n)]
    ev = tuple(("v", f"e{r}", i) for r, i in zip(comps, idx))
    tot = 0
    for b, c in zip(B, Cs):
        con = contract([(sp.Integer(1), t + ev) for t in b["terms"]], rules)
        tot += c * con.get((), 0)
    _LIFT[key] = _lift_symbols(sp.expand(tot))
    return _LIFT[key]


def lift_reduce_polynomial(poly_rows, with_p, rules, tag):
    """poly_rows: exported canonical rows [[var names...], 'p/q'] in l0..l3, p0..p3."""
    tot = 0
    for names, cf in poly_rows:
        lc = sorted(int(v[1]) for v in names if v.startswith("l"))
        pc = sp.Mul(*[sp.Symbol(v) for v in names if v.startswith("p")])
        tot += sp.Rational(cf) * pc * lift_reduce_monomial(lc, with_p, rules, tag)
    return sp.expand(tot)


def split_evanescent(expr):
    """expr = four_d + evanescent, evanescent = part linear in Gt symbols."""
    gts = [s for s in expr.free_symbols if s.name.startswith("Gt_")]
    ev = sp.expand(expr - expr.xreplace({g: 0 for g in gts}))
    return sp.expand(expr - ev), ev


def eta_trace_Gt(expr, rules):
    """external 4D projection of the evanescent part: an expression c * sum_r eta^{rr} Gt_rr (+ Gt-free terms)
  +>  is
    contracted to c * tr(gtilde) = c * (4 - d) (R4).  Any Gt pattern that is not of this trace form is an open
    index object and is refused."""
    gts = {g for g in expr.free_symbols if g.name.startswith("Gt_")}
    if not gts:
        return expr
    c = None
    for g in gts:
        a, b = int(g.name[3]), int(g.name[4])
        if a != b:
            raise UncontractedObjects([g.name])
        val = sp.expand(sp.expand(expr).coeff(g) / ETA[a])
        if c is None:
            c = val
        elif sp.expand(val - c) != 0:
            raise UncontractedObjects(sorted(x.name for x in gts))
    if len(gts) != 4:
        raise UncontractedObjects(sorted(x.name for x in gts))
    return sp.expand(sp.expand(expr).xreplace({g: 0 for g in gts}) + c * rules.trace["t"])


# ---------------------------------------------------------------- R5 Laurent / MS-bar with guards
class Pipeline:
    """lift -> reduce -> contract (incl. external 4D projection) -> Laurent.  The ledger records whether the
    reduction introduced d; the guards enforce R5."""

    def __init__(self, rules=None, mutation=None, enforce=True):
        self.rules = rules or Rules()
        self.mutation = mutation
        self.enforce = enforce                           # enforce=False only to DISPLAY what a mutation would
  +>  yield
        self.ledger = []
        if enforce:
            self.rules.enforce_symbolic()

    def reduced_component(self, comps, with_p=False, tag="T"):
        v = lift_reduce_monomial(comps, with_p, self.rules, tag)
        if v.has(d):
            self.ledger.append({"step": "reduce", "comps": list(comps), "introduces_d": True})
        if self.mutation == "premature_d4":
            if self.enforce:
                v = v.xreplace({d: 4})                  # MUTATION: d -> 4 before the expansion -> raises (opa
  +> que d)
            else:
                v = substitute_d(v, 4, "mutation display only (enforce=False): premature d = 4")
        return v

    def laurent(self, expr, Jvals, order=0):
        if self.mutation == "contract_after_laurent":
            pass                                         # (the caller hands over an uncontracted expression)
        if any(s.name.startswith(("Gt_", "e")) and s.name != "epsilon" for s in expr.free_symbols):
            raise UncontractedObjects(sorted(s.name for s in expr.free_symbols if s.name.startswith(("Gt_", "e
  +> "))
                                             and s.name != "epsilon"))
        # p15 contract correction: no heuristic test on the shape of expr (it gave a false positive and a fals
  +> e
        # negative, finding F1); R5 is enforced structurally by the opaque d (any earlier substitution has rai
  +> sed)
        if self.enforce:
            self.rules.enforce_symbolic()
        e = sp.expand(substitute_d(expr.xreplace(Jvals), 4 - 2 * eps, "Pipeline.laurent: d = 4 - 2 eps"))
        ser = sp.series(e, eps, 0, order + 1).removeO()
        pole = sp.expand(sum(ser.coeff(eps, -k) * eps ** (-k) for k in (1, 2)))
        fin = sp.expand(ser.coeff(eps, 0))
        return {"pole": pole, "finite": fin, "ms_bar_subtracted": fin, "pre_laurent": expr}


# ---------------------------------------------------------------- toy checks (generic placeholders; no integr
  +> al evaluated)
A_, B_, C_ = sp.symbols("a b c")
JTOY = {sp.Symbol("J_T[1,0]"): A_ / eps + B_ + C_ * eps}


def toy_four_d_part(rules=None, mutation=None, enforce=True):
    """T1: 4D (eta_00) coefficient of int l_0 l_0 F(l^2) = (1/d) J[1,0]."""
    P = Pipeline(rules, mutation, enforce)
    v = P.reduced_component([0, 0], with_p=False, tag="T")
    four, _ = split_evanescent(v)
    return P.laurent(four, JTOY)


def toy_evanescent_trace(rules=None, mutation=None, enforce=True):
    """T2: eta^{rs} x [Gt-part of int l_r l_s F]  =  -(4-d)/d J[1,0]: a (d-4) x pole term with finite part -a/
  +> 2."""
    P = Pipeline(rules, mutation, enforce)
    tot = sp.expand(sum(ETA[r] * split_evanescent(P.reduced_component([r, r], with_p=False, tag="T"))[1]
                        for r in range(4)))
    if mutation != "contract_after_laurent":          # MUTATION: skip the contraction and expand first
        tot = eta_trace_Gt(tot, P.rules)
    return P.laurent(tot, JTOY)


def toy_reference():
    """hand-derived values (d = 4 - 2 eps, J = a/eps + b + c eps)."""
    return {"T1_finite": sp.expand(B_ / 4 + A_ / 8), "T1_pole": sp.expand(A_ / (4 * eps)),
            "T2_finite": sp.expand(-A_ / 2), "T2_pole": sp.Integer(0)}


def known_reductions(rules):
    """closed forms: rank-2 / rank-4 tadpoles and the rank-2 two-point PV coefficients."""
    out = {}
    B, C = reduce_tensor(2, False, rules, "X")
    out["rank2_tadpole_eq_ghat_over_d"] = sp.simplify(C[0] - sp.Symbol("J_X[1,0]") / d) == 0
    B, C = reduce_tensor(4, False, rules, "X")
    out["rank4_tadpole_eq_sym_ghatghat_over_d_dplus2"] = sp.simplify(C[0] - sp.Symbol("J_X[2,0]") / (d * (d + 
  +> 2))) == 0
    B, C = reduce_tensor(2, True, rules, "Y")
    pp = sp.Symbol("p.p")
    J10, J02 = sp.Symbol("J_Y[1,0]"), sp.Symbol("J_Y[0,2]")
    c_g = [c for b, c in zip(B, C) if b["k"] == 1][0]
    c_pp = [c for b, c in zip(B, C) if b["k"] == 0][0]
    out["rank2_two_point_B00"] = sp.simplify(c_g - (J10 * pp - J02) / ((d - 1) * pp)) == 0
    out["rank2_two_point_B11"] = sp.simplify(c_pp - (d * J02 - pp * J10) / ((d - 1) * pp ** 2)) == 0
    out["pass"] = all(out.values())
    return out


def reviewer_toys():
    """p15 regression toys from the p14r independent rebuild (finding F1/F2).
    eta-trace toy: eta^{rs} int l_r l_s/(l^2 - m^2) = eta^{rs} ghat_rs J/d = J, J = m^2 A0, A0 = m^2(1/eps + a
  +> 1 + a2 eps).
      correct -> no exception, finite a1 m^4 (p14r heuristic: FALSE POSITIVE);
      premature_d4 (enforced) -> PrematureD4Substitution (p14r heuristic: FALSE NEGATIVE, finite m^4 (a1 - 1/2
  +> )).
    A0 mixing toy: reduce with tr ghat = d, contract with tr ghat = 4: refused (NumericTraceForbidden); forced
  +>  display
      gives the +m^4/2 finite shift.
    B0 mixing toy: ghat_{mu nu} int l^mu l^nu/(l^2 (l-p)^2) = d B00 + p^2 B11 = J[1,0] = 0 (scaleless); mixing
      (contract with 4): (4-d) B00 -> forced display gives the -p^2/6 finite shift."""
    m, a1, a2, p2, b1, b2 = sp.symbols("m a1 a2 p2 b1 b2")
    A0 = m ** 2 * (1 / eps + a1 + a2 * eps)
    B0 = 1 / eps + b1 + b2 * eps
    out = {}

    def eta_toy(mutation, enforce=True):
        _RED.clear()
        _LIFT.clear()
        P = Pipeline(Rules(), mutation, enforce)
        tot = sp.expand(sum(ETA[r] * P.reduced_component([r, r], with_p=False, tag="RT") for r in range(4)))
        tot = eta_trace_Gt(tot, P.rules)
        return P.laurent(tot, {sp.Symbol("J_RT[1,0]"): m ** 2 * A0})
    good = eta_toy(None)
    out["eta_trace_correct"] = {"finite": str(sp.simplify(good["finite"])), "raised": False,
                                "ok": sp.simplify(good["finite"] - a1 * m ** 4) == 0}
    try:
        eta_toy("premature_d4")
        out["eta_trace_premature_d4"] = {"raised": False, "ok": False}
    except PrematureD4Substitution as exc:
        disp = eta_toy("premature_d4", enforce=False)
        out["eta_trace_premature_d4"] = {"raised": True, "reason": str(exc),
                                         "finite_if_forced": str(sp.simplify(disp["finite"])),
                                         "ok": sp.simplify(disp["finite"] - m ** 4 * (a1 - sp.Rational(1, 2)))
  +>  == 0}

    def ghat_contract(red_rules, con_rules, with_p, tag):
        B, C = reduce_tensor(2, with_p, red_rules, tag)
        tot = 0
        for b, c in zip(B, C):
            con = contract([(sp.Integer(1), t + (("g", "h", "m0", "m1"),)) for t in b["terms"]], con_rules)
            tot += c * con.get((), 0)
        return sp.expand(tot)
    for lab, with_p, J, target_shift in (
            ("A0", False, {sp.Symbol("J_RA[1,0]"): m ** 2 * A0}, m ** 4 / 2),
            ("B0", True, {sp.Symbol("J_RB[1,0]"): sp.Integer(0), sp.Symbol("J_RB[0,2]"): p2 ** 2 * B0 / 4},
             -p2 / 6)):
        tag = "RA" if lab == "A0" else "RB"
        _RED.clear()
        _LIFT.clear()
        e = ghat_contract(Rules(), Rules(), with_p, tag).xreplace({sp.Symbol("p.p"): p2})
        fin = sp.simplify(Pipeline(Rules()).laurent(e, J)["finite"])
        try:
            ghat_contract(Rules(), Rules(trace_hat=4), with_p, tag)
            refused = False
        except NumericTraceForbidden:
            refused = True
        _RED.clear()
        _LIFT.clear()
        em = ghat_contract(Rules(), Rules(trace_hat=4, display_only=True), with_p, tag).xreplace({sp.Symbol("p
  +> .p"): p2})
        finm = sp.simplify(Pipeline(Rules(), enforce=False).laurent(em, J)["finite"])
        _RED.clear()
        _LIFT.clear()
        correct = a1 * m ** 4 if lab == "A0" else sp.Integer(0)
        out[f"{lab}_mixing"] = {"correct_finite": str(fin), "mixed_refused": refused,
                                "finite_if_forced": str(finm), "shift": str(sp.simplify(finm - fin)),
                                "ok": refused and sp.simplify(fin - correct) == 0
                                and sp.simplify(finm - fin - target_shift) == 0}
    out["pass"] = all(v["ok"] for v in out.values())
    return out


def lift_exported(graphs=("D01", "D02", "D03", "D11", "D12", "D13", "D14a", "D14b", "D14c")):
    """R3+R4 on the exported integrands (tadpole topologies: with_p only for the p-dependent numerators).
    Returns per graph: components lifted, max l-rank, components with a nonzero evanescent (Gt) part."""
    rules = Rules()
    out = {}
    for g in graphs:
        f = ROOT / "exports" / "P14_integrands" / f"{g}.json"
        if not f.is_file():
            out[g] = {"present": False}
            continue
        body = json.loads(f.read_text())
        with_p = len(body["denominators"]) > 1           # two-point: tensor basis includes p
        n_ev, n_c, rank = 0, 0, 0
        for comp, rows in body["numerator"].items():
            rank = max(rank, max((sum(1 for v in r[0] if v.startswith("l")) for r in rows), default=0))
            v = lift_reduce_polynomial(rows, with_p, rules, g)
            _, ev = split_evanescent(v)
            n_c += 1
            n_ev += ev != 0
        out[g] = {"present": True, "components": n_c, "max_l_rank": rank, "components_with_evanescent_part": n
  +> _ev,
                  "scalar_integrals": "J_" + g + "[a,b] symbols (NOT evaluated)"}
    return out


def main():
    t0 = time.time()
    rules = Rules()
    rc = rules.check()
    kr = known_reductions(rules)
    ref = toy_reference()
    t1, t2 = toy_four_d_part(), toy_evanescent_trace()
    toys = {"T1_four_d_part": {"finite": str(t1["finite"]), "pole": str(t1["pole"]),
                               "equals_reference": sp.expand(t1["finite"] - ref["T1_finite"]) == 0
                               and sp.expand(t1["pole"] - ref["T1_pole"]) == 0},
            "T2_evanescent_trace": {"finite": str(t2["finite"]), "pole": str(t2["pole"]),
                                    "equals_reference": sp.expand(t2["finite"] - ref["T2_finite"]) == 0
                                    and sp.expand(t2["pole"] - ref["T2_pole"]) == 0,
                                    "pre_laurent": str(t2["pre_laurent"]),
                                    "is_d_minus_4_times_pole": sp.simplify(
                                        t2["pre_laurent"] + (4 - d) / d * sp.Symbol("J_T[1,0]")) == 0}}
    # premature d=4 changes the finite part of T1 (a/8 lost); the guard must raise
    naive = toy_four_d_part(mutation="premature_d4", enforce=False)["finite"]   # what d=4-first would give
    muts = {}
    try:
        toy_four_d_part(mutation="premature_d4")
        muts["premature_d4"] = {"rejected": False}
    except PrematureD4Substitution as exc:
        muts["premature_d4"] = {"rejected": True, "reason": f"PrematureD4Substitution: {exc}",
                                "finite_part_if_not_caught": str(sp.expand(naive)),
                                "finite_part_differs": sp.expand(naive - ref["T1_finite"]) != 0}
    mr = Rules(trace_hat=4)
    try:                                                 # p15: structural refusal of a numeric trace
        toy_four_d_part(rules=mr)
        structural = False
    except NumericTraceForbidden:
        structural = True
    md = Rules(trace_hat=4, display_only=True)
    _RED.clear()
    _LIFT.clear()
    m1, m2 = toy_four_d_part(rules=md, enforce=False), toy_evanescent_trace(rules=md, enforce=False)
    _RED.clear()
    _LIFT.clear()
    muts["trace_ghat_eq_4"] = {"rules_check": mr.check(), "structurally_refused": structural,
                               "T1_finite": str(m1["finite"]), "T2_finite": str(m2["finite"]),
                               "rejected": structural and (not mr.check()["pass"]) and (
                                   sp.expand(m1["finite"] - ref["T1_finite"]) != 0
                                   or sp.expand(m2["finite"] - ref["T2_finite"]) != 0)}
    try:
        toy_evanescent_trace(mutation="contract_after_laurent")
        muts["contract_after_laurent"] = {"rejected": False}
    except UncontractedObjects as exc:
        muts["contract_after_laurent"] = {"rejected": True, "reason": f"UncontractedObjects: {exc}"}
    reviewer = reviewer_toys()
    lifts = lift_exported()
    ev_any = any(v.get("components_with_evanescent_part", 0) for v in lifts.values())
    verified = bool(rc["pass"] and kr["pass"] and all(t["equals_reference"] for t in toys.values())
                    and toys["T2_evanescent_trace"]["is_d_minus_4_times_pole"]
                    and all(m["rejected"] for m in muts.values()) and all(v.get("present") for v in lifts.valu
  +> es())
                    and reviewer["pass"])
    import p14_conventions as PC
    import certio
    rec = {"landmark": "XVI-P", "revision": PC.REVISION, "deliverable": "P.5 entry: operational DRED rules (ex
  +> ecutable)",
           "dred_rules_verified": verified,
           "rules": {"R1_spaces": "Q4S = QdS (+) Q(4-d)S; g4 = ghat + gtilde; tr g4 = 4, tr ghat = d, tr gtild
  +> e = 4-d; "
                                  "ghat.ghat = ghat, gtilde.gtilde = gtilde, ghat.gtilde = 0, g4.X = X",
                     "R2_momenta": "loop momentum l in QdS; external momenta p in QdS (p.gtilde = 0, stated ch
  +> oice); "
                                   "field/vertex/polarisation indices in Q4S",
                     "R3_lifting": "exported lower components l_r = l.e_(r) = l.ehat_(r), p_r = p.e_(r), e_(r)
  +>  the "
                                   "eta-orthonormal basis of Q4S; vertex tensors lifted with eta -> g4",
                     "R4_reduction": "Gram/PV projection on symmetric ghat/p tensors with symbolic d; "
                                     "ghat_rs = eta_rs - Gt_rs, eta^{rs} Gt_rs = 4-d, Gt_rs p^s = 0",
                     "R5_order": "all contractions (incl. external 4D projection) BEFORE the Laurent expansion
  +> ; d kept "
                                 "symbolic through MS-bar subtraction and finite-part extraction; (d-4) x pole
  +>  retained",
                     "R6_evanescent": "evanescent remainders arise in general and are retained (Gt structures;
  +>  "
                                      "(4-d) x pole finite terms); the p14 'none arise' statement is withdrawn
  +> "},
           "literature_background_only": ["W. Siegel, Phys. Lett. B84 (1979) 193", "W. Siegel, Phys. Lett. B94
  +>  (1980) 37",
                                          "D. Stockinger, JHEP 0503 (2005) 076, hep-ph/0503129",
                                          "A. Signer, D. Stockinger, Nucl. Phys. B808 (2009) 88, arXiv:0807.44
  +> 24"],
           "trace_rules_check": rc, "known_reductions": kr,
           "toy_checks": {"placeholders": "J = a/eps + b + c eps (generic symbols; not a loop value); d = 4 - 
  +> 2 eps",
                          **toys, "reference": {k: str(v) for k, v in ref.items()}},
           "mutations": muts, "mutations_all_rejected": all(m["rejected"] for m in muts.values()),
           "lift_of_exported_integrands": lifts, "evanescent_parts_present_in_exports": ev_any,
           "p15_contract_correction": {
               "finding": "F1_premature_d4_guard_heuristic (reproducibility/independent_rebuild_report_p14r.js
  +> on)",
               "old_safeguard": "heuristic: raise iff the reduction introduced d and d is absent before the La
  +> urent "
                                "expansion (false positive and false negative on the reviewer's eta-trace toy)
  +> ",
               "new_safeguard": "structural/provenance: OpaqueDimension d (subs/xreplace raise outside substit
  +> ute_d); "
                                "substitute_d records every authorised substitution; numeric traces of ghat/gt
  +> ilde "
                                "refused (NumericTraceForbidden) unless display_only",
               "released_p14r_values_affected": False,
               "why_unaffected": "in p14r Pipeline.laurent was applied only to the toy placeholders; no loop i
  +> ntegral "
                                 "was evaluated",
               "regression_toys": reviewer},
           "loop_evaluations_performed": False, "seconds": round(time.time() - t0, 1)}
    certio.write(ROOT / "certificates" / f"{PC.CERT_PREFIX}_dred_rules.json", rec)
    print(json.dumps({"dred_rules_verified": verified, "trace": rc["pass"], "known": kr, "toys": toys,
                      "mutations": {k: v["rejected"] for k, v in muts.items()}, "lifts": lifts,
                      "seconds": rec["seconds"]}, indent=1, default=str))
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())


# ======================================================================================= p23 CONTRACT REVISIO
  +> N: polynomial-domain refusal
# p23 (disclosed; reviewer p22 runtime_guard_bypass_poly_algebra): (1) internal sympy renames of d are admitte
  +> d only to a
# Dummy (or to an expression still containing d) -- a rename to a PLAIN symbol (Matrix.subs({d: y}) then y -> 
  +> 4) raises;
# (2) public polynomial algebra that can evaluate d (rem/prem/div/quo/resultant/discriminant/compose/decompose
  +> /shift/
# gcdex/invert/subresultants/sturm/root isolation) refuses d as a generator or domain symbol when called from 
  +> outside
# sympy.  Rational-function normalisation (cancel/factor/together/apart/simplify/expand) is unaffected.
def _check_rule(pairs, what, depth=2):            # p23: overrides the p22 rule (module global, looked up at c
  +> all time)
    if getattr(_AUTH, "active", False):
        return
    for old, new in pairs:
        if _has_d(old):
            if not _internal(depth):
                _deny(f"{what} of {old} (caller outside sympy)")
            nb = new if isinstance(new, _Basic) else sp.sympify(new, strict=False) if isinstance(new, (int, fl
  +> oat)) else new
            if not (isinstance(nb, _Basic) and (isinstance(nb, sp.Dummy) or _has_d(nb))):
                _deny(f"{what}: {old} -> {new} inside sympy (only a Dummy rename or a d-containing value is ad
  +> mitted)")


_POLY_DENY = ("rem", "prem", "pdiv", "pquo", "pexquo", "div", "quo", "exquo", "gcdex", "half_gcdex", "invert",
              "subresultants", "resultant", "discriminant", "compose", "decompose", "sturm", "nroots", "real_r
  +> oots",
              "count_roots", "ground_roots", "intervals", "refine_root", "nth_power_roots_poly")
_POLY_METHOD_DENY = _POLY_DENY + ("shift", "transform", "shift_list")


def _install_poly_refusal():
    import sympy as _sympy
    import sympy.polys.polytools as _pt

    def _args_have_d(args, kwargs):
        return any(_has_d(a) or (isinstance(a, _pt.Poly) and (d in a.gens or a.free_symbols_in_domain & {d}))
                   for a in list(args) + list(kwargs.values()))

    for name in _POLY_DENY:
        orig = getattr(_pt, name, None)
        if orig is None:
            continue

        def w(*args, _orig=orig, _name=name, **kwargs):
            if not getattr(_AUTH, "active", False) and not _internal(1) and _args_have_d(args, kwargs):
                _deny(f"{_name}(...) with d in the polynomial domain")
            return _orig(*args, **kwargs)
        w.__name__ = name
        setattr(_pt, name, w)
        if getattr(_sympy, name, None) is orig:
            setattr(_sympy, name, w)
        GUARDED_ENTRY_POINTS.append(f"polytools.{name} (d in domain)")
    for name in _POLY_METHOD_DENY:
        orig = getattr(_pt.Poly, name, None)
        if orig is None:
            continue

        def m(self, *args, _orig=orig, _name=name, **kwargs):
            if (not getattr(_AUTH, "active", False) and not _internal(1)
                    and (d in self.gens or d in self.free_symbols_in_domain or _args_have_d(args, kwargs))):
                _deny(f"Poly.{_name}(...) with d in the polynomial domain")
            return _orig(self, *args, **kwargs)
        m.__name__ = name
        setattr(_pt.Poly, name, m)
        GUARDED_ENTRY_POINTS.append(f"Poly.{name} (d in domain)")
    GUARDED_ENTRY_POINTS.append("internal rename of d to a plain Symbol (Matrix.subs)")


_install_poly_refusal()
# ======================================================================================= end p23 polynomial-d
  +> omain refusal
