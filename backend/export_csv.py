import io
import pandas as pd

def generate_csv(result_data):
    filename = result_data['filename']
    language = result_data['language']
    dc = result_data['dc']
    cc = result_data['cc']
    code = result_data['code']
    line_scores = result_data.get('line_dc_map', {})

    code_lines = code.split('\n')
    rows = []

    for i, line in enumerate(code_lines, start=1):
        rows.append({
            'Filename': filename,
            'Language': language,
            'Line Number': i,
            'Code Line': line.strip(),
            'Line DC Score': line_scores.get(i, 0),
            'Total DC': dc if i == 1 else '',
            'Total CC': cc if i == 1 else ''
        })

    df = pd.DataFrame(rows)
    csv_stream = io.StringIO()
    df.to_csv(csv_stream, index=False)
    csv_stream.seek(0)
    return io.BytesIO(csv_stream.read().encode())
