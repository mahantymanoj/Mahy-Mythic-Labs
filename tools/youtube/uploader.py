"""Upload an approved video to YouTube with an explicit confirmation gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
DEFAULT_CLIENT_SECRETS = "secrets/client_secrets.json"
DEFAULT_TOKEN_PATH = "secrets/youtube_upload_token.json"


def get_credentials(
    client_secrets_path: Path,
    token_path: Path,
) -> Credentials:
    """Load, refresh, or create OAuth credentials for YouTube uploads."""
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


def upload_video(
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    privacy: str,
    client_secrets_path: Path,
    token_path: Path,
) -> dict:
    """Upload one video and return YouTube's video resource response."""
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    credentials = get_credentials(client_secrets_path, token_path)
    youtube = build("youtube", "v3", credentials=credentials)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "27",  # Education
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/*",
        resumable=True,
        chunksize=-1,
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        _, response = request.next_chunk()

    return response


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload an approved Mahy Mythic Labs video to YouTube."
    )
    parser.add_argument("video", help="Path to the final video file")
    parser.add_argument("--title", required=True, help="Approved video title")
    parser.add_argument(
        "--description-file",
        required=True,
        help="Path to a UTF-8 text file containing the approved description",
    )
    parser.add_argument(
        "--tags",
        default="",
        help="Comma-separated tags, for example: history,astronomy,mythology",
    )
    parser.add_argument(
        "--privacy",
        choices=("private", "unlisted", "public"),
        default="private",
        help="Upload visibility. Default: private",
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
    parser.add_argument(
        "--confirm-upload",
        action="store_true",
        help="Required safety confirmation before uploading",
    )
    args = parser.parse_args()

    if not args.confirm_upload:
        parser.error(
            "Upload blocked. Review the final video, then add --confirm-upload."
        )

    description_path = Path(args.description_file)
    if not description_path.exists():
        parser.error(f"Description file not found: {description_path}")

    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]

    try:
        response = upload_video(
            video_path=Path(args.video),
            title=args.title,
            description=description_path.read_text(encoding="utf-8"),
            tags=tags,
            privacy=args.privacy,
            client_secrets_path=Path(args.client_secrets),
            token_path=Path(args.token_path),
        )
    except HttpError as error:
        raise SystemExit(f"YouTube API error: {error}") from error

    print(json.dumps(response, indent=2))
    print(f"Upload complete. Video ID: {response['id']}")
    print(f"Privacy status: {response['status']['privacyStatus']}")


if __name__ == "__main__":
    main()