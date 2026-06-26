# Project Log

## 2026-06-26

- Added Herbert-family migration candidate 0003,
  `experiments/herbert/builtin_arity_candidate.herb`, plus its stdout golden
  and documentation. It mirrors Dolo's current Python-owned
  `HERBERT_BUILTIN_ARITIES` table for observed Herbert built-ins without
  claiming the compiler has migrated away from Python yet.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_herbert_migration_candidates_are_manifested`
  (first observed failure: the expected built-in arity candidate row was absent
  from the manifest; after adding the candidate row/source/stdout/note:
  `Ran 1 test`, `OK`).
- Verified manifest integration with:
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 93 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 10 Dolo executable example(s)`, `PASS: 3 Herbert migration
  candidate(s)`), and confirmed the profile was stopped afterward.
- Added executable application-shaped example `examples/market_day.dolo` with
  committed Herbert and stdout fixtures. It combines two records, annotated
  record parameters, record aliases, assignment, boolean branching, buffer
  mutation, typed array mutation, function calls, and native stdout comparison
  in one manifested proof.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_market_day_example_compiles_to_committed_herbert`
  (first observed failure: the named example file was missing; after adding the
  example and Herbert golden: `Ran 1 test`, `OK`).
- Verified manifest integration with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_executable_manifest_examples_have_main_and_goldens`
  (`Ran 1 test`, `OK`) and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- During native verification, the first `market_day` draft exposed two pinned
  Herbert subset limits: `if` arms must return the same structural shape, and
  `main` should avoid nested tuple values produced by helper calls. The final
  example keeps `main`'s returned tuple flat while still proving the combined
  application flow.
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 93 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 10 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed the profile was stopped afterward.
- Tightened leading and doubled comma diagnostics in declaration lists. Record
  field lists such as `record Pair { , left }` / `record Pair { left,, right }`
  and parameter lists such as `fn id(, a)` / `fn id(a,, b)` now report a
  focused missing-name diagnostic at the comma instead of generic
  `expected ident`.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_record_declaration_rejects_missing_field_names_between_commas tests.test_compiler.CompilerTests.test_function_declaration_rejects_missing_parameter_names_between_commas`
  (first observed failures: all four malformed separators reported
  `expected ident`; after the parser change: `Ran 2 tests`, `OK`).
- Verified neighboring declaration-list comma behavior with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_record_declaration_rejects_trailing_field_comma tests.test_compiler.CompilerTests.test_function_declaration_rejects_trailing_parameter_comma tests.test_compiler.CompilerTests.test_record_declaration_rejects_duplicate_field_names tests.test_compiler.CompilerTests.test_function_declaration_rejects_duplicate_parameter_names`
  (`Ran 4 tests`, `OK`).
- Probed valid record and parameter lists after the change; `record Pair {
  left, right }` and `fn first(a, b)` still compile to the expected Herbert
  function shapes.
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 92 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed the profile was stopped afterward.
- Tightened function parameter list trailing-comma diagnostics. `fn id(a,)`
  and typed forms such as `fn id(a: Box,)` now fail at the comma with a
  parameter-list diagnostic instead of drifting to `expected ident` at the
  closing parenthesis.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_function_declaration_rejects_trailing_parameter_comma`
  (first observed failures: both trailing parameter comma forms reported
  `expected ident` at `)`; after the parser change: `Ran 1 test`, `OK`).
- Verified neighboring parameter behavior with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_function_declaration_rejects_duplicate_parameter_names tests.test_compiler.CompilerTests.test_main_function_must_take_no_parameters tests.test_compiler.CompilerTests.test_function_parameter_annotation_must_name_a_record tests.test_compiler.CompilerTests.test_record_field_access_lowers_to_tuple_index`
  (`Ran 4 tests`, `OK`).
- Probed leading and doubled parameter commas after the change; they still fail
  with the existing `expected ident` diagnostics, while two-parameter functions
  still compile.
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 90 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed the profile was stopped afterward.
- Rejected trailing commas in record field declarations. `record Pair { left, }`
  now fails at the comma instead of compiling as though the trailing comma were
  absent.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_record_declaration_rejects_trailing_field_comma`
  (first observed failure: the trailing-comma record did not raise
  `DoloSyntaxError`; after the parser change: `Ran 1 test`, `OK`).
- Verified neighboring record behavior with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_record_declaration_requires_at_least_one_field tests.test_compiler.CompilerTests.test_record_declaration_rejects_duplicate_field_names tests.test_compiler.CompilerTests.test_record_field_access_lowers_to_tuple_index tests.test_compiler.CompilerTests.test_record_constructor_and_if_else_lower_to_herbert`
  (`Ran 4 tests`, `OK`).
