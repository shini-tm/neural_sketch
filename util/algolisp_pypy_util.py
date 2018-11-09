#pypy_util.py


import time
from program import ParseFailure, Context
from grammar import NoCandidates, Grammar
from utilities import timing, callCompiled
from collections import namedtuple
from itertools import islice, zip_longest
from functools import reduce

from program_synthesis.algolisp.dataset import executor

SketchTup = namedtuple("SketchTup", ['sketch', 'g'])
AlgolispResult = namedtuple("AlgolispResult", ["sketch", "prog", "hit", "n_checked", "time"])


#from algolisp code
executor_ = executor.LispExecutor()

# #for reference:
# def get_stats_from_code(args):
#     res, example, executor_ = args
#     if len(example.tests) == 0:
#         return None
#     if executor_ is not None:
#         stats = executor.evaluate_code(
#             res.code_tree if res.code_tree else res.code_sequence, example.schema.args, example.tests,
#             executor_)
#         stats['exact-code-match'] = is_same_code(example, res)
#         stats['correct-program'] = int(stats['tests-executed'] == stats['tests-passed'])
#     else: assert False
# #what is a res?


def test_program_on_IO(e, IO, schema_args):
	"""
	run executor
	"""
	stats = executor.evaluate_code(
		e, schema_args, IO,
		executor_)

	return stats['tests-executed'] == stats['tests-passed']

def alternate(*args):
	# note: python 2 - use izip_longest
	for iterable in zip_longest(*args):
		for item in iterable:
			if item is not None:
				yield item

def algolisp_enumerate(tp, IO, schema_args, mdl, sketchtups, n_checked, n_hit, t, max_to_check):
	results = []
	for sketch, x in alternate(*(((sk.sketch, x) for x in sk.g.sketchEnumeration(Context.EMPTY, [], tp, sk.sketch, mdl)) for sk in sketchtups)):
		_, _, p = x
		e = p.evaluate([])
		hit = test_program_on_IO(e, IO, schema_args)
		prog = p if hit else None
		n_checked += 1
		n_hit += 1 if hit else 0
		results.append( AlgolispResult(sketch, prog, hit, n_checked, time.time()-t) )
		if hit: break
		if n_checked >= max_to_check: break
	return results, n_checked, n_hit


#pypy_enumerate(datum.tp, datum.IO, mdl, sketchtups, n_checked, n_hit, t, max_to_check)
def pypy_enumerate(tp, IO, schema_args, mdl, sketchtups, n_checked, n_hit, t, max_to_check):
	return callCompiled(algolisp_enumerate, tp, IO, schema_args, mdl, sketchtups, n_checked, n_hit, t, max_to_check)
	#if pypy doesn't work we can just call algolisp_enumerate normally
