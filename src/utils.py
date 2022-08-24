def int_or_float(s):
    return int(float(s)) if float(s) % 1 == 0 else round(float(s), 9)


def span(style: str, s):
    return f'<span style="{style}">{s}</span>'