- Probed leading and doubled record field commas after the change; they still
  fail with the existing `expected ident` diagnostics at the offending comma.
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 89 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed the profile was stopped afterward.
- Rejected sources with no top-level Dolo declarations. Empty, whitespace-only,
  newline-only, and comment-only inputs now fail at EOF with a focused
  `source must contain at least one top-level record or fn` diagnostic instead
  of emitting an empty Herbert file.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_source_requires_at_least_one_top_level_declaration`
  (first observed failures: four no-declaration sources did not raise
  `DoloSyntaxError`; after the parser change: `Ran 1 test`, `OK`).
- Verified neighboring top-level declaration diagnostics with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_record_declaration_rejects_duplicate_record_names tests.test_compiler.CompilerTests.test_function_declaration_rejects_duplicate_function_names tests.test_compiler.CompilerTests.test_top_level_declaration_names_must_not_overlap tests.test_compiler.CompilerTests.test_function_declaration_rejects_duplicate_parameter_names`
  (`Ran 4 tests`, `OK`).
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 88 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed the profile was stopped afterward.
- Rejected unsupported expression punctuation before Herbert emission. Dolo now
  fails `return :`, `return 1:2`, `return {1}`, and `return ({1}, 2)` instead
  of preserving colon or brace-shaped expression text.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_expression_rejects_unsupported_punctuation`
  (first observed failures: four punctuation forms did not raise
  `DoloSyntaxError`; after the emitter change: `Ran 1 test`, `OK`).
- Verified neighboring parser-owned delimiter behavior with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_unmatched_expression_closer_reports_closer_column tests.test_compiler.CompilerTests.test_unclosed_expression_delimiter_reports_opening_column tests.test_compiler.CompilerTests.test_unclosed_expression_delimiter_at_eof_reports_opening_column tests.test_compiler.CompilerTests.test_if_else_return_in_both_arms_satisfies_function_return tests.test_compiler.CompilerTests.test_record_constructor_and_if_else_lower_to_herbert`
  (`Ran 5 tests`, `OK`).
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 87 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Added expression adjacency validation so Dolo rejects adjacent value forms
  that would otherwise emit invalid Herbert text: `return 1 2`,
  `return flag true`, `return (1) 2`, `return 1(2)`, and
  `return new_buffer() "x"`.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_adjacent_expression_values_require_an_operator`
  (first observed failures: five adjacent-value forms did not raise
  `DoloSyntaxError`; after the emitter change: `Ran 1 test`, `OK`).
- Verified neighboring expression behavior with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_zero_argument_calls_remain_valid_expressions tests.test_compiler.CompilerTests.test_observed_herbert_builtin_call_target_is_allowed tests.test_compiler.CompilerTests.test_record_field_access_lowers_to_tuple_index tests.test_compiler.CompilerTests.test_record_constructor_and_if_else_lower_to_herbert tests.test_compiler.CompilerTests.test_prefix_not_is_allowed_in_expressions tests.test_compiler.CompilerTests.test_prefix_not_requires_an_operand tests.test_compiler.CompilerTests.test_new_array_accepts_observed_herbert_type_expressions tests.test_compiler.CompilerTests.test_expression_formatting_keeps_space_before_group_after_comma`
  (`Ran 8 tests`, `OK`).
- Probed valid tuple and prefix forms after the change: `(x, 2)` still emits as
  a tuple, `!(flag)` emits `not(flag)`, and `!!flag` emits `not not flag`.
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 86 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Tightened prefix `!` validation so it cannot emit bare or postfix Herbert
  `not` forms. `return !`, `return (!)`, `return (!, flag)`, and
  `return flag !` now fail before emission, while valid prefix use still emits
  Herbert `not`.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_prefix_not_requires_an_operand`
  (first observed failures: four malformed `!` forms did not raise
  `DoloSyntaxError`; after the emitter change: `Ran 1 test`, `OK`).
- Verified neighboring operator behavior with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_prefix_not_requires_an_operand tests.test_compiler.CompilerTests.test_prefix_not_is_allowed_in_expressions tests.test_compiler.CompilerTests.test_binary_operators_require_operands`
  (`Ran 3 tests`, `OK`).
