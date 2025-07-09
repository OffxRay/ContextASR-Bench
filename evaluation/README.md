## Data Prepare  
We provide a pre-processed example file `example_asr_results.jsonl` containing model decoding results. The **asr_info** field stores decoding results from different ASR models under three Context Evaluation Settings. This example dataset will be used to demonstrate the evaluation process for calculating WER, NE-WER, and NE-FNR metrics.

## Evaluation Process  
Step 1: Tokenize the ground truth text `text` and ASR decoding results `asr_text`, then extract contained entities to prepare for metric calculations:
```shell
python3 prepare_asr_result_for_metrics.py example_asr_results.jsonl example_asr_results_prepared.jsonl
```  
Step 2: Calculate WER, NE-WER, and NE-FNR metrics for ASR decoding results:
```shell
python3 calculate_metrics.py example_asr_results_prepared.jsonl example_asr_results_metrics.jsonl
```  
Step 3: Aggregate calculation results to obtain final metrics on the example dataset and save to local file:
```shell
python3 view_metric_result.py example_asr_results_metrics.jsonl
```