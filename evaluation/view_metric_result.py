import os
import sys
import json
import pandas as pd

from tqdm import tqdm
from collections import defaultdict


def aggregate_metrics(input_path, output_excel):
    model_stats = defaultdict(
        lambda: defaultdict(  # Model level
            lambda: {  # Language level
                'total_errors': 0,
                'total_tokens': 0,
                'ne_total_errors': 0,
                'ne_total_entities': 0,
                'total_h': 0,
                'ne_total_target': 0
            }
        )
    )

    with open(input_path, 'r') as f:
        for line in tqdm(f, desc="Processing lines"):
            data = json.loads(line.strip())
            language = data.get('language', 'UNKNOWN')
            for model, info in data['asr_info'].items():
                wer_info = info['wer_info']
                ne_wer_info = info['ne_wer_info']
                ne_fnr_info = info['ne_fnr_info']

                # Update WER stats
                model_stats[model][language]['total_errors'] += (
                    wer_info['I'] + wer_info['D'] + wer_info['S']
                )
                model_stats[model][language]['total_tokens'] += wer_info['T']
                # Update NE-WER stats
                model_stats[model][language]['ne_total_errors'] += (
                    ne_wer_info['I'] + ne_wer_info['D'] + ne_wer_info['S']
                )
                model_stats[model][language]['ne_total_entities'] += ne_wer_info['T']
                # Update NE-FNR stats
                model_stats[model][language]['total_h'] += ne_fnr_info['H']
                model_stats[model][language]['ne_total_target'] += ne_fnr_info['T']

    # Prepare results with separate columns for each language
    results = defaultdict(dict)
    for model in model_stats:
        for lang in model_stats[model]:
            stats = model_stats[model][lang]
            wer = (stats['total_errors'] / stats['total_tokens']) if stats['total_tokens'] else 0
            ne_wer = (stats['ne_total_errors'] / stats['ne_total_entities']) if stats['ne_total_entities'] else 0
            ne_fnr = (1 - stats['total_h'] / stats['ne_total_target']) if stats['ne_total_target'] else 0

            results[model][lang] = {
                "WER": round(wer, 4),
                "NE-WER": round(ne_wer, 4),
                "NE-FNR": round(ne_fnr, 4)
            }

    # Prepare separate data rows for Chinese and English
    zh_rows = []
    en_rows = []
    # Replace with your model names
    model_list = ["model1", "model1_coarse-grained", "model1_fine-grained", "model2", "model2_coarse-grained", "model2_fine-grained"]
    for model in model_list:
        if "Chinese" in results[model]:
            metrics = results[model]["Chinese"]
            zh_rows.append({
                "Model": model,
                "WER": f'{metrics["WER"] * 100:.2f}%',
                "NE-WER": f'{metrics["NE-WER"] * 100:.2f}%',
                "NE-FNR": f'{metrics["NE-FNR"] * 100:.2f}%'
            })
        if "English" in results[model]:
            metrics = results[model]["English"]
            en_rows.append({
                "Model": model,
                "WER": f'{metrics["WER"] * 100:.2f}%',
                "NE-WER": f'{metrics["NE-WER"] * 100:.2f}%',
                "NE-FNR": f'{metrics["NE-FNR"] * 100:.2f}%'
            })
    # Define common columns
    columns = ["Model", "WER", "NE-WER", "NE-FNR"]
    # Save to separate Excel files
    zh_excel = output_excel.replace(".xlsx", "_Chinese.xlsx")
    en_excel = output_excel.replace(".xlsx", "_English.xlsx")
    if zh_rows:
        df_zh = pd.DataFrame(zh_rows, columns=columns)
        df_zh.to_excel(zh_excel, index=False, engine='openpyxl')
    if en_rows:
        df_en = pd.DataFrame(en_rows, columns=columns)
        df_en.to_excel(en_excel, index=False, engine='openpyxl')

    # Console output remains the same for clarity
    print("Aggregated Results - Chinese:")
    for model in sorted(results.keys()):
        if "Chinese" in results[model]:
            metrics = results[model]["Chinese"]
            print(f"\nModel: {model}")
            print(f"  WER: {metrics['WER'] * 100:.2f}%")
            print(f"  NE-WER: {metrics['NE-WER'] * 100:.2f}%")
            print(f"  NE-FNR: {metrics['NE-FNR'] * 100:.2f}%")

    print("\nAggregated Results - English:")
    for model in sorted(results.keys()):
        if "English" in results[model]:
            metrics = results[model]["English"]
            print(f"\nModel: {model}")
            print(f"  WER: {metrics['WER'] * 100:.2f}%")
            print(f"  NE-WER: {metrics['NE-WER'] * 100:.2f}%")
            print(f"  NE-FNR: {metrics['NE-FNR'] * 100:.2f}%")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python view_metric_result.py <input.jsonl>")
        sys.exit(1)

    input_path = sys.argv[1]
    assert os.path.exists(input_path) and input_path.endswith(".jsonl"), "Input file is not a valid jsonl file!"
    output_excel = input_path.replace(".jsonl", ".xlsx")
    aggregate_metrics(input_path, output_excel)