- Probed chained and grouped prefix forms after the change: `!!flag` emits
  `not not flag`, and `!(flag)` emits `not(flag)`.
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 85 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Added dot-shape validation for record field access. Dolo now rejects malformed
  forms such as `x.`, `.x`, `x.(1)`, and constructor-result field access before
  emitting Herbert or drifting into an unrelated unknown-variable diagnostic.
  The implemented field-access surface remains simple `identifier.field`
  lowering.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_field_access_requires_identifier_target_and_field`
  (first observed failures: three malformed dot forms did not raise
  `DoloSyntaxError`, and constructor-result field access reported unknown
  variable `left`; after the emitter change: `Ran 1 test`, `OK`).
- Verified neighboring field-access behavior with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_field_access_requires_identifier_target_and_field tests.test_compiler.CompilerTests.test_record_field_access_lowers_to_tuple_index tests.test_compiler.CompilerTests.test_record_type_propagates_through_identifier_binding tests.test_compiler.CompilerTests.test_record_constructor_and_if_else_lower_to_herbert`
  (`Ran 4 tests`, `OK`).
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 84 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Rejected zero-field record declarations before they can lower to empty
  Herbert tuple-shaped values. `record Empty { }` now fails at the record name
  instead of allowing `Empty()` to emit `()`.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_record_declaration_requires_at_least_one_field`
  (first observed failure: `DoloSyntaxError` was not raised; after the parser
  change: `Ran 1 test`, `OK`).
- Verified neighboring record behavior with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_record_declaration_requires_at_least_one_field tests.test_compiler.CompilerTests.test_record_declaration_rejects_duplicate_field_names tests.test_compiler.CompilerTests.test_record_constructor_and_if_else_lower_to_herbert tests.test_compiler.CompilerTests.test_record_constructor_arity_diagnostic_reports_column tests.test_compiler.CompilerTests.test_record_field_access_lowers_to_tuple_index`
  (`Ran 5 tests`, `OK`).
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 83 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Added expression-shape validation for empty parenthesized value expressions
  and malformed comma fields. Dolo now rejects `return ()`, `return (,1)`,
  `return (1,)`, `return (1,,2)`, and bad function-call comma forms before
  emitting Herbert; valid zero-argument calls such as `new_buffer()` remain
  valid.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_parenthesized_expressions_must_not_be_empty tests.test_compiler.CompilerTests.test_expression_commas_require_values_on_both_sides tests.test_compiler.CompilerTests.test_zero_argument_calls_remain_valid_expressions`
  (first observed failures: direct tuple/group cases did not raise
  `DoloSyntaxError`, while bad call commas failed later as arity errors at the
  call target; after the emitter change: `Ran 3 tests`, `OK`).
- Verified neighboring expression behavior with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_new_array_accepts_observed_herbert_type_expressions tests.test_compiler.CompilerTests.test_expression_formatting_keeps_space_before_group_after_comma tests.test_compiler.CompilerTests.test_record_constructor_and_if_else_lower_to_herbert tests.test_compiler.CompilerTests.test_do_statement_emits_observed_no_value_herbert_builtin_calls tests.test_compiler.CompilerTests.test_observed_herbert_builtin_call_requires_observed_arity`
  (`Ran 5 tests`, `OK`).
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 82 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Added binary-operator shape validation for Dolo expressions, so malformed
  forms such as `return 1 +`, `return + 1`, `return 1 + * 2`, and
  `if flag &&` fail before Dolo emits Herbert with dangling or misplaced
  operators. Prefix `!` remains valid and lowers to Herbert `not`.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_binary_operators_require_operands tests.test_compiler.CompilerTests.test_prefix_not_is_allowed_in_expressions`
  (first observed failures: four malformed binary-operator expressions did not
  raise `DoloSyntaxError`; after the emitter change: `Ran 2 tests`, `OK`).
- Verified neighboring expression/example behavior with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_record_constructor_and_if_else_lower_to_herbert tests.test_compiler.CompilerTests.test_examples_compile_to_committed_herbert tests.test_compiler.CompilerTests.test_text_builtin_example_compiles_to_committed_herbert`
  (`Ran 3 tests`, `OK`).
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 79 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Tightened Dolo's assignment boundary so `=` remains statement syntax only.
  Expressions such as `return x = 1`, `let y = x = 1`, and `if flag = true`
  now fail with a Dolo diagnostic instead of emitting Herbert assignment-shaped
  text that does not belong in the expression surface.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_assignment_operator_is_not_allowed_inside_expressions`
  (first observed failures: three bad expression forms did not raise
  `DoloSyntaxError`; after the emitter change: `Ran 1 test`, `OK`).
- Verified neighboring assignment/example behavior with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_assignment_operator_is_not_allowed_inside_expressions tests.test_compiler.CompilerTests.test_assignment_target_must_already_be_bound tests.test_compiler.CompilerTests.test_examples_compile_to_committed_herbert`
  (`Ran 3 tests`, `OK`).
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 77 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Added conservative return-completeness validation for Dolo functions: a
  function must reach a direct `return`, or an `if` with an `else` where both
  arms guarantee a return, before Dolo emits Herbert. This matches the pinned
  Herbert target's `function '<name>' may complete without returning` boundary
  for the no-loop control-flow forms Dolo currently has.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_functions_must_return_on_all_paths tests.test_compiler.CompilerTests.test_if_else_return_in_both_arms_satisfies_function_return`
  (first observed failures: four fallthrough functions did not raise
  `DoloSyntaxError`; after the parser change: `Ran 2 tests`, `OK`).
- Updated stale diagnostics fixtures that were testing invalid `do` statements
  or constructor arity inside functions that also fell off the end; each now has
  a trailing `return` so the intended diagnostic remains isolated.
- Verified the formerly masked diagnostics with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_do_statement_rejects_value_builtin_calls tests.test_compiler.CompilerTests.test_do_statement_rejects_unknown_calls tests.test_compiler.CompilerTests.test_do_statement_requires_one_whole_call tests.test_compiler.CompilerTests.test_do_statement_validates_no_value_builtin_arity tests.test_compiler.CompilerTests.test_record_constructor_arity_diagnostic_reports_column`
  (`Ran 5 tests`, `OK`).
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 76 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Enforced the pinned Herbert executable-entry boundary for Dolo `main`: when a
  source declares `fn main`, it must take zero parameters before the compiler
  will emit Herbert.
