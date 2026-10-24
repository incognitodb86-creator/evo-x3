# PW1d SMOKE TEST - one Omni rewrite from the HC3 start still (no render)

- task: REF2AV | resolution 16:9 | duration 10.0 s (node snaps to the 243 f @ 24 fps grid) | greedy | seed 42
- reference: `community/hc/HC3_lesbian_beach.jpg` (the HC3 approved pick, the only reference)
- base: `Qwen2.5-Omni-7B GGUF Q4_K_M · 6.2 GB download · ~9 GB with the adapter and a 12k context`
- adapter: `on disk: MiniMax-H3-Prompt-Rewriter-LoRA-Omni-Q8_0.gguf [qwen2vl, 0.3 GB]`
- options: max_new_tokens 2048, temperature 0.7, top_p 0.8, top_k 20, repetition_penalty 1.05, n_ctx 8192, gpu_layers -1, auto_download **False** (a smoke test must fail, not fetch)
- prompt_id `8581a1ee-351e-4da5-8361-202a75ce6df1` | port 10004 | mode run
- window: 2026-10-24 12:36:40 -> 2026-10-24 12:37:01 CT = 0.3 min GPU
- text output only: no sampler, no DiT, no SaveVideo, no vision judge, no media file (check 9)

## The short prompt that went in

```
Use <Picture 1> for the beach scene and for the two adult women in it. The clip opens on them close and unhurried in the shallow surf at golden hour, the camera low and near, handheld with a slow drift in; warm rim light, wet skin, spray backlit. Adult fictional scene, two women, no one else in frame, the sound is the surf and their breathing.
```

## rewritten_prompt (the six fields the node produced)

```
subject_definitions:
<Subject 1> is the woman on the left in <Picture 1>, featuring long blonde hair, a red and black plaid bikini top, and black bikini bottoms with a red floral pattern.
<Subject 2> is the woman on the right in <Picture 1>, featuring long blonde hair, a pink bikini top with black trim, and black bikini bottoms with a pink geometric pattern.
<Subject 3> is the beach scene in <Picture 1>, featuring a sandy beach, shallow surf, and a distant coastal landscape under warm golden hour lighting.

summary:
[reference generation] The target video features <Subject 1> and <Subject 2> sitting close together on the sand of <Subject 3>. The camera slowly drifts in on them as they relax in the shallow surf at golden hour, with warm rim light highlighting their wet skin and the spray backlit by the sun.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - the target video features the same woman with long blonde hair, wearing the red and black plaid bikini top and black bikini bottoms with a red floral pattern.
<Subject 2> (appears in [Shot 1]): fully_preserved - the target video features the same woman with long blonde hair, wearing the pink bikini top with black trim and black bikini bottoms with a pink geometric pattern.
<Subject 3> (appears in [Shot 1]): fully_preserved - the target video takes place on the same sandy beach with shallow surf and a distant coastal landscape under warm golden hour lighting.

detailed_description:
The target video is in a realistic, cinematic style with warm golden hour lighting and a shallow depth of field.

[Shot 1] The shot opens on a low-angle, handheld camera positioned near the sand of <Subject 3>, a serene beach scene featuring a sandy beach, shallow surf, and a distant coastal landscape. In the center of the frame, <Subject 1> and <Subject 2> sit close together on the wet sand. <Subject 1>, on the left, wears a red and black plaid bikini top and black bikini bottoms with a red floral pattern. <Subject 2>, on the right, wears a pink bikini top with black trim and black bikini bottoms with a pink geometric pattern. The camera slowly drifts in on them, maintaining a low and intimate viewpoint. The warm golden hour light casts a soft rim light on their wet skin, highlighting the glistening texture of their hair and bodies. The shallow surf washes gently around their legs, with small sprays of water backlit by the sun. The women relax in the shallow water, their bodies leaning slightly toward one another in a quiet, unhurried moment. <Subject 1> rests her arm on the sand, while <Subject 2> leans forward, her gaze directed downward. The camera continues its slow, steady push-in, enhancing the intimate atmosphere. The audible soundscape consists entirely of the rhythmic, soothing sound of the surf washing over the sand and the soft, natural breathing of the two women, creating a peaceful and relaxing environment.

overall_soundscape:
The soundscape features the continuous, soothing sound of shallow surf washing over the sand, accompanied by the soft, natural breathing of the two women.

non_diegetic_music:
N/A
```

## Fields split out

### subject_definitions

