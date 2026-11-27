"""Fetch a private Drive overlay with application-default credentials; fail closed."""
import argparse
import os
import tempfile
from pathlib import Path
from .historical_quarantine import load_holds

FILE_ID = "1Jw9dfxT2ksMSNrOnnsmZE9YQrdSe3ATt"
EXPECTED_BYTES = 30352499

def retrieve(output):
    import google.auth
    from google.auth.transport.requests import AuthorizedSession
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/drive.readonly"])
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    fd, name = tempfile.mkstemp(prefix=".overlay-", dir=output.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream, AuthorizedSession(credentials) as session:
            with session.get("https://www.googleapis.com/drive/v3/files/"+FILE_ID, params={"alt":"media","supportsAllDrives":"true"}, stream=True, timeout=(15,120), allow_redirects=False) as response:
                if response.status_code != 200:
                    raise RuntimeError("Drive retrieval failed: HTTP "+str(response.status_code))
                size = 0
                for chunk in response.iter_content(chunk_size=65536):
                    size += len(chunk)
                    if size > EXPECTED_BYTES:
                        raise ValueError("Overlay exceeds expected size")
                    stream.write(chunk)
                if size != EXPECTED_BYTES:
                    raise ValueError("Overlay size mismatch")
        holds = load_holds(temp)
        os.link(temp,output)
        print("Verified quarantine keys:",len(holds))
    finally:
        temp.unlink(missing_ok=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path)
    retrieve(parser.parse_args().output)