- Verified the RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_main_function_must_take_no_parameters`
  (first observed failure: `DoloSyntaxError` was not raised for
  `fn main(seed)`; after the parser change: `Ran 1 test`, `OK`).
- Updated the executable-manifest no-argument-main test for the new parser
  boundary, since parameterized `main` now fails during Dolo parsing while
  helper-only executable rows still fail with the manifest-specific no-main
  diagnostic.
- Verified the focused parser/manifest boundary with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_main_function_must_take_no_parameters tests.test_compiler.CompilerTests.test_manifest_validator_requires_executable_no_arg_main`
  (`Ran 2 tests`, `OK`).
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 74 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Replaced the stale Dolo shadowing rule for observed Herbert built-ins with a
  target-surface reservation: Dolo function declarations now reject names such
  as `length`, `add`, and `new_array`, matching the pinned Herbert compiler's
  built-in reuse boundary instead of emitting Herbert that native verification
  rejects.
- Moved the observed Herbert built-in names, arities, and type names into
  `src/dolo/herbert_surface.py` so parser and emitter use one target-surface
  table.
- Verified the compiler boundary with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_function_declaration_rejects_observed_herbert_builtin_names tests.test_compiler.CompilerTests.test_observed_herbert_builtin_call_target_is_allowed tests.test_compiler.CompilerTests.test_herbert_void_builtins_are_not_value_calls tests.test_compiler.CompilerTests.test_do_statement_emits_observed_no_value_herbert_builtin_calls`
  (`Ran 4 tests`, `OK`).
- Verified the full local gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 73 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Hardened migration-candidate validation in the other direction too:
  candidate notes under `docs/migration-candidates/` now fail validation when
  they do not link back to any manifested Herbert candidate source.
- Verified the orphan-note validator slice with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_manifest_validator_rejects_orphaned_migration_candidate_notes`
  (first observed failure: an orphaned note was accepted; after the validator
  change: `Ran 1 test`, `OK`).
- Verified the full gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 73 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Hardened migration-candidate validation so notes in
  `docs/migration-candidates/` must mention each manifested Herbert candidate
  source and stdout golden. This keeps executable repayment candidates tied to
  their proof notes instead of relying on nearby prose.
- Verified the migration-note validator slice with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_manifest_validator_requires_migration_candidate_note_links`
  (first observed failures: candidate notes that omitted the source/stdout row
  were accepted; after the validator change: `Ran 1 test`, `OK`).
- Verified the full gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 72 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Improved expression formatting so a grouped expression after a comma keeps a
  separating space in emitted Herbert, for example `array((int, (bool,
  string)))`.
- Verified the formatter slice with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_expression_formatting_keeps_space_before_group_after_comma`
  (first observed failure: emitted Herbert used `int,(bool, string)`; after the
  formatter change: `Ran 1 test`, `OK`). The full bootstrap suite then ran as
  `Ran 71 tests`, `OK`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Added executable example `examples/array_shape.dolo` with committed Herbert
  and stdout fixtures, proving nested observed Herbert type expressions such as
  `array((int, (bool, string)))` and tuple fields containing `array(string)`
  through the executable manifest.
- Verified the nested type-expression example with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 70 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 9 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Tightened `new_array(...)` Herbert type-expression validation so singleton
  tuple types such as `(int)` fail before Dolo emits Herbert that the pinned
  Herbert parser rejects.
