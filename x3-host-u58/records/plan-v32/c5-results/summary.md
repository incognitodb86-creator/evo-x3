# quant-bench summary (2026-11-18 15:29:40)

Mean over runs, (min-max) across runs. Decode and prefill are client-side (stream timing), the same method for every engine.

## Speed

| Engine | Model | Runs | Load s | Cold prompt | Cold TTFT s | Prefill t/s | Decode t/s | Follow-up TTFT s | Draft accept |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Accuracy

Pass = problems solved per run. Per problem = runs that solved it. Think tokens and decode are per request; wall is per run.

| Engine | Model | Set | Runs | Pass mean | Best | Worst | Stdev | Per problem | Think tokens | Decode t/s | Wall min/run | Hit cap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| live | gufo-v2 | agent | 1 | 11.00/11 | 11/11 | 11/11 | - | cpp/bank-account 1/1, cpp/binary-search-tree 1/1, cpp/zebra-puzzle 1/1, go/alphametics 1/1, go/connect 1/1, go/dominoes 1/1, go/zebra-puzzle 1/1, rust/decimal 1/1, rust/macros 1/1, rust/poker 1/1, rust/xorcism 1/1 | - | - | 13.0 | 0 |
| live | halogen-v2 | agent | 1 | 9.00/11 | 9/11 | 9/11 | - | cpp/bank-account 1/1, cpp/binary-search-tree 1/1, cpp/zebra-puzzle 1/1, go/alphametics 0/1, go/connect 1/1, go/dominoes 1/1, go/zebra-puzzle 1/1, rust/decimal 1/1, rust/macros 1/1, rust/poker 1/1, rust/xorcism 0/1 | - | - | 27.0 | 0 |
