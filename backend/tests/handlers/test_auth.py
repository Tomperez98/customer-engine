from __future__ import annotations

import datetime

import lego_workflows
import pytest
from fastapi.security import HTTPAuthorizationCredentials

from customer_engine_api import handlers
from customer_engine_api.core.time import now


@pytest.mark.e2e()
async def test_expired_token() -> None:
    with pytest.raises(handlers.auth.validate_token.TokenExpiredError):
        await lego_workflows.run_and_collect_events(
            handlers.auth.validate_token.Command(
                token=HTTPAuthorizationCredentials(
                    scheme="Bearer",
                    credentials="eyJhbGciOiJSUzI1NiIsImtpZCI6ImQ4OjkxOmFhOmI2OjdkOjRmOmViOjIyOmFiOmUzOmMwOjViOmY0Ojc4OjY0OjkyIiwidHlwIjoiSldUIn0.eyJhdWQiOltdLCJhenAiOiIwZWY4YWM1OTk4Nzk0MWE5OGQ5NTFlOGJiMjdjNDE3YiIsImJpbGxpbmciOnsiaGFzX3BheW1lbnRfZGV0YWlscyI6ZmFsc2UsIm9yZ19lbnRpdGxlbWVudHMiOm51bGwsInBsYW4iOnsiYWdyZWVtZW50X2lkIjpudWxsLCJjb2RlIjpudWxsLCJjcmVhdGVkX29uIjpudWxsLCJoYXNfdHJpYWxfcGVyaW9kIjpudWxsLCJpbnZvaWNlX2R1ZV9vbiI6bnVsbCwibmFtZSI6bnVsbCwicGxhbl9jaGFyZ2VfdHlwZSI6bnVsbCwidHJpYWxfZXhwaXJlc19vbiI6bnVsbH19LCJleHAiOjE3MTA0NTAwNjIsImlhdCI6MTcxMDM2MzY2MiwiaXNzIjoiaHR0cHM6Ly9jdXN0b21lcmZvcm1zZW5naW5lLmtpbmRlLmNvbSIsImp0aSI6IjE5NDIwMjExLWFkZmItNDU4Zi04ODhhLTdlYzZkODg0NzAyYSIsIm9yZ19jb2RlIjoib3JnX2NhM2ZhNjEwNmI5IiwicGVybWlzc2lvbnMiOltdLCJzY3AiOlsib3BlbmlkIiwicHJvZmlsZSIsImVtYWlsIiwib2ZmbGluZSJdLCJzdWIiOiJrcF9jYTJlOTI0ODcxOGQ0NzNkYjU2MTg4MWQ5NGU0ZjQ5OCJ9.Mmg04sGqCEkwPWw7BrZZCzqWJoa8FeJYc4cU9RnMMxpmYlpzwEOgLWKUVrh8RJjgpiSW0oUQNXpr6kX8p6GQj7IkNAmemnblxBp9yLaSVc7A-y0xwvJOHexKDtGEOdfVGATmhKoVyzYiZbPZj1EfeF_vL-JxwFLWA6R81eY_MC-gcg4WFDZBP4EXaxK4IiZTo7sqfx1_IP9AVesGeiSqLZUDSgcq47OoZBI7G8RyymJRfasHyhZY-bIxdqQs5lnF2olftrN3g52OzgW67cG6UaOqWkZXJBkt27uBFhL1Ebzx4zQT2x5NNv_1zOh31Fd-H9p_xFxXMxa_0tlXJDArTw",
                ),
                current_time=now(),
            )
        )


@pytest.mark.e2e()
async def test_all_ok_token() -> None:
    await lego_workflows.run_and_collect_events(
        handlers.auth.validate_token.Command(
            token=HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="eyJhbGciOiJSUzI1NiIsImtpZCI6ImQ4OjkxOmFhOmI2OjdkOjRmOmViOjIyOmFiOmUzOmMwOjViOmY0Ojc4OjY0OjkyIiwidHlwIjoiSldUIn0.eyJhdWQiOltdLCJhenAiOiIwZWY4YWM1OTk4Nzk0MWE5OGQ5NTFlOGJiMjdjNDE3YiIsImJpbGxpbmciOnsiaGFzX3BheW1lbnRfZGV0YWlscyI6ZmFsc2UsIm9yZ19lbnRpdGxlbWVudHMiOm51bGwsInBsYW4iOnsiYWdyZWVtZW50X2lkIjpudWxsLCJjb2RlIjpudWxsLCJjcmVhdGVkX29uIjpudWxsLCJoYXNfdHJpYWxfcGVyaW9kIjpudWxsLCJpbnZvaWNlX2R1ZV9vbiI6bnVsbCwibmFtZSI6bnVsbCwicGxhbl9jaGFyZ2VfdHlwZSI6bnVsbCwidHJpYWxfZXhwaXJlc19vbiI6bnVsbH19LCJleHAiOjE3MTA0NTAwNjIsImlhdCI6MTcxMDM2MzY2MiwiaXNzIjoiaHR0cHM6Ly9jdXN0b21lcmZvcm1zZW5naW5lLmtpbmRlLmNvbSIsImp0aSI6IjE5NDIwMjExLWFkZmItNDU4Zi04ODhhLTdlYzZkODg0NzAyYSIsIm9yZ19jb2RlIjoib3JnX2NhM2ZhNjEwNmI5IiwicGVybWlzc2lvbnMiOltdLCJzY3AiOlsib3BlbmlkIiwicHJvZmlsZSIsImVtYWlsIiwib2ZmbGluZSJdLCJzdWIiOiJrcF9jYTJlOTI0ODcxOGQ0NzNkYjU2MTg4MWQ5NGU0ZjQ5OCJ9.Mmg04sGqCEkwPWw7BrZZCzqWJoa8FeJYc4cU9RnMMxpmYlpzwEOgLWKUVrh8RJjgpiSW0oUQNXpr6kX8p6GQj7IkNAmemnblxBp9yLaSVc7A-y0xwvJOHexKDtGEOdfVGATmhKoVyzYiZbPZj1EfeF_vL-JxwFLWA6R81eY_MC-gcg4WFDZBP4EXaxK4IiZTo7sqfx1_IP9AVesGeiSqLZUDSgcq47OoZBI7G8RyymJRfasHyhZY-bIxdqQs5lnF2olftrN3g52OzgW67cG6UaOqWkZXJBkt27uBFhL1Ebzx4zQT2x5NNv_1zOh31Fd-H9p_xFxXMxa_0tlXJDArTw",
            ),
            current_time=datetime.datetime(
                year=2020, month=1, day=1, tzinfo=datetime.UTC
            ),
        )
    )