<Subject 1> is the woman on the left in <Picture 1>, featuring long blonde hair, a red and black plaid bikini top, and black bikini bottoms with a red floral pattern.
<Subject 2> is the woman on the right in <Picture 1>, featuring long blonde hair, a pink bikini top with black trim, and black bikini bottoms with a pink geometric pattern.
<Subject 3> is the beach scene in <Picture 1>, featuring a sandy beach, shallow surf, and a distant coastal landscape under warm golden hour lighting.

### summary

[reference generation] The target video features <Subject 1> and <Subject 2> sitting close together on the sand of <Subject 3>. The camera slowly drifts in on them as they relax in the shallow surf at golden hour, with warm rim light highlighting their wet skin and the spray backlit by the sun.

### retention_analysis

<Subject 1> (appears in [Shot 1]): fully_preserved - the target video features the same woman with long blonde hair, wearing the red and black plaid bikini top and black bikini bottoms with a red floral pattern.
<Subject 2> (appears in [Shot 1]): fully_preserved - the target video features the same woman with long blonde hair, wearing the pink bikini top with black trim and black bikini bottoms with a pink geometric pattern.
<Subject 3> (appears in [Shot 1]): fully_preserved - the target video takes place on the same sandy beach with shallow surf and a distant coastal landscape under warm golden hour lighting.

### detailed_description

The target video is in a realistic, cinematic style with warm golden hour lighting and a shallow depth of field.

[Shot 1] The shot opens on a low-angle, handheld camera positioned near the sand of <Subject 3>, a serene beach scene featuring a sandy beach, shallow surf, and a distant coastal landscape. In the center of the frame, <Subject 1> and <Subject 2> sit close together on the wet sand. <Subject 1>, on the left, wears a red and black plaid bikini top and black bikini bottoms with a red floral pattern. <Subject 2>, on the right, wears a pink bikini top with black trim and black bikini bottoms with a pink geometric pattern. The camera slowly drifts in on them, maintaining a low and intimate viewpoint. The warm golden hour light casts a soft rim light on their wet skin, highlighting the glistening texture of their hair and bodies. The shallow surf washes gently around their legs, with small sprays of water backlit by the sun. The women relax in the shallow water, their bodies leaning slightly toward one another in a quiet, unhurried moment. <Subject 1> rests her arm on the sand, while <Subject 2> leans forward, her gaze directed downward. The camera continues its slow, steady push-in, enhancing the intimate atmosphere. The audible soundscape consists entirely of the rhythmic, soothing sound of the surf washing over the sand and the soft, natural breathing of the two women, creating a peaceful and relaxing environment.

### overall_soundscape

The soundscape features the continuous, soothing sound of shallow surf washing over the sand, accompanied by the soft, natural breathing of the two women.

### non_diegetic_music

N/A

## integrated_multimodal_description

```

```

## Objective checks

- PASS 1 subject_definitions
- PASS 2 summary
- PASS 3 retention_analysis
- PASS 4 detailed_description
- PASS 5 overall_soundscape
- PASS 6 non_diegetic_music
- PASS 7 rewritten_prompt >= 600 chars
- FAIL 8 the 10.0 s answer quotes the 243-frame grid
- PASS 9 no media file written under ComfyUI/output/community
- PASS 10 writer status completed without error

6/6 checks passed. Media files in the window: none

## ComfyUI console (the durable copy of a failure reason)

```
stamp [2026-10-24 12:36:0
[2026-10-24 12:36:06.533] !!! Exception during processing !!! Ref2AV describes how a target video reuses reference assets, so it needs at least one. Connect a picture, a clip or a sound -- or pick T2AV, which is the task written from text alone.
[2026-10-24 12:36:06.535] Traceback (most recent call last):
  File "C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\execution.py", line 547, in execute
    output_data, output_ui, has_subgraph, has_pending_tasks = await get_output_data(prompt_id, unique_id, obj, input_data_all, execution_block_cb=execution_block_cb, pre_execute_cb=pre_execute_cb, v3_data=v3_data)
                                                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\execution.py", line 352, in get_output_data
    return_values = await _async_map_node_over_list(prompt_id, unique_id, obj, input_data_all, obj.FUNCTION, allow_interrupt=True, execution_block_cb=execution_block_cb, pre_execute_cb=pre_execute_cb, v3_data=v3_data)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\execution.py", line 326, in _async_map_node_over_list
    await process_inputs(input_dict, i)
  File "C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\execution.py", line 314, in process_inputs
    result = f(**inputs)
             ^^^^^^^^^^^
  File "C:\Users\derek\HardcoreNSFW-TestRuntime\ComfyUI\comfy_api\internal\__init__.py", line 149, in wrapped_fu
```
