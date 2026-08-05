"""Retrieve read-only YouTube Analytics reports and save them as CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]
DEFAULT_CLIENT_SECRETS = "secrets/client_secrets.json"
DEFAULT_TOKEN_PATH = "secrets/youtube_analytics_token.json"


def get_credentials(
    client_secrets_path: Path,
    token_path: Path,
) -> Credentials:
    """Load, refresh, or create read-only Analytics OAuth credentials."""
    credentials: Credentials | None = None

    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(token_path, SCOPES)

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    if not credentials or not credentials.valid:
        if not client_secrets_path.exists():
            raise FileNotFoundError(
                f"OAuth client secrets not found: {client_secrets_path}"
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_path,
            SCOPES,
        )
        credentials = flow.run_local_server(port=0)

    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(credentials.to_json(), encoding="utf-8")
    return credentials


def query_channel_analytics(
    start_date: str,
    end_date: str,
    client_secrets_path: Path,
    token_path: Path,
) -> pd.DataFrame:
    """Return daily channel metrics as a pandas DataFrame."""
    credentials = get_credentials(client_secrets_path, token_path)
    analytics = build("youtubeAnalytics", "v2", credentials=credentials)

    report = analytics.reports().query(
        ids="channel==MINE",
        startDate=start_date,
        endDate=end_date,
        metrics="views,likes,comments,estimatedMinutesWatched,subscribersGained",
        dimensions="day",
        sort="day",
    ).execute()

    columns = [header["name"] for header in report.get("columnHeaders", [])]
    rows = report.get("rows", [])
    return pd.DataFrame(rows, columns=columns)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export read-only YouTube channel analytics to CSV."
    )
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    parser.add_argument(
        "--output",
        default="reports/youtube-analytics.csv",
        help="Destination CSV path",
    )
    parser.add_argument(
        "--client-secrets",
        default=DEFAULT_CLIENT_SECRETS,
        help="OAuth client-secret JSON path",
    )
    parser.add_argument(
        "--token-path",
        default=DEFAULT_TOKEN_PATH,
        help="Local OAuth token path",
    )
    args = parser.parse_args()

    report = query_channel_analytics(
        start_date=args.start_date,
        end_date=args.end_date,
        client_secrets_path=Path(args.client_secrets),
        token_path=Path(args.token_path),
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(output_path, index=False)

    print(f"Saved {len(report)} rows to: {output_path}")


if __name__ == "__main__":
    main()