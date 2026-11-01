#!/usr/bin/env python3
"""
Master E2E Test Runner for Recommendation Platform.

Discovers and runs test tiers:
- Tier 1: Feature Coverage (tests/test_tier1_feature.py)
- Tier 2: Boundary & Corner Cases (tests/test_tier2_boundary.py)
- Tier 3: Cross-Feature Interactions (tests/test_tier3_interaction.py)
- Tier 4: Real-World Workloads (tests/test_tier4_workload.py)

Usage:
    python tests/test_runner.py              # Run all tiers
    python tests/test_runner.py --tier 1     # Run specific tier (1, 2, 3, or 4)
    python tests/test_runner.py --verbose    # Verbose test output
    python tests/test_runner.py --summary    # Brief summary only
"""
import argparse
import sys
import time
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import tier test modules
from tests import test_tier1_feature
from tests import test_tier2_boundary
from tests import test_tier3_interaction
from tests import test_tier4_workload
from tests import test_tier5_adversarial_frontend

TIER_CONFIG = {
    1: {
        "name": "Tier 1: Feature Coverage",
        "description": "Standard <head>, OpenGraph, Twitter, Schema JSON-LD, Sitemap, Robots, UI, Retention, AdSense, Trust, Links",
        "module": test_tier1_feature,
    },
    2: {
        "name": "Tier 2: Boundary & Corner Cases",
        "description": "Empty codes, missing links, date boundaries, extreme lengths, special chars/XSS, small viewports, edge datasets",
        "module": test_tier2_boundary,
    },
    3: {
        "name": "Tier 3: Cross-Feature Interactions",
        "description": "Search + filter, dark mode + ads, i18n + SEO, ad spacing + CTAs, 3-state cards, theme persistence, sitemap parity",
        "module": test_tier3_interaction,
    },
    4: {
        "name": "Tier 4: Real-World Application Workloads",
        "description": "End-to-end build verification, production artifacts, full DOM parsing, trust pages, strict sitemap & robots, dataset fidelity",
        "module": test_tier4_workload,
    },
    5: {
        "name": "Tier 5: Adversarial Coverage Hardening",
        "description": "Design tokens, Inter+Noto typography, 3-state cards, category chips & counts, JS & i18n parity, AdSense 4 zero-CLS, Trust pages E-E-A-T, mobile viewports & a11y",
        "module": test_tier5_adversarial_frontend,
    },
}


class DetailedTestResult(unittest.TextTestResult):
    """Custom test result collector capturing status per test method."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.successes = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.successes.append(test)


def run_tier(tier_num: int, verbose: bool = False) -> dict:
    """Run tests for a single tier and return structured metrics."""
    config = TIER_CONFIG[tier_num]
    suite = unittest.defaultTestLoader.loadTestsFromModule(config["module"])
    
    start_time = time.time()
    runner = unittest.TextTestRunner(
        resultclass=DetailedTestResult,
        verbosity=2 if verbose else 0,
        stream=sys.stdout if verbose else unittest.runner._WritelnDecorator(open(os.devnull, "w"))
    )
    result = runner.run(suite)
    elapsed = time.time() - start_time

    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = len(result.successes)
    
    return {
        "tier": tier_num,
        "name": config["name"],
        "description": config["description"],
        "total": total,
        "passed": passed,
        "failed": failures + errors,
        "failures_list": result.failures,
        "errors_list": result.errors,
        "elapsed": elapsed,
        "success": (failures + errors) == 0,
    }


def print_banner():
    banner = """
================================================================================
           E2E TEST RUNNER -- RECOMMENDATION PLATFORM TEST SUITE
================================================================================
Methodology: 4-Tier Opaque-Box Specification Verification
Scope: SEO Engine, Modern UX/UI, AdSense Readiness, Robustness & Integrity
================================================================================
"""
    print(banner.strip())


def main():
    parser = argparse.ArgumentParser(description="Master E2E Test Runner for Recommendation Platform.")
    parser.add_argument(
        "--tier",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Run only the specified test tier (1: Feature, 2: Boundary, 3: Interaction, 4: Workload, 5: Adversarial).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tiers including Tier 5 Adversarial Coverage Hardening.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output for each individual test case execution.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary table without detailed failure traces.",
    )
    parser.add_argument(
        "--exit-zero",
        action="store_true",
        help="Always exit with code 0 (useful for diagnostic reporting in CI setup phases).",
    )
    args = parser.parse_args()

    print_banner()

    if args.tier:
        tiers_to_run = [args.tier]
    elif args.all:
        tiers_to_run = [1, 2, 3, 4, 5]
    else:
        tiers_to_run = [1, 2, 3, 4]
    tier_results = []
    
    overall_start = time.time()
    for t_num in tiers_to_run:
        print(f"\n>> Executing [{TIER_CONFIG[t_num]['name']}]...")
        res = run_tier(t_num, verbose=args.verbose)
        tier_results.append(res)
        status_str = "PASS" if res["success"] else "FAIL"
        print(f"   Status: [{status_str}] -- Passed: {res['passed']}/{res['total']} | Failed: {res['failed']} ({res['elapsed']:.2f}s)")

    overall_elapsed = time.time() - overall_start

    # Summary Table
    print("\n" + "=" * 80)
    print("                              TEST EXECUTION SUMMARY                            ")
    print("=" * 80)
    print(f"{'Tier':<8} | {'Tier Name':<38} | {'Total':<6} | {'Pass':<6} | {'Fail':<6} | {'Status'}")
    print("-" * 80)

    total_tests = 0
    total_passed = 0
    total_failed = 0

    for r in tier_results:
        total_tests += r["total"]
        total_passed += r["passed"]
        total_failed += r["failed"]
        status = "PASSED" if r["success"] else "FAILED"
        print(f"Tier {r['tier']:<3} | {r['name']:<38} | {r['total']:<6} | {r['passed']:<6} | {r['failed']:<6} | {status}")

    print("-" * 80)
    pass_pct = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"TOTAL    | All Selected Tiers                     | {total_tests:<6} | {total_passed:<6} | {total_failed:<6} | {pass_pct:.1f}% Pass")
    print("=" * 80)
    print(f"Total Suite Execution Time: {overall_elapsed:.2f} seconds\n")

    # Failure Details (if not --summary)
    if total_failed > 0 and not args.summary:
        print("=" * 80)
        print("                             FAILED TESTS BREAKDOWN                             ")
        print("=" * 80)
        for r in tier_results:
            if r["failed"] == 0:
                continue
            print(f"\n--- [{r['name']}] Failures ({r['failed']}) ---")
            for test, traceback_str in r["failures_list"]:
                test_name = test.id().split(".")[-1]
                test_doc = test.shortDescription() or ""
                # Get assertion failure line
                last_line = traceback_str.strip().splitlines()[-1]
                print(f"  * {test_name}: {test_doc}")
                print(f"    Reason: {last_line}")
            for test, traceback_str in r["errors_list"]:
                test_name = test.id().split(".")[-1]
                test_doc = test.shortDescription() or ""
                last_line = traceback_str.strip().splitlines()[-1]
                print(f"  * ERROR in {test_name}: {test_doc}")
                print(f"    Reason: {last_line}")

    if total_failed == 0:
        print("\nALL TESTS PASSED! Project meets 100% of tested requirements.\n")
        return 0
    else:
        print(f"\nATTENTION: {total_failed} test(s) failed. See breakdown above for requirements to implement.\n")
        return 0 if args.exit_zero else 1


if __name__ == "__main__":
    import os
    sys.exit(main())
