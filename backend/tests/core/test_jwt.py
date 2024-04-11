from __future__ import annotations

import pytest

from customer_engine_api.core import jwt


@pytest.mark.unit()
def test_decode_token() -> None:
    assert jwt.KindeToken.from_enconded_token(
        encoded_token="eyJhbGciOiJSUzI1NiIsImtpZCI6ImQ4OjkxOmFhOmI2OjdkOjRmOmViOjIyOmFiOmUzOmMwOjViOmY0Ojc4OjY0OjkyIiwidHlwIjoiSldUIn0.eyJhdWQiOltdLCJhenAiOiIwZWY4YWM1OTk4Nzk0MWE5OGQ5NTFlOGJiMjdjNDE3YiIsImJpbGxpbmciOnsiaGFzX3BheW1lbnRfZGV0YWlscyI6ZmFsc2UsIm9yZ19lbnRpdGxlbWVudHMiOm51bGwsInBsYW4iOnsiYWdyZWVtZW50X2lkIjpudWxsLCJjb2RlIjpudWxsLCJjcmVhdGVkX29uIjpudWxsLCJoYXNfdHJpYWxfcGVyaW9kIjpudWxsLCJpbnZvaWNlX2R1ZV9vbiI6bnVsbCwibmFtZSI6bnVsbCwicGxhbl9jaGFyZ2VfdHlwZSI6bnVsbCwidHJpYWxfZXhwaXJlc19vbiI6bnVsbH19LCJleHAiOjE3MTA0NTAwNjIsImlhdCI6MTcxMDM2MzY2MiwiaXNzIjoiaHR0cHM6Ly9jdXN0b21lcmZvcm1zZW5naW5lLmtpbmRlLmNvbSIsImp0aSI6IjE5NDIwMjExLWFkZmItNDU4Zi04ODhhLTdlYzZkODg0NzAyYSIsIm9yZ19jb2RlIjoib3JnX2NhM2ZhNjEwNmI5IiwicGVybWlzc2lvbnMiOltdLCJzY3AiOlsib3BlbmlkIiwicHJvZmlsZSIsImVtYWlsIiwib2ZmbGluZSJdLCJzdWIiOiJrcF9jYTJlOTI0ODcxOGQ0NzNkYjU2MTg4MWQ5NGU0ZjQ5OCJ9.Mmg04sGqCEkwPWw7BrZZCzqWJoa8FeJYc4cU9RnMMxpmYlpzwEOgLWKUVrh8RJjgpiSW0oUQNXpr6kX8p6GQj7IkNAmemnblxBp9yLaSVc7A-y0xwvJOHexKDtGEOdfVGATmhKoVyzYiZbPZj1EfeF_vL-JxwFLWA6R81eY_MC-gcg4WFDZBP4EXaxK4IiZTo7sqfx1_IP9AVesGeiSqLZUDSgcq47OoZBI7G8RyymJRfasHyhZY-bIxdqQs5lnF2olftrN3g52OzgW67cG6UaOqWkZXJBkt27uBFhL1Ebzx4zQT2x5NNv_1zOh31Fd-H9p_xFxXMxa_0tlXJDArTw",  # noqa: S106
    ) == jwt.KindeToken(
        token_id="19420211-adfb-458f-888a-7ec6d884702a",  # noqa: S106
        scopes=["openid", "profile", "email", "offline"],
        subject="kp_ca2e9248718d473db561881d94e4f498",
        org_code="org_ca3fa6106b9",
        expiration_time=1710450062,
    )
