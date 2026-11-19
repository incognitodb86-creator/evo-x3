# RAW SCRAPE: Are Minimax spicy loras ... a lie?
- URL: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/
- Author: u/North_Enthusiasm_331
- Created: 2026-09-09 11:08 CT (utc 1788970123)
- Score: 160 · num_comments field: 190 · scraped unique: 214
- Subreddit: r/StableDiffusion

## OP SELFTEXT
I know that the answer is ultimately no, and also that they're all still early in development ...

BUT I'm having a hard time getting the ones I find on civitai to produce anything resembling the examples. I follow generation guidelines where provided, and have even taken workflow settings from downloaded videos ... but they never seem to work very well. And if I try to add a lora to a sfw workflow that I'm happy with, the results look AWFUL. 

I've resorted to using wan generations as video references. 

Is i2v the best option? Does ref2va ever work? 

Any tips, recommendations, or resources you can recommend? Any else struggled with this? 

## ALL COMMENTS (threaded)
### u/bstr3k · p8rt79z · score 47 · 2026-09-09 11:17 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8rt79z/
Have you tried Eros? This is Tenstrip's model that hes been tweaking with. He's a wizard

[https://huggingface.co/TenStrip/10Eros-Max/tree/main?not-for-all-audiences=true](https://huggingface.co/TenStrip/10Eros-Max/tree/main?not-for-all-audiences=true)

People have been saying beta 5 version without the turbo integrated has been good, but you can try turbo if you'd like. It would be a drop in replacement for the H3 model since it started its life being tweaked from H3 

  ### u/[deleted] · p8rxq88 · score 1 · 2026-09-09 11:36 CT
  - parent: t1_p8rt79z · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8rxq88/
  [removed]

  ### u/WholeBrain9977 · p8s440v · score 16 · 2026-09-09 12:03 CT
  - parent: t1_p8rt79z · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s440v/
  The Eros model worked really well for me—using 8 steps and no additional LoRA. I do have one issue, though: for some reason, the model doesn't seem to strictly follow every detail of the reference when using Ref2VA mode. In specific areas—like the breasts—it tends to render a generic shape, likely derived from the training dataset. I have a workflow for a specific actress with a very distinctive breast shape; when I use a reference image of her in a "three-point" pose, the model simply forgets her actual breast shape and replaces it with a generic one bouncing. I haven't figured out a workaround for this yet. Additionally, I generated a POV-angle shot of her to use as a reference, but the model alters the pose to something similar—yet not identical—to the original image. I haven't found a solution for this either.

    ### u/FuckTheActualWhat · p8sdtaj · score 5 · 2026-09-09 12:45 CT
    - parent: t1_p8s440v · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sdtaj/
    I’m fairly certain that Eros is designed for fl2va rather than ref2va. Thats why its doesn’t do well in reference workflows. 

    ### u/emveor · p8smu8w · score 2 · 2026-09-09 13:23 CT
    - parent: t1_p8s440v · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8smu8w/
    Very distinct breast shape? Like... 5 breasts??   

      ### u/WholeBrain9977 · p8u9ebp · score 3 · 2026-09-09 17:41 CT
      - parent: t1_p8smu8w · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8u9ebp/
      Just a perfect perky breast. Like really round and teardrop nipple position. Like it's part of her identidy, so it's important, and the model messed up with this detail.

        ### u/qwertyop00 · p8vi6w9 · score 1 · 2026-09-09 21:35 CT
        - parent: t1_p8u9ebp · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vi6w9/
        That totally fictional actress, what does her full name rhyme with ?

      ### u/reeight · p8vus1m · score 3 · 2026-09-09 22:45 CT
      - parent: t1_p8smu8w · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vus1m/
      MMH3 doesn't do well with understanding 'puffy' for example.  When I prompt 'small', they look like a medium C-cup to me.  
      I end up using image character sheets or LoRAs.

        ### u/WholeBrain9977 · p8ypwxy · score 2 · 2026-09-10 10:00 CT
        - parent: t1_p8vus1m · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ypwxy/
        But the problem is that, even with a character sheet and a clear close-up image of the breasts for reference, the model fails to reproduce them accurately during rapid movement. It swaps the nipple for a larger one, and the breasts bounce the way ordinary breasts would. It’s as if the model has a strong bias regarding how breasts are supposed to behave—which is a shame, since in my case, they aren't natural breasts, and the nipple is supposed to be smaller.

          ### u/reeight · p931gb0 · score 2 · 2026-09-10 22:05 CT
          - parent: t1_p8ypwxy · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p931gb0/
          I guess a LoRA is needed then?

    ### u/tenowg2022 · p8sx599 · score 9 · 2026-09-09 14:06 CT
    - parent: t1_p8s440v · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sx599/
    I had the same issue with the base ref2va model, for some reason I had an off the wall idea, and asked grok, he recommended I use embedding for my reference descriptions, sure it was bs I tried it anyways, he gave me a custom node to generate the embedding. I use qwen locally to generate a very detailed description of about 200 words, pass that to the embedding and use that, and the results were impossible to ignore. if interested I could dump the code for the node and a screen of the workflow.

      ### u/LocoMod · p8t07e0 · score 3 · 2026-09-09 14:19 CT
      - parent: t1_p8sx599 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8t07e0/
      Go on...

        ### u/tenowg2022 · p8t46yy · score 20 · 2026-09-09 14:35 CT
        - parent: t1_p8t07e0 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8t46yy/
            import os
            import folder_paths
            import torch
            from safetensors.torch import save_file
            
            
            class SaveH3Embedding:
                @classmethod
                def INPUT_TYPES(cls):
                    return {
                        "required": {
                            "conditioning": ("CONDITIONING",),
                            "name": ("STRING", {"default": "minimaxh3_my_orbit"}),
                        }
                    }
            
            
                RETURN_TYPES = ("STRING",)
                RETURN_NAMES = ("path",)
                FUNCTION = "save"
                CATEGORY = "minimax_h3"
                OUTPUT_NODE = True
            
            
                def save(self, conditioning, name):
                    cond = conditioning[0][0]  # [1, N, 5120]
                    if cond.ndim == 3:
                        cond = cond[0]
                    # keep text-tagged rows if present
                    extra = conditioning[0][1] if len(conditioning[0]) > 1 else {}
                    tags = extra.get("minimax_token_tags")
                    if tags is not None:
                        tags = tags.reshape(-1)
                        # 1 = text modality in H3
                        mask = tags.cpu() == 1
                        if mask.any():
                            cond = cond[mask]
                    vec = cond.detach().float().cpu().contiguous()
                    folder = folder_paths.get_folder_paths("embeddings")[0]
                    os.makedirs(folder, exist_ok=True)
                    path = os.path.join(folder, f"{name}.safetensors")
                    save_file({"qwen3vl_32b": vec}, path)
                    return (path,)
            
            NODE_CLASS_MAPPINGS = {"SaveH3Embedding": SaveH3Embedding}
            NODE_DISPLAY_NAME_MAPPINGS = {"SaveH3Embedding": "Save MiniMax H3 Embedding"}
        
        https://preview.redd.it/ieush1wvpjoh1.png?width=977&format=png&auto=webp&s=2a0fc2064cc45fdaea5d43d1232ae443464f8f19
        
        Full prompt tailored to describing a nude reference model, I use character sheets and it handles it well:
        
            You are a master at extracting human details from images.
            You will describe the figure in the image you receive to extreme details. If the user supplies any text, organicly use that text to override your descriptions in a additive fashion.
            
            ## Include
            - face, eye, mouth
            - figure shape, demensions, fitness, etc
            - skin color and type
            - breast size and shape
            - areola size and shape
            - nipple size and shape
            - pelvic region description
            
            Once you have fully analysed the image, generate a concise summaried version, keeping it to 200 words or less.
            
            You will return only the concise summarized version, no padding text, no explaination, no additional words, only the concise summaried version as your response.
        
        then use the text: <Subject 1> from <Picture 1> embedding:minimaxh3\_test
        
        The node obviously goes into custom\_nodes in a \_\_init\_\_.py, good luck

          ### u/LocoMod · p8tk4ih · score 7 · 2026-09-09 15:43 CT
          - parent: t1_p8t46yy · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tk4ih/
          OP delivered. Hot dang!

          ### u/WholeBrain9977 · p8udbww · score 2 · 2026-09-09 18:02 CT
          - parent: t1_p8t46yy · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8udbww/
          You’ve already been a huge help so far, but would you mind sharing your creation method and what your character sheets look like?

            ### u/tenowg2022 · p8uhuxh · score 7 · 2026-09-09 18:25 CT
            - parent: t1_p8udbww · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8uhuxh/
            Yea, I will give you my workflow, no worries, just be aware I prepared this for LTX ingredients Lora, so it has alot nodes that are not required for a basic character sheet, it does save each step, and as you will see by the image it can be somewhat touchy with some characters, it likes to chop the top of the head off sometimes.
            
            https://preview.redd.it/n8qf6wtdwkoh1.png?width=2704&format=png&auto=webp&s=cc6999468f7cda8c099c78f7cc83b124b9fe169d
            
            that should work as a drag and drop, if not just give a shout and I will drop the json

              ### u/WholeBrain9977 · p8vnjbg · score -1 · 2026-09-09 22:04 CT
              - parent: t1_p8uhuxh · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vnjbg/
              Sorry, maybe I'm dumb, but can't make the drag and drop work.

            ### u/StandWorth9165 · p8wglou · score 3 · 2026-09-10 01:21 CT
            - parent: t1_p8udbww · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8wglou/
            This is the one I use and it doesnt cut the head off. [Krea 2 character sheets & Flux 2 Klein detailer : r/comfyui](https://www.reddit.com/r/comfyui/comments/1w6o357/krea_2_character_sheets_flux_2_klein_detailer/)
            

            ### u/StandWorth9165 · p8wgrkr · score 2 · 2026-09-10 01:22 CT
            - parent: t1_p8udbww · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8wgrkr/
            https://preview.redd.it/hkt1xjx0zmoh1.jpeg?width=1291&format=pjpg&auto=webp&s=4d9e01bc921b9c5da966dac43208d4f59d866a3f
            

            ### u/StandWorth9165 · p8wiskx · score 1 · 2026-09-10 01:39 CT
            - parent: t1_p8udbww · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8wiskx/
            There's also a very handy workflow involving a bunch of Pixaroma nodes. I don't know where I got it but it works to transfer clothing. But if you add a generic naked body to the clothing input and tweak the prompt a little you get a naked version of your character
            
            https://preview.redd.it/52fojcdr1noh1.jpeg?width=1490&format=pjpg&auto=webp&s=9543c2eb4c5a9bf329a6ccf02d734462f317c39c
            

          ### u/OrdinaryAward4498 · p8vp6ti · score 1 · 2026-09-09 22:13 CT
          - parent: t1_p8t46yy · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vp6ti/
          That’s Effy the succubus!

            ### u/tenowg2022 · p8vxj2x · score 2 · 2026-09-09 23:02 CT
            - parent: t1_p8vp6ti · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vxj2x/
            While very similar I can assure you it is a different character, similar taste I guess.

      ### u/LeKhang98 · p8wbcry · score 1 · 2026-09-10 00:40 CT
      - parent: t1_p8sx599 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8wbcry/
      Do you know why embeddings outperform raw text? Is this similar to text embeddings from the SD1.5 era? Can we use them for negative prompts too, or to help when a text prompt is too long?

        ### u/tenowg2022 · p8xfb0f · score 2 · 2026-09-10 06:03 CT
        - parent: t1_p8wbcry · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8xfb0f/
        It is the same idea as SD1.5 text embeddings, you are prepressing a chunk of text by a dedicated LLM that only works on exactly what you want it too then encoding it, the text\_encoder later doesn't need to even look at it. So I think it works better because the encoder has alot less clutter to filter through when it encodes your prompt. The amount of text you use is also vastly different, would you manually write 200+ words for every character reference? It is part detail part preprocessing, giving the text-encoder less to look at, and letting it work on your long winded prompt for the scene and just assuming the reference explain themselves.
        
        But I am no expert in this field, I didn't even have an idea of what creating an embedding looked like three day ago.

          ### u/LeKhang98 · p93ma02 · score 1 · 2026-09-11 00:25 CT
          - parent: t1_p8xfb0f · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p93ma02/
          Thank you that's an interesting idea.

          ### u/LeKhang98 · p93mba4 · score 1 · 2026-09-11 00:25 CT
          - parent: t1_p8xfb0f · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p93mba4/
          Thank you that's an interesting idea.

      ### u/cashcowman · p9elbkl · score 1 · 2026-09-12 14:06 CT
      - parent: t1_p8sx599 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p9elbkl/
      Yes please.

        ### u/tenowg2022 · p9elvj3 · score 1 · 2026-09-12 14:09 CT
        - parent: t1_p9elbkl · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p9elvj3/
        look down...

    ### u/rd180x · p8ulogf · score 3 · 2026-09-09 18:45 CT
    - parent: t1_p8s440v · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ulogf/
    Get the hybrid model with MysticXXX 

  ### u/DietAshamed2246 · p8wlwky · score 0 · 2026-09-10 02:04 CT
  - parent: t1_p8rt79z · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8wlwky/
  Unless I am confusing that model with some other one, Eros Max already has a turbo LoRA baked in.

    ### u/bstr3k · p8wy68p · score 1 · 2026-09-10 03:48 CT
    - parent: t1_p8wlwky · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8wy68p/
    beta 5 has one with turbo and one without (migth need to scroll down a little bit to see) 

      ### u/DietAshamed2246 · p8wyp1f · score 0 · 2026-09-10 03:53 CT
      - parent: t1_p8wy68p · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8wyp1f/
      I even had a chat argument with the maker over this addition of turbo LoRA into the model. He said it was necessary. Without the turbo baked in the model apparently was generating garbage, so he had to bake the turbo in the model. 

  ### u/hurrdurrimanaccount · p8x48rz · score 1 · 2026-09-10 04:40 CT
  - parent: t1_p8rt79z · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8x48rz/
  the model is a lie. it does not improve or enhance nsfw results at all. complete random seed variance at best.

  ### u/haremlifegame · p9b6mbi · score 1 · 2026-09-12 02:30 CT
  - parent: t1_p8rt79z · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p9b6mbi/
  Has he fixed the tongues/kissing/licking? That's minimax weakest point

### u/No-Zookeepergame4774 · p8rv5gd · score 17 · 2026-09-09 11:25 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8rv5gd/
As CivitAI has ramped up (real and virtual) monetization of models and and made money/paid forms of Buzz more essential for various services, more and more of the models on CivitAI of all types are deceptive vehicles for the creators to “earn” Buzz, and this definitely is even more true in whatever area is currently popular, especially for NSFW. So, yeah, its probably a particular problem right now for spicy H3 LoRAs. 

But, yeah, ref2va works pretty well with the stock model and ComfyUI workflows and the prompting guidelines published for Minimax H3. (I’ve also had good results with some of the hybrid models floating around, but I don’t have one clear favorite yet.)

  ### u/TheThoccnessMonster · p8rxxcn · score 8 · 2026-09-09 11:37 CT
  - parent: t1_p8rv5gd · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8rxxcn/
  As one of the top video LoRA creators on Civit, I can say that personally it’s not an easy model to get consistently good results with so many of us are still training vs. releasing stuff that “kind of works”. 

    ### u/North_Enthusiasm_331 · p8s9h5b · score 1 · 2026-09-09 12:26 CT
    - parent: t1_p8rxxcn · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s9h5b/
    Yeah I've seen a lot of comments about that, so I don't mean to complain about the current state. I have every confidence it will get better, and am excited about what's happening across the model/lora world. I'm just having a harder time making what exists work than with previous models, where I could get something decent and approximating the examples much easier.

    ### u/No-Zookeepergame4774 · p8sa92d · score 2 · 2026-09-09 12:29 CT
    - parent: t1_p8rxxcn · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sa92d/
    Yeah, from everything I’ve seen H3 is a hard model to work with for LoRA training. Which kind of exacerbates the problem on CivitAI, because hard to do good, honest models doesn’t make it any harder to do deceptive low-effort trash and outright scams, so the ratio of those to the good stuff is even higher than it otherwise would be. 

  ### u/Netsuko · p8ryyfq · score 26 · 2026-09-09 11:41 CT
  - parent: t1_p8rv5gd · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ryyfq/
  Some people want 15k buzz to download their models now. They can fuck right off. 

    ### u/Intelligent-Youth-63 · p8s0tm5 · score 18 · 2026-09-09 11:49 CT
    - parent: t1_p8ryyfq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s0tm5/
    They are universally not worth any amount of $$ in my opinion. And paywall gated is a tough way for people to find out. It’s not sustainable, because the people who are getting burned learn.
    
    That said, the right way IMO is to find people doing consistently good open source work and put your support dollars there.

      ### u/North_Enthusiasm_331 · p8s90zv · score 1 · 2026-09-09 12:24 CT
      - parent: t1_p8s0tm5 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s90zv/
      yeah, show me someone like Fox•Fur•Essence doing amazing work and making it available, and I'm way more willing to support

      ### u/rd180x · p8ulx1c · score 1 · 2026-09-09 18:47 CT
      - parent: t1_p8s0tm5 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ulx1c/
      Well it took them $$$ to train and these loras do work i haven't bought any though but i understand, saw someone list one for $800, these people don't understand how to sell 

        ### u/Netsuko · p917hp6 · score 0 · 2026-09-10 16:21 CT
        - parent: t1_p8ulx1c · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p917hp6/
        All AI models are literally trained on stolen data. Asking money for that is even worse. And safe for VERY few exceptions, none of these merged and trained models on civit are anywhere NEAR what it actually costs to train an actual full model. 

          ### u/No-Zookeepergame4774 · p91bkw5 · score 1 · 2026-09-10 16:41 CT
          - parent: t1_p917hp6 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p91bkw5/
          Basically no models are trained on literally stolen data; even to the extent that training may involve using intellectual property in violation of copyright or other IP rights that's not literally—or even in close metaphor to transgressions involving physical property—stealing but trespass (distinguished by the former depriving the owner of the property, while thr latter involves inauthorized use which does not deprive the owner of the property.)

    ### u/No-Zookeepergame4774 · p8s94fs · score 12 · 2026-09-09 12:24 CT
    - parent: t1_p8ryyfq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s94fs/
    15K? If only that were the extreme.
    
    https://preview.redd.it/6ovjbiq84joh1.jpeg?width=1005&format=pjpg&auto=webp&s=7493e96cb0eb8c4efd3dfe3b5dbde6dd50bf1ec3

    ### u/plHme · p8wlpuo · score 2 · 2026-09-10 02:02 CT
    - parent: t1_p8ryyfq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8wlpuo/
    I don’t like it either. Not because it’s bad to want money. But in this form of AI. **Sharing** is the answer.

  ### u/Bad_Trader_Bro · p8sfn0f · score 7 · 2026-09-09 12:52 CT
  - parent: t1_p8rv5gd · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sfn0f/
  yeah that's fucking ridiculous. Some of us creators do it for the love of the game, and to help others learn so that we can see more models.

  ### u/Choowkee · p8uvavu · score 1 · 2026-09-09 19:36 CT
  - parent: t1_p8rv5gd · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8uvavu/
  What does the monetizationg changes have to do with Lora quality...? It seems like you just *really* wanted to rant about Civit.
  
  Early LTX 2.0/WAN Loras had the exact same issue where they were underbaked plus training H3 is much harder than LTX.

    ### u/No-Zookeepergame4774 · p8xazgu · score 1 · 2026-09-10 05:32 CT
    - parent: t1_p8uvavu · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8xazgu/
    \>What does the monetization have to do with Lora quality...? 
    
    It incentivizes deceptive spam, both because the shift to require paid-for buzz for more functions gives more incentive to acquire paid-for buzz (green/yellow, depending on SFW/NSFW uses), and because the changes to creator monetization options create more opportunities to turn deceptive spam into paid-for forms of buzz.
    
    \> This just sounds like an excuse to rant about the recent changes on Civit.
    
    Sure, if you ignore that actions have consequences.
    
    \> What "essential services" are there on Civit that are gatekept with buzz? 
    
      
    I didn't say anything about essential services, I said paid-for buzz was made more essential for existing services. There is a difference about requiring paid-for forms of buzz for services which did not previously require it and (e.g., NSFW generation on [civitai.red](http://civitai.red), which previously could use blue buzz but is now restricted to yellow for non-members) -- making it essential for those services -- and the services themselves being "essential". 
    
     

### u/Significant-Baby-690 · p8rv9u2 · score 10 · 2026-09-09 11:26 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8rv9u2/
Mystic is decent and there is new one today M3 unlocked. Also seems to be decent.

I2V is certainly the way though. Eros as a base model is good too, but the image quality is not too good, sound is even worse, and you can't change the weights. IMHO the base model with Mystic on 0.5 and some concept specific lora based on the scene is the best now.

  ### u/badswagmuffins · p8rx3do · score 1 · 2026-09-09 11:34 CT
  - parent: t1_p8rv9u2 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8rx3do/
  Have you compared Mystic to HMNSFW motion?
  
  I am at a cross between the two. I feel like Mystic keeps giving my characters high pitch voices 

    ### u/Significant-Baby-690 · p8ry1pu · score 5 · 2026-09-09 11:38 CT
    - parent: t1_p8rx3do · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ry1pu/
    HMNSFW is imho way weaker. But it's really hard to judge, each model knows something .. and is ignorant about other stuff. Also the spread between seeds is wild. You can get one superb video .. and then 10 trash ones. Video testing sucks ..

  ### u/ArdascesIV · p8sk3aq · score 2 · 2026-09-09 13:11 CT
  - parent: t1_p8rv9u2 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sk3aq/
  M3 unlocked? 

  ### u/rd180x · p8vu6o1 · score 3 · 2026-09-09 22:41 CT
  - parent: t1_p8rv9u2 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vu6o1/
  facts eros is trash for quality

    ### u/Significant-Baby-690 · p8x885p · score 1 · 2026-09-10 05:12 CT
    - parent: t1_p8vu6o1 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8x885p/
    Hm .. it seems it's mainly issue with low res and the non-turbo model. Turbo model, 8-10 steps, bump the res a bit, like 720p and it's ok. It's actually one of the better turbos. Not good for non-nsfw though, it does weird stuff to clothing.

      ### u/rd180x · p8y2u5u · score 2 · 2026-09-10 08:15 CT
      - parent: t1_p8x885p · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8y2u5u/
      I mean it's not as realistic like Hybrid + MysticXXX, i ran 1mp 15s on rtx 6000 pro on runpod, 2k images

### u/boriskarloff83 · p8rvivg · score 8 · 2026-09-09 11:27 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8rvivg/
partly. authors rarely post their exact settings, resolution, if they used reference images to produce their samples, etc. and in some cases, most of the magic you can see in the samples is actually the prompt instead of the lora itself. need more 'without lora|with lora'. sorry, no recommendations. still looking for decent loras for downstair parts myself

### u/Chiduk99 · p8rwhit · score 53 · 2026-09-09 11:31 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8rwhit/
follow my setup.

Hybrid B30-49 with VBVR H3 + MysticXXX + Turbo Dareties 4to8 Step v1.0.

Set VBVR to 1.0, MysticXXX to 0.5 for general use or 0.8–1.0 for NSFW, and Turbo to 0.8.

Use Euler Simple as the sampler with 8 steps.

I’ve been generating R2V NSFW with this setup, and the results have been pretty good.

for prompt, use Grok or if you want to run LLM on PC use this model: Gemma4-26B-A4B-QAT-Uncensored-HauhauCS-Balanced-Q4\_K\_M

  ### u/NeverLucky159 · p8ry2bd · score 3 · 2026-09-09 11:38 CT
  - parent: t1_p8rwhit · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ry2bd/
  Is that LLM good for coding as well? Claude is way too expensive 

    ### u/Netsuko · p8rymnj · score 16 · 2026-09-09 11:40 CT
    - parent: t1_p8ry2bd · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8rymnj/
    I believe Qwen is kind of considered the best local LLM for coding while models like Gemma are much better at English creative writing and expression since their base language is not Chinese like Qwen.   
    Qwen is known to follow directions more strictly which is what you want in coding but not necessarily for creative writing/descriptions. 

      ### u/Free_Pressure8623 · p8sapys · score 6 · 2026-09-09 12:31 CT
      - parent: t1_p8rymnj · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sapys/
      A trick I do it make Gemma write me the prompt and break out the story/scenes. Then QWEN builds it into the structure for H3. Maybe it's overkill but I'm lazy and hate writting prompts. 

      ### u/Murky-Relation481 · p8u9ivh · score 5 · 2026-09-09 17:42 CT
      - parent: t1_p8rymnj · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8u9ivh/
      I've found latest Qwen is significantly better at writing dirty prompts than Gemma which tends to use more literary prose and euphemisms which doesn't help in most situations.

        ### u/Netsuko · p8uizsv · score 2 · 2026-09-09 18:31 CT
        - parent: t1_p8u9ivh · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8uizsv/
        Are you talking about Qwen 3.8 flash next? I managed to get an iQ4\_XS quant running on my system.. barely... i might have to take another look at it's writing capabilities.

          ### u/Murky-Relation481 · p8ujjry · score 2 · 2026-09-09 18:34 CT
          - parent: t1_p8uizsv · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ujjry/
          I am using [the full 27B 3.8 abliterated model](https://ollama.com/huihui_ai/Qwen3.8-abliterated). I do have a 4090 though, it fits fully in VRAM with a 32k context window.

            ### u/Netsuko · p8ul83a · score 4 · 2026-09-09 18:43 CT
            - parent: t1_p8ujjry · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ul83a/
            Oh, yeah, I should have that model somewhere. Currently messing around with the flash next version, it's around 90GB but it actually does run on a 4090+64GB ram. I'm actually curious how it's writing capabilities are. 

            ### u/Netsuko · p8uln9e · score 3 · 2026-09-09 18:45 CT
            - parent: t1_p8ujjry · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8uln9e/
            [https://huggingface.co/orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF](https://huggingface.co/orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF)

    ### u/Chiduk99 · p8ryprs · score 11 · 2026-09-09 11:40 CT
    - parent: t1_p8ry2bd · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ryprs/
    Depends on what kind of “coding” you’re doing, but if your PC is good enough, I recommend using Qwen3.8-27B-GGUF.

      ### u/boxthrowaway2026 · p8sjk4v · score 2 · 2026-09-09 13:09 CT
      - parent: t1_p8ryprs · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sjk4v/
      >Qwen3.8-27B-GGUF.
      
      Unsloth version or something else?

        ### u/reeight · p8vwa4k · score 1 · 2026-09-09 22:54 CT
        - parent: t1_p8sjk4v · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vwa4k/
        The new v3 of Unsloth's GUFF is the best baseline IMHO.  
        But you might get more milage from exotic custom engines+quant
        
        [https://github.com/syv-ai/qwen38-27b-rtx3090](https://github.com/syv-ai/qwen38-27b-rtx3090)  
        [https://github.com/0xSero/qwen38-3090-sglang](https://github.com/0xSero/qwen38-3090-sglang)  
        [https://github.com/turboderp-org/exllamav3](https://github.com/turboderp-org/exllamav3)

    ### u/ibringthehotpockets · p8s38qw · score -5 · 2026-09-09 11:59 CT
    - parent: t1_p8ry2bd · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s38qw/
    If you are fed up with a $20-100 subscription price you 1000% cannot afford the sheer hardware to run ANY top coding model that rivals even sonnet. Unfortunately this is the reality for now. With how distillation is going I would expect this to become more accessible to consumers in 2027. Still will definitely need a robust unified memory setup regardless. I can’t imagine V/RAM prices will drop any significant margin in the near future. 

      ### u/Cautious_Chicken_604 · p8sdf2b · score 6 · 2026-09-09 12:43 CT
      - parent: t1_p8s38qw · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sdf2b/
      I'd wager a lot of people on this sub already have at least 16GB VRAM or more. 
      
      $100 a month subscription is a lot when you consider it's $1200 a year. You could buy a 5070 Ti instead. You can run Qwen3.8-27B IQ3_S at 120k context length. It's definitely good enough to code stuff for comfy if you prime it with the right context. Heck 
      you could buy two ARC A770s and run them under llama.cpp Vulkan for combined 32GB VRAM which lets you run Qwen3.8-27B at Q6~Q8 depending on context length. It's a seriously capable model. 
      
      Especially if you were on a max plan paying $200 a month like some people are. That's $2400 a year. Prior to Qwen3.8-27B I never had much faith in local models for coding but it all changed with that one. It was like the Opus 4.5 release kind of moment for me. Now I'm hardware maxing , so I can have one GPU for comfy, and the rest for local LLMs.

        ### u/ibringthehotpockets · p8sondh · score 1 · 2026-09-09 13:30 CT
        - parent: t1_p8sdf2b · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sondh/
        Highly disagree about native capability but yea it’s a fair assumption most have 16gb. assuming the absolute best case for qwen models and assuming they aren’t bench maxed in the slightest (they are which is fine), capability is light years away from fable or Astra or sol or opus 4.8
        
        That being said there’s a big distinction. In the right hands qwen is useful, but absolutely **not** if a non developer is expecting to get a similar vibe code experience on big projects. Codex and Claude have trained models on specifically breaking down user intent into architecture in a masterful way. Which is why we can get the crazy one shots from the simplest prompts “make a pretty and useful budgeting app for me” actually leads to something coherent. 
        
        Local models will get there within a year IMO and I’m absolutely excited. Anthropic and OpenAI will more than likely have IPOd by that point and will stop shelling out billions of $ of compute on kids asking a frontier model what color the sky is. But it’s useful for them to keep for the training data for now. They’re just eating a huge temporary loss while at it. We’re in the right spot when local models touch down and I’m sure some companies will optimize the hell out of models and get the same easy user experience for a tiny fraction of the cost. For those of us who have setups and the knowledge, we will hopefully be running some super cool agentic setups 

          ### u/Cautious_Chicken_604 · p8vjgd3 · score 1 · 2026-09-09 21:42 CT
          - parent: t1_p8sondh · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vjgd3/
          This is cope.
          
          Qwen3.8-27B was the moment you're talking about. Qwen4 will be even better.
          
          It's capable of pretty epic one shots on modest hardware:
          
          https://www.reddit.com/r/LocalLLaMA/comments/1w4821c/qwen_38_27b_q4km_oneshot_a_super_mario_clone/
          
          If you use a SOTA for only the planning phase you have a really damn capable model:
          
          https://www.reddit.com/r/LocalLLaMA/comments/1waz5a0/qwen_38_27b_with_pi_agent_pushed_to_its_3d/
          
          Everyone who can afford to do this hobby has access to this. Judging on oneshot performance is silly when agents can iterate and debug. 
          
          Anyone who can actually operate ConfyUI has enough brainpower to pull this off.

        ### u/desktop4070 · p8vtmwg · score 1 · 2026-09-09 22:38 CT
        - parent: t1_p8sdf2b · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vtmwg/
        I have a 5070 Ti, but some of the smaller quants for 27B on LM Studio have been really slow for me. Can you link the one that worked fairly fast for you?

      ### u/NeverLucky159 · p8thjlc · score 1 · 2026-09-09 15:32 CT
      - parent: t1_p8s38qw · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8thjlc/
      I have RTX 4090 and 128GB RAM, I don't have to spend anything 

    ### u/PeterTheMeterMan · p8s891p · score 3 · 2026-09-09 12:21 CT
    - parent: t1_p8ry2bd · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s891p/
    It's not really coding skill that you get with Claude (or the latest GPT models like SOL/Astra), it's that they know ComfyUI inside and out. Being a top model in coding doesn't necessarily lend well to coding a Comfy node - there are lots of pitfalls. It's only recently that even the premiere models really had a grasp of coding for Comfy specifically.

      ### u/Cautious_Chicken_604 · p8s9yja · score 2 · 2026-09-09 12:28 CT
      - parent: t1_p8s891p · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s9yja/
      That's if you let them go off only what's in their training data about how ComfyUI works. You can get a local model to clone the source code, read through and understand it and THEN start coding, and it'll do wayyy better. 

    ### u/Kukipapa · p8scigh · score 2 · 2026-09-09 12:39 CT
    - parent: t1_p8ry2bd · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8scigh/
    For smaller coding tasks try some Qwen 3.8 quant,  configured by a Claude client as custom model.
    
    I live tested writing a small Python app on a 16 GB VRAM 5080 locally, it exceeded my expectations for speed and correctness compared to previous models (Gemma, Qwen 3.6 etc.)
    
    It won’t compete with real Claude but it can be an absolutely usable assistant running locally, free.

    ### u/rd180x · p8ulhd5 · score 2 · 2026-09-09 18:44 CT
    - parent: t1_p8ry2bd · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ulhd5/
    Lmao 

  ### u/rheylew · p8scbbz · score 1 · 2026-09-09 12:38 CT
  - parent: t1_p8rwhit · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8scbbz/
  What is your vram and system ram? And do you have any vids I can check out, I'm in the same boat trying to learn a consistent workflow..

  ### u/realmfan56 · p8sj6uh · score 2 · 2026-09-09 13:07 CT
  - parent: t1_p8rwhit · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sj6uh/
  Can you share your workflow for this, please?

  ### u/Link1227 · p8sw0mg · score 1 · 2026-09-09 14:01 CT
  - parent: t1_p8rwhit · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sw0mg/
  Thanks for sharing.

  ### u/jankies11 · p8th2om · score 1 · 2026-09-09 15:30 CT
  - parent: t1_p8rwhit · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8th2om/
  Abliterated or standard vae? 

    ### u/PumpkinLeather8421 · p8w1erp · score 0 · 2026-09-09 23:27 CT
    - parent: t1_p8th2om · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8w1erp/
    Uh… broken bot?

  ### u/rd180x · p8ulka3 · score 1 · 2026-09-09 18:45 CT
  - parent: t1_p8rwhit · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ulka3/
  Yeah i am on this but Turbo to 0.5

  ### u/Corleone11 · p8xs807 · score 1 · 2026-09-10 07:20 CT
  - parent: t1_p8rwhit · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8xs807/
  > Turbo Dareties 4to8 Step v1.0
  Can you provide a link for the Dareties turbo lora you're using. I've lost a bit the oversight since there are so many turbo loras.

    ### u/Chiduk99 · p8xw785 · score 1 · 2026-09-10 07:42 CT
    - parent: t1_p8xs807 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8xw785/
    [https://huggingface.co/Rkss/Minimax\_h3\_fl2v\_lightx2v\_turbo\_4to8step\_v0.1-v1.0\_768p\_v4\_step600\_dareties\_fro095\_native/tree/main](https://huggingface.co/Rkss/Minimax_h3_fl2v_lightx2v_turbo_4to8step_v0.1-v1.0_768p_v4_step600_dareties_fro095_native/tree/main)

      ### u/Corleone11 · p8y1w4o · score 1 · 2026-09-10 08:10 CT
      - parent: t1_p8xw785 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8y1w4o/
      Many thanks!

### u/DjMesiah · p8ryxqx · score 87 · 2026-09-09 11:41 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ryxqx/
The secret to H3 is that you don’t actually need Lora’s for excellent spicy content.  All can be done with image references.  It’s actually wild

  ### u/North_Enthusiasm_331 · p8rzlyv · score 8 · 2026-09-09 11:44 CT
  - parent: t1_p8ryxqx · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8rzlyv/
  do you starting images, or references for particular acts, shall we say? does that mean generating consistent images as various "milestones" for a video (beginning, middle parts, end) and then generating accordingly? or can subject references be independent of other image references that direct the action? 

    ### u/DjMesiah · p8s069o · score 96 · 2026-09-09 11:46 CT
    - parent: t1_p8rzlyv · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s069o/
    H3 knows a lot of the actions already, so the images just basically tell it poses and genitalia.  If you want, I can work on cleaning up my workflow and sharing it but it’ll take a couple hours before I’m able

      ### u/StrawHatTebo · p8s0wze · score 10 · 2026-09-09 11:50 CT
      - parent: t1_p8s069o · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s0wze/
      you'd be a legend

        ### u/DjMesiah · p8sdc90 · score 13 · 2026-09-09 12:43 CT
        - parent: t1_p8s0wze · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sdc90/
        Ok I’ll work on it along with some instructions, promise I’ll send by end of the day (midnight ET zone)

          ### u/ErenYeager91 · p8snkrf · score 1 · 2026-09-09 13:26 CT
          - parent: t1_p8sdc90 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8snkrf/
          damn that's cool

          ### u/LeftHandedToe · p8srifm · score 3 · 2026-09-09 13:42 CT
          - parent: t1_p8sdc90 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8srifm/
          lol years of cat posts, the horrors they must've seen as you work with your models. 

          ### u/SignificantSuit7876 · p8swezx · score 1 · 2026-09-09 14:03 CT
          - parent: t1_p8sdc90 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8swezx/
          Can I have it too!?

          ### u/Dull_Celebration5958 · p8sxadd · score 1 · 2026-09-09 14:06 CT
          - parent: t1_p8sdc90 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sxadd/
          Would love to see this as well!

            ### u/DjMesiah · p8sz6il · score 1 · 2026-09-09 14:14 CT
            - parent: t1_p8sxadd · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sz6il/
            Edited my comment above

          ### u/Ordinary_Weekend_333 · p8ubiac · score 1 · 2026-09-09 17:52 CT
          - parent: t1_p8sdc90 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ubiac/
          This looks very cool. Testing it out now. 

            ### u/DjMesiah · p8uimfe · score 1 · 2026-09-09 18:29 CT
            - parent: t1_p8ubiac · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8uimfe/
            It’d be cool to know how user friendly (or not) it winds up being cause I have no clue

              ### u/Ordinary_Weekend_333 · p8ukqll · score 1 · 2026-09-09 18:40 CT
              - parent: t1_p8uimfe · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ukqll/
              I might be a good test case then, because I'm brand new to all this and have no idea what I'm doing. 😄

                ### u/DjMesiah · p8ur9u3 · score 1 · 2026-09-09 19:15 CT
                - parent: t1_p8ukqll · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ur9u3/
                It’ll probably generate something weird but I can send you the final prompt because the workflow outputs that to a .txt by default 

                ### u/DjMesiah · p8urnst · score 1 · 2026-09-09 19:17 CT
                - parent: t1_p8ukqll · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8urnst/
                Also maybe just try any other text encoder, it can be anything that work as an image analyzer llm 

                ### u/DjMesiah · p8ut4y4 · score 2 · 2026-09-09 19:25 CT
                - parent: t1_p8ukqll · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ut4y4/
                I added the full prompt as a .txt to the drive for those that need to bypass the prompt enhancer for now.  I suspect you need a prerequisite of some kind.  If you didn’t already, I recommend just doing a fresh install via Easy Install because it should install all needed prerequisites automatically.  (I think)

                  ### u/Ordinary_Weekend_333 · p8utz7v · score 1 · 2026-09-09 19:29 CT
                  - parent: t1_p8ut4y4 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8utz7v/
                  Haha yeah, it generated a pretty weird video. It worked though! I will check another encoder and the full prompt. Thanks!

        ### u/DjMesiah · p8sz3c4 · score 2 · 2026-09-09 14:14 CT
        - parent: t1_p8s0wze · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sz3c4/
        Edited my comment above

      ### u/z3rO_1 · p8s3tof · score 7 · 2026-09-09 12:02 CT
      - parent: t1_p8s069o · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s3tof/
      Man, I would like to see the workflow. When I tried I2V I get whiggling tentacles instead of genitalia, lol.

        ### u/DjMesiah · p8sz4mg · score 1 · 2026-09-09 14:14 CT
        - parent: t1_p8s3tof · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sz4mg/
        Edited my comment above

      ### u/Illustrious_Ant_9242 · p8sbvqu · score 8 · 2026-09-09 12:36 CT
      - parent: t1_p8s069o · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sbvqu/
      I felt like it struggles a bit.. it would pop a dick off like it's a strap on dildo, or depict cum like it's gallons of milk 

        ### u/DjMesiah · p8sz5l6 · score 2 · 2026-09-09 14:14 CT
        - parent: t1_p8sbvqu · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sz5l6/
        Edited my comment above

      ### u/tehorhay · p8t30cu · score 1 · 2026-09-09 14:30 CT
      - parent: t1_p8s069o · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8t30cu/
      Neat

      ### u/Opening_Pizza_9428 · p8tjksk · score 2 · 2026-09-09 15:40 CT
      - parent: t1_p8s069o · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tjksk/
      Not every hero wears a cape ..

        ### u/DjMesiah · p8tk71l · score 3 · 2026-09-09 15:43 CT
        - parent: t1_p8tjksk · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tk71l/
        Sometimes your community needs you 

      ### u/ThaSipah · p8tzs51 · score 1 · 2026-09-09 16:54 CT
      - parent: t1_p8s069o · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tzs51/
      Excellent. 

      ### u/Le_Singe_Nu · p8u3h0p · score 2 · 2026-09-09 17:12 CT
      - parent: t1_p8s069o · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8u3h0p/
      I love how you create a complex NSFW workflow and then say "mf'kers" in the commentary doc.
      
      I think most people who would download the workflow can handle a bit of swearing! ;)

        ### u/DjMesiah · p8u7uck · score 4 · 2026-09-09 17:33 CT
        - parent: t1_p8u3h0p · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8u7uck/
        I added an exclamation point but that is as far as I’ll go

      ### u/rd180x · p8ulba3 · score 3 · 2026-09-09 18:43 CT
      - parent: t1_p8s069o · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ulba3/
      I use the same hybrid, btw you can skip image caption, just write generic: 
      Subjectvm: man fully_preserved: same expression, etc
      
      Will still work

        ### u/DjMesiah · p8ur2gj · score 1 · 2026-09-09 19:14 CT
        - parent: t1_p8ulba3 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ur2gj/
        Good to know.  I may have way overdone the reference prompting just trying to figure out how it works 

    ### u/grrrwoofwoof · p8uotpy · score 1 · 2026-09-09 19:02 CT
    - parent: t1_p8rzlyv · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8uotpy/
    Use ref2va without starting image unless you really want to animate a scene. Use this to create proper prompt. 

  ### u/TriuneTraveler · p8s9rvr · score 5 · 2026-09-09 12:27 CT
  - parent: t1_p8ryxqx · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s9rvr/
  how do you avoid people looking plastic and oversaturated? it never looks like the reference , too cartoonish 

    ### u/Important-Radish-722 · p8t3fyl · score 3 · 2026-09-09 14:32 CT
    - parent: t1_p8s9rvr · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8t3fyl/
    That's very controllable with the prompt, and steps.
    And, big hint- if you provide a room ref (r2v) H3 will take that into account when generating characters. 

    ### u/DietAshamed2246 · p8wzdo2 · score 1 · 2026-09-10 03:59 CT
    - parent: t1_p8s9rvr · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8wzdo2/
    Someone found a solution for that. It's on Reddit somewhere. The solution for removing the over-contrast and plasticy skin is to add 2 extra nodes of latent upscale. I don't know if it works, but the posted samples looked good. Here, check this out: https://www.reddit.com/r/StableDiffusion/s/QauNe53mMt

  ### u/newaccount47 · p8t0fdp · score 5 · 2026-09-09 14:20 CT
  - parent: t1_p8ryxqx · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8t0fdp/
  Dude I've gotten nightmare fuel even with images. Do you not get that? 

    ### u/Ordinary_Weekend_333 · p8u4uyy · score 1 · 2026-09-09 17:18 CT
    - parent: t1_p8t0fdp · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8u4uyy/
    Haha, yeah, I've made some disturbing shit somewhere between horror movie and adult film on accident. 

    ### u/Yasstronaut · p8v62o6 · score 1 · 2026-09-09 20:31 CT
    - parent: t1_p8t0fdp · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8v62o6/
    Just don’t use the ref2va model. Use the same workflow with the fl2va workflow and it works way better. Or a hybrid model 

      ### u/newaccount47 · pag0ybp · score 1 · 2026-09-17 15:46 CT
      - parent: t1_p8v62o6 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/pag0ybp/
      I was using ref2va. the ref was a full image of the full person. Perhaps the issue was that there was no close up ref images of the parts that I waned to have zoomed in on in the video? 

  ### u/JesusShaves_ · p8t0wr9 · score 1 · 2026-09-09 14:22 CT
  - parent: t1_p8ryxqx · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8t0wr9/
  This is true. You can try the loras but they don't help much and you don't actually need them. H3 really hasn't ever censored anything I've tried to create. It has some problems with realistic genitals sometimes but that's the worst of it.

    ### u/DjMesiah · p8t1k3i · score 5 · 2026-09-09 14:24 CT
    - parent: t1_p8t0wr9 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8t1k3i/
    Correct, it’s only the genitals that need references

      ### u/QuirksNFeatures · p8uz8k3 · score 2 · 2026-09-09 19:56 CT
      - parent: t1_p8t1k3i · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8uz8k3/
      Every time someone has said something like this and I've actually gotten an example video from them, it was severely lacking.  
      
      And with this workflow there's too much to download for me to fuck around with until I see examples.

        ### u/DjMesiah · p8v1sdz · score 2 · 2026-09-09 20:09 CT
        - parent: t1_p8uz8k3 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8v1sdz/
        I’ll put an example video into the folder

          ### u/QuirksNFeatures · p8v2763 · score 1 · 2026-09-09 20:12 CT
          - parent: t1_p8v1sdz · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8v2763/
          I would appreciate it.  I'd love to be wrong about this.

            ### u/DjMesiah · p8v3ihg · score 1 · 2026-09-09 20:18 CT
            - parent: t1_p8v2763 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8v3ihg/
            My personal favorite is people who post Lora’s where the examples they provide look horrible.  It’s convenient for knowing to skip it.  

          ### u/QuirksNFeatures · p8v3r22 · score 2 · 2026-09-09 20:19 CT
          - parent: t1_p8v1sdz · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8v3r22/
          Okay her face makes her look like a child.  Like 12 years old.  That is not cool, man.
          
          Other than that, still not good enough.  Doesn't look natural.

            ### u/DjMesiah · p8v43dy · score 1 · 2026-09-09 20:21 CT
            - parent: t1_p8v3r22 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8v43dy/
            Seriously? I’ll change the source image then, I did not think that was an issue 

              ### u/QuirksNFeatures · p8v4pmd · score 2 · 2026-09-09 20:24 CT
              - parent: t1_p8v43dy · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8v4pmd/
              As far as I'm concerned, it's not a real person.  There's no victim.  I don't care about that. But everyone should decide that for themselves and with not even a thumbnail or anything, people are going to download that and be very unhappy.

                ### u/DjMesiah · p8v652o · score 1 · 2026-09-09 20:32 CT
                - parent: t1_p8v4pmd · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8v652o/
                I get your point but it’s also why people refrain from sharing nsfw workflows, in the end it’s not worth it

                  ### u/QuirksNFeatures · p8v9tv1 · score 1 · 2026-09-09 20:51 CT
                  - parent: t1_p8v652o · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8v9tv1/
                  The workflow is just a workflow.  No reasonable person would have an issue with that.  It's the files you put into the workflow that would get some people in a twist.  I'm just saying maybe don't spring that on people.  If they could see a thumbnail and say "oh okay not for me", but no thumbnails on google drive. 
                  
                  Either way, if you changed it that's great.  
                  
                  Anyway aside from the age of the girl, it was pretty good.  Don't let me discourage you.  I'm sure a lot of people will be happy with your workflow.  It's just not what I'm looking for.  I feel like I get better results with the loras in I2V, and even when using the regular model as a reference model.  It's not usually easy but I get there.  Most of the time.

                    ### u/DjMesiah · p8vbnb5 · score 1 · 2026-09-09 21:00 CT
                    - parent: t1_p8v9tv1 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vbnb5/
                    Well in any case I changed the source image and removed the video, although the girl appeared 20years old to me

  ### u/berlinbaer · p8t4sew · score 7 · 2026-09-09 14:38 CT
  - parent: t1_p8ryxqx · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8t4sew/
  stop saying "spicy" you sound like those booktok women who read werewolf billionaire porn and and are afraid to use the words sex or porn.

    ### u/_Iggy_Lux · p8t6f7g · score 5 · 2026-09-09 14:45 CT
    - parent: t1_p8t4sew · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8t6f7g/
    lmao based - thanks for the laugh.

    ### u/North_Enthusiasm_331 · p8thij0 · score 19 · 2026-09-09 15:32 CT
    - parent: t1_p8t4sew · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8thij0/
    That is literally what I’m trying to create 

      ### u/[deleted] · p8trsoa · score 1 · 2026-09-09 16:17 CT
      - parent: t1_p8thij0 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8trsoa/
      [removed]

    ### u/Mammoth-Classroom982 · p8u53ae · score 4 · 2026-09-09 17:20 CT
    - parent: t1_p8t4sew · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8u53ae/
    reverse suspended congress anal with asuna from blue archive

  ### u/Odd3572 · p8tfn6t · score 1 · 2026-09-09 15:24 CT
  - parent: t1_p8ryxqx · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tfn6t/
  Hooray! My, erm, spicy collection can finally be used directly 

  ### u/jankies11 · p8tgkx5 · score 1 · 2026-09-09 15:28 CT
  - parent: t1_p8ryxqx · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tgkx5/
  When you say image references you mean fl2va guide image insertion or ref2va? Certain things seem to really need some lora help but very low lora strength really.

    ### u/DjMesiah · p8th7l5 · score 1 · 2026-09-09 15:30 CT
    - parent: t1_p8tgkx5 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8th7l5/
    Use fl2va or hybrid model with reference sampler.  H3 can do anything.  The lines between fl2va and ref2va can be blurred.  You can do a first frame standard i2v style and use references for subjects that enter.  Or just anatomy references for whatever happens.  Or you can start from a unique frame using components from reference images. It can do whatever you ask

      ### u/Yasstronaut · p8v5y2d · score 1 · 2026-09-09 20:31 CT
      - parent: t1_p8th7l5 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8v5y2d/
      I find i2v is 3x faster than ref for some reason, and depending on the use case it’s better

  ### u/usually_fuente · p8tquym · score 3 · 2026-09-09 16:13 CT
  - parent: t1_p8ryxqx · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tquym/
  People keep saying that, but I have not actually seen any examples.

    ### u/DjMesiah · p8twq95 · score 1 · 2026-09-09 16:39 CT
    - parent: t1_p8tquym · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8twq95/
    I posted the workflow so give it a try.  It truly does work shockingly well

  ### u/WholeBrain9977 · p8ub8tf · score 1 · 2026-09-09 17:51 CT
  - parent: t1_p8ryxqx · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ub8tf/
  Sorry, but are you referring to the FL2VA mode or Ref2VA? I tried hard to use just pose images and intimate parts, but the standard ComfyUI model simply distorted the anatomy or the movement was wrong—for instance, the p3nis wouldn't actually enter the female; it looked like it was just stuck to her, and the male was the one being penetrated, no matter how many references images or videos I added or how I tweaked the prompt in Grok, I couldn't get the movement and anatomy perfect. So, (almost) all the issues were resolved by using the Eros model.

### u/icchansan · p8rzn99 · score 3 · 2026-09-09 11:44 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8rzn99/
References are ur friends and motion lora ;)

### u/No-Dark-7873 · p8s3bxw · score 2 · 2026-09-09 12:00 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s3bxw/
yeah it's become a scam.  Loras aren't needed for H3.  Just use porn character swapping.

  ### u/InsaneBrew · p8sffzt · score 3 · 2026-09-09 12:51 CT
  - parent: t1_p8s3bxw · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sffzt/
  I have never been able to make people replacement work for H3. I see mention of it but all comments always express everyone’s complete inability to make it work. Maybe lightning loras messing it up. 

    ### u/No-Dark-7873 · p8tuazi · score 1 · 2026-09-09 16:28 CT
    - parent: t1_p8sffzt · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tuazi/
    it works.  People who got it to work just ran off never to be heard from again.

### u/uniquelyavailable · p8s5g1d · score 2 · 2026-09-09 12:09 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s5g1d/
I have not been able to make anything remotely resembling human anatomy with any of the base checkpoints or finetunes. I think people are using video references maybe?

### u/PeterTheMeterMan · p8s8tly · score 7 · 2026-09-09 12:23 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s8tly/
What about these new "refmod"quick to train .safetensors - anyone test if a curated set of these would work to produce the illusive normal johnson?   
  
https://huggingface.co/datasets/malcolmrey/various/blob/main/h3-center/docs/MINIMAX_H3_REFMODS_INSTALLATION_AND_USAGE_GUIDE.md

  ### u/ImpressiveStorm8914 · p8ue0r4 · score 1 · 2026-09-09 18:05 CT
  - parent: t1_p8s8tly · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ue0r4/
  If the character you train has visible gentleman vegetables in the dataset used, then you will get a carrot and two onions in the final result after clothing is removed.

### u/Dwanvea · p8s8tqy · score 3 · 2026-09-09 12:23 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8s8tqy/
The cake is a lie

### u/WaitAcademic1669 · p8sfocd · score 1 · 2026-09-09 12:52 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sfocd/
 As you mention, h3 loras are still in development, but i've noticed you can often achieve the desired result without loras: you give a reference image of what you aim to and prompt the model to follow it as reference for the exact scene. Works brilliant for example, to fetch the appearance of breasts in a nude woman, maybe not the same for specific motion and more complex scenes.

### u/Simonindelicate · p8sg7ox · score 1 · 2026-09-09 12:55 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sg7ox/
Is the prompt going to a censored LLM for optimisation before it hits the model?

### u/Vladmerius · p8somrj · score 1 · 2026-09-09 13:30 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8somrj/
I've tried a couple and copied the example prompts without the loras and it is almost the same result. This model is so good it just needs a little push in the right direction prompt wise for 99% of stuff.

It's kind of funny this is the most capable model yet out of the box but I don't really use it for NSFW stuff much simply because it's actually good for productivity it feels almost wasteful to just use it for gooning. 

### u/diogodiogogod · p8sphl5 · score 1 · 2026-09-09 13:34 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sphl5/
I made sure my male anatomy Lora has only t2v examples exactly to show it does work (and comparison plots as well). And all of them have comfyui workflows, you can just load them with the exact nodes and models and you should be able to replicate. IMO h3 is quite a good learner, but you need to train it well and long...

### u/Revolutionary-Bar766 · p8sy8aw · score 5 · 2026-09-09 14:10 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sy8aw/
MysticXXX V4 (must be v4, the other 3 versions weren't great) is incredibly solid. All of my recent gens use this LoRA and rarely any others.

### u/manstory4 · p8sy8kj · score 1 · 2026-09-09 14:10 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8sy8kj/
Get 10ero turbo v5..pair it with mysticxxx4 at .05...done

  ### u/akustyx · p8tbi1q · score 2 · 2026-09-09 15:06 CT
  - parent: t1_p8sy8kj · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tbi1q/
  .5 or .05?

    ### u/manstory4 · p8tkzih · score 2 · 2026-09-09 15:47 CT
    - parent: t1_p8tbi1q · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tkzih/
    0.5

### u/Important-Radish-722 · p8t0ys6 · score 2 · 2026-09-09 14:22 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8t0ys6/
Getting the lora weights and prompt format right is essential.

### u/EternalDivineSpark · p8tb1r4 · score -2 · 2026-09-09 15:04 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tb1r4/
Just look my profile find GitHub link and try

  ### u/hurrdurrimanaccount · p8x5qn9 · score 1 · 2026-09-10 04:52 CT
  - parent: t1_p8tb1r4 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8x5qn9/
  nah.

### u/[deleted] · p8tci23 · score 1 · 2026-09-09 15:10 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tci23/
[removed]

### u/Fickle_Koala7964 · p8tfdmj · score 1 · 2026-09-09 15:23 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tfdmj/
I also spent quite a lot of time putting the workflow together and finding the right combination. Getting the LoRA weights and prompt format right to achieve the results I wanted was pretty tricky, especially when combining multiple Loras

I’ve been testing the video generation on [ratemyd.app](http://ratemyd.app)  over the past few days, and it’s actually pretty good. So far, it has managed to generate pretty much every pose and situation I wanted.

(Don’t be surprised by the site’s main concept,  it’s focused on a particular fetish, but their video generator is genuinely really good)

### u/-Ellary- · p8to8n9 · score 0 · 2026-09-09 16:01 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8to8n9/
https://preview.redd.it/buolxc3s6koh1.png?width=600&format=png&auto=webp&s=23977c84f9f751c25c3ec0aa133a7fbfcb0eb4cb


### u/Spiritual_Whole_5916 · p8tqpm2 · score 1 · 2026-09-09 16:12 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8tqpm2/
Most workflows are hobbled/crippled so no one is using them as a crib sheet i've noticed. Also don't forget that many just do tons of seed rolling until they get a decent result, and/or there is post production trickery going on they don't disclose

### u/AI-Make-NSFW-Stuff · p8u7zlj · score 1 · 2026-09-09 17:34 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8u7zlj/
Some of them don't play well with others, MysticXXX seems to work well, use it at lower weights if you'll combine it with other loras.

Also once you find a combination that works, rerun the generation with higher steps and remove turbo acceleration, or use some upscaling workflows to get better quality.

### u/Sad_Coach_1433 · p8u9n6k · score 2 · 2026-09-09 17:43 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8u9n6k/
Look up refmod  won't need just basic image ref can in a  sense low key train a character Lora in indeed 60 secs just using 10-32 images1  video sample and voice sample and a  description. Ya it's not a true lora but it's better then the normal r2v create a character file when we use it over and over again without having to keep using single images in load image nodes. 

  ### u/taurine_bitch · p8vfwmu · score 1 · 2026-09-09 21:23 CT
  - parent: t1_p8u9n6k · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vfwmu/
  What size was your video that you added to the refmod?

    ### u/Sad_Coach_1433 · p8vg2df · score 1 · 2026-09-09 21:24 CT
    - parent: t1_p8vfwmu · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vg2df/
    67ish mb 720p

      ### u/taurine_bitch · p8vhb5h · score 1 · 2026-09-09 21:30 CT
      - parent: t1_p8vg2df · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vhb5h/
      And did it help with your reference identity? I tried for _several_ hours last night to make refmods that more closely matched the likeness/identity of using individual reference images. I tried 8-12 images, 12-18 images, 20-30 images, using `--mode training`, `--mode encode`, tried cropping close-up face photos, and even tried using full resolution dataset images. And there was always something _not quite right_ with the identity of the refmod. Every time, my refmod was only like 150 to 180KB in size. I didn't think to add a video, though. How close were your refmod's identity to your target reference?

        ### u/Sad_Coach_1433 · p8vhvsx · score 1 · 2026-09-09 21:34 CT
        - parent: t1_p8vhb5h · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vhvsx/
        I haven't tried anything with like a lot of motion yet  just been trying  portrait shots training mode is apparently for motions and styles not identity that's encode 

          ### u/taurine_bitch · p8vixht · score 1 · 2026-09-09 21:39 CT
          - parent: t1_p8vhvsx · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vixht/
          Yeah, I tried the `encode` option and it was about the same quality/likeness as `training`. I'll try again with adding a video and with `encode` and see if it helps. With your portrait shots, how is your likeness/identity to your source reference? Close? Pretty close? Dead on? Others are saying how great the refmods are, so I feel like I'm missing something.
          
          Last question, for your datasets, how varied were your images? Were there any with the subject having slightly different hair color or maybe a few years age difference?

            ### u/Sad_Coach_1433 · p8vjp9s · score 1 · 2026-09-09 21:43 CT
            - parent: t1_p8vixht · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vjp9s/
            i just took about 14 pics off google images made this 
            
            https://reddit.com/link/p8vjp9s/video/ypp71b9yvloh1/player
            

              ### u/Sad_Coach_1433 · p8vjtsh · score 1 · 2026-09-09 21:44 CT
              - parent: t1_p8vjp9s · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vjtsh/
              https://reddit.com/link/p8vjtsh/video/rz68eha2wloh1/player
              

                ### u/Sad_Coach_1433 · p8vjw6r · score 1 · 2026-09-09 21:44 CT
                - parent: t1_p8vjtsh · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vjw6r/
                https://reddit.com/link/p8vjw6r/video/efzb42c4wloh1/player
                

                  ### u/Sad_Coach_1433 · p8vkhx4 · score 1 · 2026-09-09 21:47 CT
                  - parent: t1_p8vjw6r · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vkhx4/
                  This was fp8 model 20 steps no turbo lora 

                ### u/taurine_bitch · p8vk2yl · score 2 · 2026-09-09 21:45 CT
                - parent: t1_p8vjtsh · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vk2yl/
                Damn. That's really good.

                ### u/Sad_Coach_1433 · p8vkkik · score 1 · 2026-09-09 21:48 CT
                - parent: t1_p8vjtsh · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vkkik/
                This was 10euros turbo beta 4 6 steps 

              ### u/Sad_Coach_1433 · p8vk39r · score 1 · 2026-09-09 21:45 CT
              - parent: t1_p8vjp9s · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vk39r/
              actress indie neverett u tell me? they close?
              
              https://preview.redd.it/ok4krwmawloh1.jpeg?width=385&format=pjpg&auto=webp&s=d5866e98bb9b9f7100a461cea168fc419666c71c
              

                ### u/taurine_bitch · p8vlm1d · score 1 · 2026-09-09 21:53 CT
                - parent: t1_p8vk39r · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vlm1d/
                Yeah, that's really good. Last question, how did you get the generate_refmod to also use the video? I aded it to the dataset folder along with all of the photos but it skipped over the video and audio file.

                  ### u/Sad_Coach_1433 · p8vls1i · score 1 · 2026-09-09 21:54 CT
                  - parent: t1_p8vlm1d · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vls1i/
                  What are you using to create the file

                    ### u/taurine_bitch · p8vm77y · score 1 · 2026-09-09 21:56 CT
                    - parent: t1_p8vls1i · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vm77y/
                    The `generate_refmod.py` command. The "Option B: Standard ComfyUI" section of the [Creation Guide](https://huggingface.co/datasets/malcolmrey/various/blob/main/h3-center/docs/MINIMAX_H3_REFMOD_CREATION_GUIDE.md).

                      ### u/Sad_Coach_1433 · p8vmq2n · score 1 · 2026-09-09 21:59 CT
                      - parent: t1_p8vm77y · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vmq2n/
                      I use comfy workflow 
                      Try this  comfyui workflow 
                      https://limewire.com/d/FfSRP#bVFYz9OGlJ
                      Will have a node where you direct the folder path for where  your images are, will have a video loader a VHS node  you load the video there then the main node you would put the description of the photos and into the left you load the voice audio there and then just give it a name and then que 

                        ### u/Sad_Coach_1433 · p8vn7wq · score 1 · 2026-09-09 22:02 CT
                        - parent: t1_p8vmq2n · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vn7wq/
                        Will take less than 60 seconds to run and create the files you have two files a visual and an audio restart comfy and then go to the Ref mod loader in work flow u use to gen videos load the visual in mod 1 and in Mod 2 would be the audio one

                        ### u/Sad_Coach_1433 · p8vpg1c · score 1 · 2026-09-09 22:15 CT
                        - parent: t1_p8vmq2n · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vpg1c/
                        this is the work flow  i use after making the character files.i added auto scene prompt nope in main promp you just type your basic idea and hit gen the auto scene prompt will auto add everything else like the direction of the character and the <subject 1> tags  so you dont have to every time. also added show text it will show the final full prompt with  the direction and full prompt [https://limewire.com/d/MUUYm#eBtB3R5KV0](https://limewire.com/d/MUUYm#eBtB3R5KV0) has the newest refmod 2.0  loader where you load the character files 

                        ### u/taurine_bitch · p8vpqwk · score 1 · 2026-09-09 22:16 CT
                        - parent: t1_p8vmq2n · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vpqwk/
                        Oh, interesting. Where is workflow from? The nodes from github only have the extract refmod node. The default nodes don't have this "Master" node.

                        ### u/Sad_Coach_1433 · p8vq1mj · score 1 · 2026-09-09 22:18 CT
                        - parent: t1_p8vmq2n · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vq1mj/
                        The nodes showed up after the 2.0 update when go to add a new node 

                          ### u/Sad_Coach_1433 · p8vqcgl · score 1 · 2026-09-09 22:20 CT
                          - parent: t1_p8vq1mj · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vqcgl/
                          I had chatgpt wire it all together for me as you see it works per my sample videos

                          ### u/taurine_bitch · p8w49ca · score 1 · 2026-09-09 23:47 CT
                          - parent: t1_p8vq1mj · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8w49ca/
                          Yeah, I got the nodes updated (I didn't know there was an update). I got the refmod created. It now seems to create 2 (X_audio.safetensor and X_visual.safetensor) instead of the single file refmod. My visual.safetensor file is like 24MB in size and I instantly go OOM on my 4090, hah. And that's with 22 reference photos in the dataset, 1 video that's 11 seconds and 8MB, and 1 audio file that's 2 seconds long.

                            ### u/Sad_Coach_1433 · p8w4ww7 · score 1 · 2026-09-09 23:52 CT
                            - parent: t1_p8w49ca · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8w4ww7/
                            Hmm 🧐  ya the character files r small in size that's normal and yea it makes two one for appearance and one for audio.strange you oom I made indie with 32 images 1 video and voice ref audio and I'm on 5060 ti 🫪👀

                              ### u/Sad_Coach_1433 · p8w55z0 · score 1 · 2026-09-09 23:54 CT
                              - parent: t1_p8w4ww7 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8w55z0/
                              Should get a error on what's causing the oom

                              ### u/taurine_bitch · p8w5kty · score 1 · 2026-09-09 23:56 CT
                              - parent: t1_p8w4ww7 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8w5kty/
                              Hmmm...I know you've already helped me a ton but would you mind doing me one more favor? Could you screenshot your Master Create Character node, as if you were making another ref mod? Since yours works, I'd like to compare our settings to make sure I'm not missing something or setting something too high.
                              
                              Did you resize your photos beforehand? I only have 22 photos, 1 video that's 8MB in size and 11 seconds long, and 1 audio file that's only 2 seconds long. Your dataset is bigger than mine and works. I'm not doing something right, haha.

                                ### u/Sad_Coach_1433 · p8w6hfe · score 1 · 2026-09-10 00:03 CT
                                - parent: t1_p8w5kty · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8w6hfe/
                                Naw I just put em in a folder then put the parts in the node just googled bunch different angles for her and shared em on chatgpt and it let me know which ones to keep that work best for refmod I take a screenshot in second hold up 

                                ### u/Sad_Coach_1433 · p8w7b7i · score 1 · 2026-09-10 00:09 CT
                                - parent: t1_p8w5kty · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8w7b7i/
                                i dmed u figure be quicker and not fill up this thread 

### u/[deleted] · p8ue0wn · score 1 · 2026-09-09 18:05 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8ue0wn/
[removed]

### u/KimSwallowsMD · p8upag0 · score -4 · 2026-09-09 19:05 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8upag0/
You don’t really need this trust me 

### u/conkikhon · p8vj1ne · score 1 · 2026-09-09 21:40 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8vj1ne/
A lora can mess with the base understanding or motion of the model, you don't need much strength if you only want improved details

### u/Tiforma · p8wg18q · score 1 · 2026-09-10 01:17 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8wg18q/
10eros and pinkcherry models work well

### u/SeaworthinessFresh16 · p8yzdci · score 1 · 2026-09-10 10:40 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p8yzdci/
U need to prompt it. Cant just write a sentence. You really need to describe everything then you will see magic happen.

### u/kualikuri · p95xpqp · score 5 · 2026-09-11 09:38 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p95xpqp/
Ref2VA works very well for me. I use 2 reference images for each subject and they come out perfect. You can also add a reference audio for any subject that you want to speak with a specific voice. Reference videos work as well fly both visual and audio references, but because they’re broken down into one image per frame it significantly increases both the conditioning time and the generation time.

You’ll want to reference to official Ref2VA prompting guide as the format needs to be very specific, but it gives you very good control over the scene. Summary is used to establish overall macro architecture so it knows where points A, B, and C are, and the detailed description is a step-by-step instruction for each action describing how to get from point A to B to C. You need to be very detailed, and when it comes to NSFW stuff it helps to anchor the spatial relationship of the NSFW parts by describing their position relative to their nearest non-NSFW parts. Also, when it comes to terminology for NSFW stuff, try not to be too clinical. H3 seems to understand common vernacular terms better than clinical terms in many cases.

Lastly, when it comes to checkpoints and LoRAs, I have a few recommendations. First, when it comes to NSFW checkpoints, many people will recommend Eros, but IMO it’s just not there right now and probably won’t be until Sulphur is released so they can finetune it. I highly recommend Dasiwa. It is great for both NSFW and Non-NSFW, for realistic, semi-realistic, and anime/cartoon styles, plus it’s a hybrid model that can be used for REF2VA, FL2VA, and T2VA (though I still use the REF2VA prompting style for pure T2VA because it lets me micromanage subject identities and other details). As for LoRAs, your observation is unfortunately the same as mine. I’d hard for people to train LoRAs for H3 right now, so the quality is not there. What I have found helps a lot is using multiple different (2-3) LoRAs for the same thing, all with lower weights. The best one I’ll usually give a weight of 0.6\~0.7, while the others get 0.4\~0.5. Even a “bad” LoRA can be helpful as a counterpart to a decent LoRA if they have different things they’re good at.

Last thing I’ll say is, I definitely don’t recommend using Sage or Spectrum. They’ll speed up your generation, but they’ll also destroy your quality and prompt adherence. Doing 8 steps with the right 8 step boost LoRA will work exceptionally better for both time saving and quality. I actually find that I get better quality using the 8 step boost LoRA than doing full 20 steps without it. I just drop my MP in the resolution selector to 0.3 for prompt testing and seed hunting, then when I’m ready for final generation I up it to 0.6MP and pass it through a VAE upscale to 0.9 MP.

  ### u/cal_01 · pa66d65 · score 1 · 2026-09-16 09:37 CT
  - parent: t1_p95xpqp · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/pa66d65/
  A bit late here, but Spectrum also completely destroys audio too.

### u/SnooMachines1543 · p9embs7 · score 2 · 2026-09-12 14:11 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p9embs7/
I know I’m late. But to answer your question. Yes…. I use the dick and pussy loras in all kinds of configurations at all strengths. The dicks still come out looking like dead rhinoceros horns, the end of baseball bats, or dicks that have narcotic forskins. And the pussys look like deflated basketballs or just mangled flesh. I’ve done what others seem to be doing. Generate on wan2.2 and use that reference image as the starting point. But when you’re doing a longer scene where the man meets the woman and they get naked together, nothing seems to work. 

  ### u/North_Enthusiasm_331 · p9eogjb · score 1 · 2026-09-12 14:20 CT
  - parent: t1_p9embs7 · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p9eogjb/
  Yeah there's such an obvious difference between scenes generated with mmax vs ltx vs wan -- frustrating to be so close to being able to make want you want, yet not quite there. It also seems to be that if I use wan video as reference, the mmax video ends up looking like the wan one, in terms of both speed and quality ... have you been able to address this? maybe my settings/prompt make the reference video too strong? are you using wan video but different starting image, or just references?

    ### u/SnooMachines1543 · p9et5fo · score 1 · 2026-09-12 14:41 CT
    - parent: t1_p9eogjb · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p9et5fo/
    I just generate a 1 or 2 second clip on wan and take a screenshot of the pose or image I like and drop that in as a reference. Or I’ll do a longer video use the opening pic and the end pick. Prompt what I want and watch it go. But still end up with 1/2 chewed sausages for dicks and a botanical experiment for ass and vag. They also don’t actually”suck” dicks. They just kind of sit there. I think we’re just spoiled lol. Imagine having this 20 years ago. We’d never leave the house haha

### u/cashcowman · p9hdeyh · score 1 · 2026-09-12 22:47 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/p9hdeyh/
Downloading these modules is a real pain.  Keep faulting and restarting.

### u/IRLMainCharacter · pa20538 · score 1 · 2026-09-15 17:57 CT
- parent: t3_1wbpwcq · permalink: https://www.reddit.com/r/StableDiffusion/comments/1wbpwcq/are_minimax_spicy_loras_a_lie/pa20538/
i think the examples are mostly done by i2v, or maybe t2v with a lucky seed. therefore, expecting similiar results with r2v is doomed, which sucks because r2v is where h3 has the greatest potential. you have to experiement alot with different prompts to get close. rule of thumb: be as specific as possible. H3 expects 350-500 words for the detailed description, that is free prompt real estate waiting to be built upon.
