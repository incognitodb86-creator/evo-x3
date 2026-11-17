# Saved web evidence - fetched 2026-10-29 ~21:05 CT by Forge (pi, mcp fetch), for plans/2026-10-29-terrace-retest-plan.md item S8

URL: https://huggingface.co/TenStrip/10Eros-Max/discussions/74
Title: "Best approach for maintaining likeness in I2V?" (#74, opened by wittywolk, closed by wittywolk)
Why: Max brief 2 (`briefs/2026-10-29-2100-forge-brief2.md`) item 1 says the "<Picture 1> is the correct scene
identity" text IS in #74 and tells Forge to use LokkenJP's exact wording from it. Forge fetched #74 to read the
exact text. Fetched as readable text (the tool's markdown conversion), not raw HTML; nothing edited below except
the wrapping of the page into the reply posts.

---

TenStrip/10Eros-Max · Best approach for maintaining likeness in I2V?  (#74)

## wittywolk (opener, edited)

Previously it was straightforward - just feed the image and run it. Now, with the two-pass workflow, it's not that
simple. Using a reference model helps bring it back, but in my case, it causes noticeable face boiling that wasn't
an issue with older methods.

To anyone who knows their way around this: what should I try? Bump up the initial pass resolution? Tweak the refmod
parameters?

I prefer I2V over T2V 99% of the time because Krea 2 can give me a much better initial image with higher likeness
and all the exact elements I want already dialed in.

The time/quality I use most frequently lands me at ~0.8 MP final output.

btw: In my opinion the BF16 upscaler results are way better than the FP16, without much time difference.

## LokkenJP (the S8 source, verbatim in full)

I'm not having issues doing pure i2v with a starting reference image and holding it.

Try something like this in the prompt: "<Picture 1> is the correct scene identity. All lighting, lighting hue, color
palette, visual output style, camera angle, camera focal length, camera orbit, camera framing, background,
background objects, and characters fully preserved from <Picture 1>. <Picture 1> is the initial frame for the video
and the scene continues from there. Then the rest of the prompt"

This usually holds quite well as the conditioning is passed to both sampling phases, so the second refine pass
should also hold the reference.

You can try bumping up the initial pass resolution and step count to 10 or 12 and see if that helps.

## wittywolk (the #74 graph fix, verbatim in full)

I did some testing and tweaking, and here is what I landed on:

* Changed Reference to Video from Match to Max (the impact scales with the megapixel setting used, ranging from
  minor to significant).
* Set Add Guide For MiniMax H3: 1x before the first Basic Guider, and 1x before the second Basic Guider (the one
  after the upscale pass), using the initial first-frame image.

This setup currently relies on just a single image. Next, I plan to tweak it by using a refmod instead of the
reference image, keeping the raw image strictly for the two Add Guide passes.

I also benchmarked it with and without your prompt, both with and without Add Guide, and honestly... I won't be
using the steering prompt. Add Guide locks down the first frame almost identically to how a native I2V node behaves
(giving a true 1:1 match in framing, alignment, etc.), whereas the prompt only nudged the composition closer
without fully nailing it. Layering the prompt on top of Add Guide introduced weird artifacts - like the character
not blinking for several seconds. With two Add Guide passes already in place, the prompt just isn't worth the
trouble.

## LokkenJP (closing)

Problem I see with this approach of "add guide" is that, if the image selected is used as a reference but not as a
starting frame, this might inject the wrong conditioning in the sampler. And the node needs careful managing bc you
cannot bypass the initial image like this to do pure t2v. But I might figure out something.

PS. Adapted the same basic approach slightly modified on my current workflows, if you want to take a look at them
in my repo. Thanks!

---

## What Forge takes from this (read-only conclusions, all attributable to the quoted posts)

1. The prompt line S8 must use is **LokkenJP's text in #74** - two sentences, then his own instruction "Then the
   rest of the prompt" = append the existing prompt. Max's brief 2 is right: the line is in #74. (My F5 in
   `notes/2026-10-29-terrace-retest-plan-findings.md` cited the generic `<Image N>` form from #63/#50 - the
   `<Picture 1>` form with the added "initial frame" sentence is in #74. F5 corrected there.)
2. The #74 graph fix (Match→Max + one Add Guide before each guider) is what B2 already implements.
3. The thread's own verdict on S8: wittywolk benchmarked prompt vs Add Guide, both ways, and stopped using the
   prompt: "Layering the prompt on top of Add Guide introduced weird artifacts - like the character not blinking
   for several seconds." So S8's expected direction is negative on this cell, and the artifact to watch is named.
4. Extra facts, not used tonight, worth recording for later arms: "the default 0.3 MP starting resolution
   completely loses the likeness"; "bumping up the initial pass resolution and step count to 10 or 12";
   "BF16 upscaler results are way better than the FP16, without much time difference" (relevant to arm S3, which
   moves B2's conv_v1_bf16 to fp16 - i.e. S3 tests the direction the community dislikes); typical user output
   ~0.8 MP.
