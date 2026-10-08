"""CLI entry point: python main.py [--once | --loop]"""
import argparse
import time

from gmail_agent import agent, config, gmail_client


def main():
    parser = argparse.ArgumentParser(description="Gmail auto-reply agent (Claude API)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="Process unread mail once and exit (default)")
    mode.add_argument("--loop", action="store_true", help="Keep polling until Ctrl+C")
    args = parser.parse_args()

    service = gmail_client.authenticate()
    my_email = gmail_client.get_my_email(service)
    print(f"Authenticated as: {my_email}")
    print(f"Mode: {config.AUTO_SEND_MODE}")

    session_start_ms = int(time.time() * 1000)
    if args.loop:
        agent.run_loop(service, my_email, session_start_ms)
    else:
        agent.process_once(service, my_email, session_start_ms)


if __name__ == "__main__":
    main()
