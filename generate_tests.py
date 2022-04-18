import argparse
import os
import random
import sys


TEST_STEP_WEIGHT_MAP = {
    'login_page_load': 0.05,
    'home_page_load': 0.05,
    'tool_search_load': 0.05,
    'tool_form_load': 0.1,
    'workflow_list_page_load': 0.1,
    'workflow_run_page_load': 0.6,
    'workflow_history_summary_load': 0.15
}

WORKFLOW_WEIGHT_MAP = {
    'Selenium_test_1': 0.2,
    'Selenium_test_2': 0.45,
    'Selenium_test_3': 0.3,
    'Selenium_test_4': 0.05
}


def from_env_or_required(key):
    return {'default': os.environ[key]} if os.environ.get(key) else {'required': True}


def print_test_plan(args):
    step_list = random.choices(list(TEST_STEP_WEIGHT_MAP.keys()), weights=TEST_STEP_WEIGHT_MAP.values(), k=args.num_tests)
    for step_name in step_list:
        plan = f"sudo docker run -e GALAXY_USERNAME={args.username} -e GALAXY_PASSWORD={args.password} -e GALAXY_SERVER={args.server} usegalaxyau/page_perf_timer:latest --end_step={step_name}"
        if step_name not in ['login_page_load', 'home_page_load', 'tool_search_load', 'tool_form_load']:
            workflow_names = random.choices(list(WORKFLOW_WEIGHT_MAP.keys()), weights=WORKFLOW_WEIGHT_MAP.values(), k=1)
            plan += f" --workflow_name {workflow_names[0]}"
        print(plan)


def create_parser():
    parser = argparse.ArgumentParser(
        description='Generate a suite of tests that can be piped into gnu parallel')
    parser.add_argument('-s', '--server', default=os.environ.get('GALAXY_SERVER') or "https://usegalaxy.org.au",
                        help="Galaxy server url")
    parser.add_argument('-u', '--username', **from_env_or_required('GALAXY_USERNAME'),
                        help="Galaxy username to use (or set GALAXY_USERNAME env var)")
    parser.add_argument('-p', '--password', **from_env_or_required('GALAXY_PASSWORD'),
                        help="Password to use (or set GALAXY_PASSWORD env var)")
    parser.add_argument('--num_tests', type=int, default=10,
                        help="Number of tests to generate")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    print_test_plan(args)
    return 0


if __name__ == '__main__':
    sys.exit(main())