- Verified the diagnostic slice with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_new_array_tuple_type_requires_multiple_fields`
  (first observed failure: no `DoloSyntaxError` was raised for
  `new_array((int))`; after the emitter change: `Ran 1 test`, `OK`). The
  neighboring `new_array` type-expression tests then ran as `Ran 3 tests`,
  `OK`.
- Verified the full gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 70 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 8 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Hardened the bootstrap migration-candidate test so it explicitly keeps both
  current Herbert candidates manifested: record field indexing and array
  mutation.
- Added Herbert-family migration candidate 0002,
  `experiments/herbert/array_mutation_candidate.herb`, plus its stdout golden
  and candidate note. It mirrors the pinned typed-array and `do` mutation
  behavior from `examples/array_mutation.dolo` without claiming any Python
  compiler replacement yet.
- Updated `ROADMAP.md` and `docs/trust-debt.md` so they describe the current
  migration-candidate set rather than only candidate 0001.
- Verified the candidate slice with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 69 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 8 Dolo executable example(s)`, `PASS: 2 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Tightened the built-in `new_array(...)` boundary so it now reports a focused
  diagnostic when the call has zero or multiple Herbert type arguments. This
  preserves Dolo function precedence for a user-defined `new_array` function.
- Verified the diagnostic slice with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_new_array_requires_one_herbert_type_argument`
  (first observed failures: zero-argument `new_array()` did not raise, and
  `new_array(int, string)` failed later as `unknown variable 'int'`; after the
  emitter change: `Ran 1 test`, `OK`). The neighboring `new_array` and
  built-in-name precedence tests then ran as `Ran 4 tests`, `OK`.
- Verified the full gate set after the change with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 69 tests`, `OK`), and
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the Linux/x86 Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 8 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Added a narrow `do` statement for observed no-value Herbert mutation built-ins
  `add` and `append`. Dolo value expressions still reject those no-value calls,
  now with a diagnostic that points users to `do`.
- Added executable example `examples/array_mutation.dolo` with committed Herbert
  and stdout fixtures, proving typed `new_array(int)`, `do add`, `get`,
  `count`, `new_buffer`, `do append`, and `freeze` through the executable
  manifest.
- Verified the new RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_do_statement_emits_observed_no_value_herbert_builtin_calls tests.test_compiler.CompilerTests.test_do_statement_rejects_value_builtin_calls tests.test_compiler.CompilerTests.test_do_statement_rejects_unknown_calls tests.test_compiler.CompilerTests.test_do_statement_validates_no_value_builtin_arity`
  (first observed failure: `do` parsed as an assignment target and reported
  `line 2, column 6: expected '='`; after the parser/emitter change:
  `Ran 4 tests`, `OK`).
- Tightened the no-value built-in expression diagnostic after `do` landed:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_herbert_void_builtins_are_not_value_calls`
  first failed because the message still said `Dolo do statements are not
  implemented`; after the diagnostic update, the focused no-value and `do`
  tests ran as `Ran 5 tests`, `OK`.
- Verified locally with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 68 tests`, `OK`), plus
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the executable Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 8 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Added a narrow typed-array boundary for observed Herbert `new_array(...)`
  calls: the emitter now accepts primitive, nested `array(T)`, and tuple-shaped
  Herbert type expressions as type arguments instead of misreporting type names
  as unknown Dolo variables.
- Rejected observed Herbert no-value mutation built-ins `add` and `append` in
  Dolo expressions until Dolo owns an explicit `do` statement, closing a docs
  overclaim where the target subset named built-ins the Dolo surface could not
  honestly use.
- Added executable example `examples/array_seed.dolo` with committed Herbert
  and stdout fixtures, proving typed empty-array construction plus `count`
  through the executable manifest.
- Pinned the existing name-resolution boundary that Dolo-declared functions
  take precedence over observed Herbert built-in names, so user functions named
  `add` or `append` are not mistaken for no-value built-ins.
- Verified the new RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_new_array_accepts_observed_herbert_type_expressions tests.test_compiler.CompilerTests.test_new_array_type_argument_must_be_observed_herbert_type_expression tests.test_compiler.CompilerTests.test_herbert_void_builtins_are_not_value_calls`
  (first observed failures: `new_array(int)` reported `unknown variable 'int'`,
  `new_array(Missing)` reported `unknown variable 'Missing'`, and `add` /
  `append` did not raise; after the emitter change: `Ran 3 tests`, `OK`).
- Verified locally with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 63 tests`, `OK`), plus
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the executable Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 7 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Hardened parser diagnostics for unsupported `elif` so the parser reports the
  `elif` column with a direct unsupported-form message instead of treating it
  as an assignment target and drifting to `expected '='`.
- Verified the new diagnostic RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_elif_reports_unsupported_form`
  (first observed failure: `line 4, column 10: expected '='`; after the parser
  change: `Ran 1 test`, `OK`).
- Verified locally with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 58 tests`, `OK`), plus
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the executable Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 6 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.
- Hardened parser diagnostics for stray `else` statements so `else` without a
  matching `if` reports the `else` column instead of the generic
  `expected ident` parser fallback.
- Verified the new diagnostic RED/GREEN path with:
  `PYTHONPATH=src python3 -m unittest tests.test_compiler.CompilerTests.test_stray_else_reports_without_matching_if`
  (first observed failure: `line 2, column 3: expected ident`; after the parser
  change: `Ran 1 test`, `OK`).
- Verified locally with:
  `git diff --check`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 59 tests`, `OK`), plus
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the executable Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 6 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`), and confirmed both Colima profiles were stopped afterward.

