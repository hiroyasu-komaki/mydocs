from datetime import datetime, timezone, timedelta


def get_jst_datetime_str() -> str:
    """
    JST（日本標準時）の現在日時を文字列で取得
    形式: YYYY-MM-DD HH:MM
    
    Returns:
        JSTの日時文字列（例: "2026-02-07 12:07"）
    """
    # JSTはUTC+9
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst)
    return now_jst.strftime('%Y-%m-%d %H:%M')
