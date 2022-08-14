def int_or_float(s):
    return int(float(s)) if float(s) % 1 == 0 else float(s)


def span(style: str, s):
    return f'<span style="{style}">{s}</span>'