## 2026-06-25

- Created `CommonHerb/dolo` as a public GitHub repository.
- Created a clean local checkout at `/Users/ben/Desktop/untitled folder 2/dolo`.
- Observed sibling Herbert checkout at `/Users/ben/Desktop/untitled folder 2/herbert`.
- Verified sibling Herbert remote is `https://github.com/CommonHerb/herbert.git`
  and current commit is `e9dff2283113063f60fece453e9ab9eb16e7366a`.
- Read Herbert `README.md`, `VERIFYING.md`, `Makefile`, parser probes, and
  foundational examples to ground the first target subset.
- Noted local substrate boundary: this machine is Apple Silicon macOS; Herbert's
  committed production seed is an x86-64 Linux ELF, so generated Herbert
  execution needs Linux/x86-64, CI, or emulation.
- Added the first Python-standard-library bootstrap compiler slice on branch
  `foundation/compiler-v0`: records, record constructors, annotated record
  parameters, field access lowering, functions, `let`, assignment, `return`,
  `if` / `else`, expressions preserved into readable Herbert, examples, CLI,
  and unit tests.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`.
- Pushed `foundation/compiler-v0`, observed GitHub Actions `check` success,
  fast-forwarded `main`, pushed `main`, and observed GitHub Actions `check`
  success on `main` at `c485cee2c74dd8f8fa2f4ec623741b7845f79dfa`.
- Addressed final review by adding record-constructor arity validation, tests
  for too-few and too-many fields, and `!` to `not` lowering.
- Declared the bootstrap's current Python substrate as Python 3.13 because that
  is the locally verified interpreter and CI lane for this first slice.
- Started branch `foundation/executable-truth-loop` from
  `a01dd9fe493d6aba5d05723563ef58265dad5b1a`.
- Added executable `main` examples for `citizen` and `ledger`, committed
  Herbert goldens, committed native stdout keys, and a manifest in
  `tests/fixtures/executable_manifest.tsv`.
- Added `HERBERT.lock` pinning `CommonHerb/herbert` at
  `e9dff2283113063f60fece453e9ab9eb16e7366a` with gen-1 seed sha256
  `8a9be3012cd3a132d2da5eb25df0b083671ff352725fdfb10504f1e7a939ce50`.
- Added `scripts/verify_herbert_truth.sh`, which requires Linux/x86_64, checks
  the Herbert checkout and seed hash, stages a temporary executable seed copy,
  compiles generated Herbert to ELF, runs the ELF, and compares native stdout.
- Added a GitHub Actions `herbert-execution` job that checks out pinned Herbert
  and runs the executable truth loop on Ubuntu.
- Added `docs/language-reference.md` for the implemented v0.1 surface and
  `docs/trust-debt.md` for borrowed substrate.
- Updated the workflow to current `actions/checkout@v7` and
  `actions/setup-python@v6` after GitHub reported Node 20 deprecation
  annotations on the older actions.
- Added the first tiny Herbert-family migration candidate,
  `experiments/herbert/record_field_index_candidate.herb`, plus
  `docs/migration-candidates/0001-record-field-index.md` and a CI manifest so
  the candidate runs through the same pinned Herbert seed.
- Started Dolo stewardship branch `codex/dolo-stewardship-20260625`.
- Tightened tokenizer diagnostics so unexpected characters and unterminated
  string or character literals report line and column, with focused RED-first
  tests.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 14 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 2 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Pushed `codex/dolo-stewardship-20260625` to origin at
  `c392db6958ab6fd43148c02ff43cac962808a125` and observed GitHub Actions
  `check` success for run `28212891134`.
- Tightened parser and lowering diagnostics so record constructor arity,
  unresolved field access, unknown record fields, and unclosed expression
  delimiters report useful columns instead of line-only or drifted block errors.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 18 tests`, `OK`).
- Taught the bootstrap CLI to report `DoloSyntaxError` diagnostics as plain
  `dolo: ...` stderr messages with exit status 1 instead of exposing Python
  tracebacks.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 19 tests`, `OK`).
- Added parser guardrails for ambiguous duplicate names: top-level records,
  top-level functions, record fields, and function parameters now fail with
  columned `DoloSyntaxError` messages.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 23 tests`, `OK`).
