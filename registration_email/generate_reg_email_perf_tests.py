import argparse
import os
import sys
import uuid
from string import Template


def from_env_or_required(key):
    return {"default": os.environ[key]} if os.environ.get(key) else {"required": True}


def print_test_plan(args):
    for test_no in range(args.num_users):
        email = Template(args.email_template).substitute(test_no=test_no)
        username = Template(args.username_template).substitute(test_no=test_no)
        extra_envs = f"-e GALAXY_API_KEY={args.api_key}" if args.api_key else ""
        plan = f"sudo docker run --rm -e GALAXY_SERVER={args.server} -e GALAXY_EMAIL={email} -e GALAXY_USERNAME={username} -e GALAXY_PASSWORD={args.password} -e IMAP_SERVER={args.imap_server} -e IMAP_USERNAME={args.imap_username} -e IMAP_PORT={args.imap_port} -e IMAP_PASSWORD={args.imap_password} {extra_envs} usegalaxyau/registration_email_perf_timer:latest"
        print(plan)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Generate a suite of tests that can be piped into gnu parallel"
    )
    parser.add_argument(
        "-s",
        "--server",
        default=os.environ.get("GALAXY_SERVER") or "https://dev.usegalaxy.org.au",
        help="Galaxy server url",
    )
    parser.add_argument(
        "-e",
        "--email_template",
        default=os.environ.get("GALAXY_EMAIL_TEMPLATE")
        or "usegalaxyaustresstest+u_$test_no@gmail.com",
        help="Email address template to use when registering the user (or set GALAXY_EMAIL_TEMPLATE env var). Template values will be filled in using Template.substitute. Supported variables: test_no",
    )
    parser.add_argument(
        "-u",
        "--username_template",
        default=os.environ.get("GALAXY_USERNAME_TEMPLATE") or "u_$test_no",
        help="Username template to use when registering the user (or set GALAXY_USERNAME env var). Template values will be filled in using Template.substitute. Supported variables: test_no",
    )
    parser.add_argument(
        "-p",
        "--password",
        default=os.environ.get("GALAXY_PASSWORD") or uuid.uuid4(),
        help="Password to use when registering the user (or set GALAXY_PASSWORD env var)",
    )
    parser.add_argument(
        "-i",
        "--imap_server",
        default=os.environ.get("IMAP_SERVER") or "imap.gmail.com",
        help="IMAP server to use when checking for receipt of email (or set IMAP_SERVER env var)",
    )
    parser.add_argument(
        "-o",
        "--imap_port",
        type=int,
        default=os.environ.get("IMAP_PORT") or 993,
        help="IMAP port to use when checking for receipt of email (or set IMAP_PORT env var)",
    )
    parser.add_argument(
        "-m",
        "--imap_username",
        default=os.environ.get("IMAP_USERNAME") or "usegalaxyaustresstest@gmail.com",
        help="IMAP username to use when checking for receipt of email (or set IMAP_USERNAME env var)",
    )
    parser.add_argument(
        "-a",
        "--imap_password",
        **from_env_or_required("IMAP_PASSWORD"),
        help="IMAP password to use when checking for receipt of email (or set IMAP_PASSWORD env var)",
    )
    parser.add_argument(
        "-k",
        "--api_key",
        default=os.environ.get("GALAXY_API_KEY"),
        help="Galaxy API key. If specified, the created user will be deleted at the end of the test run",
    )
    parser.add_argument(
        "--num_users", type=int, default=10, help="Number of users to register"
    )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    print_test_plan(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