- Added executable example `examples/boolean_gate.dolo` to prove existing Dolo
  boolean operator lowering (`&&`, `||`, `!`) through committed Herbert and
  stdout fixtures.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 23 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 3 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Extended the bootstrap CLI's plain-error boundary to source-file read
  failures, so missing input files report `dolo: PATH: No such file or
  directory` without a Python traceback.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 24 tests`, `OK`).
- Added type-boundary validation for record parameter annotations: annotations
  must name a record declared in the same source file and now fail with a
  columned `DoloSyntaxError` instead of being silently ignored.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 25 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 3 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Added expression variable reference validation: plain variable references now
  must name a parameter or earlier `let` binding, and unknown references fail
  with a columned `DoloSyntaxError`.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 29 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 3 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Added assignment target validation: assignment now updates only parameters or
  names introduced by `let`, and unbound assignment targets fail with a
  columned `DoloSyntaxError`.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 26 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 3 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Added function call target validation: calls now target Dolo functions
  declared in the same source file or the observed Herbert built-ins documented
  in `docs/foundation/herbert-target-subset.md`; unknown call targets fail with
  a columned `DoloSyntaxError`.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 28 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 3 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Added Dolo function call arity validation: calls to Dolo functions declared
  in the same source now require the declared number of arguments and fail with
  a columned diagnostic when the count differs. Observed Herbert built-in calls
  remain target-validated by name only; Dolo still does not claim their arity.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 30 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 3 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Added `let` binding redeclaration validation: `let` now introduces only new
  names in the current binding context, so attempts to shadow a parameter or
  earlier local binding fail with a columned diagnostic. Assignment remains the
  spelling for updating an existing binding.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 31 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 3 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Updated `VERIFYING.md` so the local bootstrap-test proof list names the
  current diagnostic and binding checks, CLI plain-error checks, and Herbert
  harness pin/staging coverage instead of describing only the earliest example
  compiler behavior.
- Added narrow record type propagation through simple identifier bindings:
  a `let` or assignment from a single identifier with known record type now
  carries that type knowledge forward, so aliases can use record field access
  without a full Dolo type system.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 32 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 3 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Added executable example `examples/citizen_alias.dolo` with committed Herbert
  and stdout fixtures, proving the record-alias field-access behavior through
  the executable manifest instead of only the unit-level compiler test.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 32 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 4 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Added executable example `examples/stock_update.dolo` with committed Herbert
  and stdout fixtures, proving parameter and local assignment updates through
  the executable manifest.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 32 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 5 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Tightened parser EOF diagnostics for unclosed expression delimiters: an
  expression ending at EOF with an open delimiter now reports the opening
  delimiter column instead of drifting into an `unterminated block` message.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 33 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 5 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Tightened parser diagnostics for unclosed delimiters in brace-terminated
  expressions such as `if` conditions: an open delimiter now reports the
  opening delimiter column instead of drifting to an `expected '{'` at EOF.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 34 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 5 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Hardened the executable manifest workflow by requiring manifest rows to stay
  sorted, then reordered `tests/fixtures/executable_manifest.tsv` by source path
  so future executable examples have a deterministic insertion point.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 34 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 5 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Added `tests/fixtures/non_executable_examples.tsv` and a bootstrap test that
  requires every `examples/*.dolo` file to be classified as executable or
  explicitly non-executable with a reason, so example additions cannot bypass
  the Herbert truth-loop decision surface by accident.
- Updated `VERIFYING.md` to document the executable/non-executable example
  classification rule.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 35 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 5 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Tightened expression delimiter diagnostics so unmatched closing delimiters
  such as `return flag)` and `if flag) {` fail at the closing delimiter column
  instead of drifting into later parser errors or emitted Herbert text.
- Updated `docs/language-reference.md` and `VERIFYING.md` to document the
  delimiter diagnostic contract.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 37 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 5 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Tightened expression keyword diagnostics so non-literal keywords such as
  `return let` fail at the keyword column instead of being emitted as Herbert
  text. Boolean keyword literals `true` and `false` remain valid.
- Updated `docs/language-reference.md` and `VERIFYING.md` to document the
  expression keyword boundary.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 38 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 5 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Added a Python-standard-library manifest validator that rejects malformed TSV
  rows, unsorted manifests, missing file targets, duplicate executable versus
  non-executable example classifications, and unclassified examples before the
  slower Herbert execution loop runs.
- Wired `scripts/verify_herbert_truth.sh` to run the same manifest validator
  before staging the pinned Herbert seed, keeping local and Linux/x86_64
  manifest contracts aligned.
- Updated `VERIFYING.md` and `docs/trust-debt.md` to document the new
  validation proof and its Python bootstrap-substrate status.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 40 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 5 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Added executable example `examples/text_probe.dolo` with committed Herbert and
  stdout fixtures, proving the documented `length`, `index`, and `equal`
  built-in path through Dolo and pinned Herbert. The example keeps Herbert's
  observed convention that string `index` returns an integer byte value.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 41 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 6 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Added observed arity validation for value-level Herbert built-ins that Dolo can
  currently emit directly, so bad calls such as `length("abc", 1)` fail with a
  Dolo diagnostic before reaching Herbert's lower-level native-subset checks.
- Updated `docs/language-reference.md`, `docs/foundation/herbert-target-subset.md`,
  and `VERIFYING.md` to document this as an arity boundary only, not a full
  Dolo type-system claim.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 42 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 6 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Fixed a stale `docs/language-reference.md` Functions paragraph that still
  described observed Herbert built-ins as name-validated only after the compiler
  gained observed arity diagnostics.
- Rejected cross-kind top-level declaration duplicates, so a record and function
  can no longer share a name that would be ambiguous between constructor and
  call lowering.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 43 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 6 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Hardened repository manifest validation to reject duplicate source rows in
  executable example, non-executable example, and Herbert migration manifests
  before the native truth loop runs.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 44 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 6 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Hardened repository manifest validation so executable Dolo rows must parse
  and define a no-argument `fn main()` before the native truth loop runs.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 45 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 6 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Updated `docs/language-reference.md` diagnostics to name the already-enforced
  record/function top-level declaration overlap check.
- Hardened Herbert migration manifest validation so migration sources must be
  `.herb` files with a visible `func main()` entry point before the native truth
  loop runs.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 46 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 6 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Hardened executable manifest validation so source, Herbert golden, and stdout
  golden columns must use `.dolo`, `.herb`, and `.stdout` suffixes before the
  native truth loop runs.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 47 tests`, `OK`).
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 6 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Hardened repository manifest validation so Herbert migration stdout goldens
  must use `.stdout`, and both executable and migration stdout goldens must end
  with a newline before the native truth loop compares process output.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 49 tests`, `OK`), plus
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the executable Herbert truth loop through the local stopped-after-use
  `herbert-x86` Colima profile:
  `PYTHONPATH=src scripts/verify_herbert_truth.sh --herbert-dir ../herbert`
  (`PASS: 6 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
- Hardened repository manifest validation so generated Herbert/stdout output
  targets cannot be reused across executable rows or migration rows, and so
  manifest file targets must remain repository-relative; absolute paths and
  parent-directory traversal are rejected before the native truth loop can read
  or execute outside Dolo's tree.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 51 tests`, `OK`), plus
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the executable Herbert truth loop in GitHub Actions on Linux/x86_64:
  `scripts/verify_herbert_truth.sh --herbert-dir herbert`
  (`PASS: 6 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`) for pushed commit `79b1e551`. The local `herbert-x86` Colima
  profile remained flaky during this slice (`host agent process has exited:
  signal: killed`; one retry dropped SSH after 3 executable examples), so CI is
  the current native truth source for this checkpoint.
- Hardened manifest verification so executable `.dolo` rows must compile to the
  committed `.herb` golden during `python3 -m dolo.manifests --root . verify`,
  and hardened CI so the Herbert checkout ref is read from `HERBERT.lock`
  instead of duplicated in the workflow.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 53 tests`, `OK`), plus
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Hardened CI so both the Herbert repository and commit are read from
  `HERBERT.lock`, eliminating the workflow's remaining duplicate Herbert
  checkout target. Added `scripts/verify_herbert_truth_colima.sh` as a local
  wrapper that starts the existing Colima profile, runs the pinned truth loop,
  attempts to stop the profile on exit, bounds cleanup stop commands, and names
  the profile logs to inspect when local Colima verification fails.
- Verified locally with:
  `bash -n scripts/verify_herbert_truth_colima.sh`,
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 54 tests`, `OK`), plus
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Local wrapper execution did not complete the truth loop in this slice:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  exited `1` during Colima startup with `host agent process has exited:
  signal: killed`. The wrapper printed the diagnostic log paths, exited instead
  of hanging, and the profile was verified stopped afterward (`colima list`:
  `herbert-x86 Stopped`); inspect
  `/Users/ben/.colima/_lima/colima-herbert-x86/ha.stderr.log` and `serial.log`
  for local Colima details. GitHub Actions remains the Linux/x86_64 truth
  source for this checkpoint.
- Hardened manifest validation so executable and non-executable example source
  rows must be top-level `examples/*.dolo` paths, closing a gap where
  non-executable rows could name arbitrary existing files with reason text.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 55 tests`, `OK`), plus
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Hardened manifest validation so executable Herbert/stdout goldens must stay
  in `tests/fixtures/`, Herbert migration candidates must stay in
  `experiments/herbert/`, and migration stdout goldens must stay in
  `tests/fixtures/`.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 56 tests`, `OK`), plus
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Hardened parser diagnostics for unsupported `else if` so the parser reports
  the `if` column with a direct unsupported-form message instead of the generic
  `expected '{'` block diagnostic.
- Verified locally with:
  `PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"`
  (`Ran 57 tests`, `OK`), plus
  `PYTHONPATH=src python3 -m dolo.manifests --root . verify`.
- Verified the executable Herbert truth loop through the stopped-after-use
  `herbert-x86` Colima profile:
  `scripts/verify_herbert_truth_colima.sh --profile herbert-x86 --herbert-dir ../herbert`
  (`PASS: 6 Dolo executable example(s)`, `PASS: 1 Herbert migration
  candidate(s)`).
