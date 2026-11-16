# U21 B4 Writer Quality — Blinded A/B Evaluation Packet

- **Prompt file:** `/home/derekboone/AI/community/benchmarks/u21-writer-prompts-20261115.json`
- **Prompt file git commit:** `d1505a59cab3b34c7ec78c978b31bbaad5ec4dfd`
- **Prompt file SHA-256:** `b66b3156aaa4dc651b29f2f0fbbc79bee9759cd0e4b72be48a902c423e65bdac`
- **Pinned samplers:** `temperature=0.7`, `top_p=0.95`, `top_k=64`, `min_p=0.05`, `max_tokens=500`, `enable_thinking=False`
- **Fixed seeds (3 rounds):** `[101, 202, 303]`
- **Order randomization:** Round 1 alternates A/B by prompt parity; Round 2 strictly inverts Round 1 (`A/B` -> `B/A`); Round 3 uses a seeded random order. Official mapping is stored separately in `b4_writer_key.json`.
- **Status:** Official Prompt maker scores **PENDING**.

## Round 1 (seed=101) — W01_noir_dock (noir)
**Prompt:** Write a 220-word third-person noir opening set on a rain-slicked riverfront loading dock at 2:00 AM. A private investigator discovers a soaked leather ledger wedged beneath a rusted bollard. Focus on concrete physical details, light on wet concrete, and terse rhythm. End on a quiet threat.

### Sample A
The clock on the pier tower struck two, a hollow toll swallowed by the fog. Rain fell in heavy, rhythmic sheets, turning the riverfront loading dock into a graveyard of slicked concrete and oil-stained shadows. The moonlight didn't shine here; it only bruised the surface of the puddles, casting fractured, sickly light across the wet asphalt.

Elias moved through the dark, his trench coat heavy with moisture. His boots crunched on grit and broken glass. He stopped near a rusted bollard, a jagged tooth of iron rising from the pier. Something caught the dim glow of a distant streetlamp.

He knelt. The cold seeped through his trousers instantly. Wedged deep in the iron's shadow was a book. It was a leather ledger, bloated and black from the soak, looking more like a drowned organ than stationery. He pried it loose. The leather felt like cold, dead skin against his palms. It was heavy with more than just rainwater; it held the weight of secrets that didn't want to be found.

A sudden scrape of metal echoed from the warehouse behind him. The rain continued its steady, indifferent beat. Elias didn't turn around. He just tightened his grip on the book and felt the sudden, sharp chill of being watched.

### Sample B
Rain hammered the loading dock in sheets. The river below moved black and heavy, a slow muscle against the pilings. Two AM. The city slept, but the water didn't. It never did.

Vance crouched by the rusted bollard, knees aching against wet concrete. The leather ledger sat wedged in the gap between iron and stone, swollen and dark as a bruise. He pulled it free. Water ran from its spine in thin threads. The cover had warped, the leather cracking where the sun had once baked it. No name inside. No date. Just columns of numbers, faded to ghosts.

He held it to the light of the single working lamp on the pier. The bulb buzzed, casting a jaundiced pool across the dock. Rain pooled in the concrete cracks, each one a tiny mirror reflecting nothing. Vance turned the pages. The ink bled at the edges, numbers dissolving like sugar in tea. Someone had written here in a hurry. Someone had hidden this here in a hurry.

He stood. His knees cracked. The river kept moving, indifferent. The ledger sat in his hand, heavier than it should have been.

Somewhere up the pier, a door opened. Light spilled out, then vanished. The sound of footsteps followed, soft on wet concrete.

Vance didn't turn around. Not yet.

---

## Round 2 (seed=202) — W01_noir_dock (noir)
**Prompt:** Write a 220-word third-person noir opening set on a rain-slicked riverfront loading dock at 2:00 AM. A private investigator discovers a soaked leather ledger wedged beneath a rusted bollard. Focus on concrete physical details, light on wet concrete, and terse rhythm. End on a quiet threat.

### Sample A
Rain needled the river. It drummed on the corrugated roof of the loading dock, turned the concrete to black glass, and pooled in the cracks. Two in the morning. The city slept beyond the water, its lights smeared and broken on the surface.

Elian Voss crouched beneath a rusted bollard, its iron skin flaking orange into his palm. His knee pressed wet concrete. His coat clung to his shoulders, cold and heavy. He did not care. His fingers worked beneath the bollard's base, past a tangle of rotted rope and a crushed beer can, until they found leather.

The ledger was soaked. Its cover had warped like a dead leaf, the spine split, the pages swollen and fused. Water darkened it to the color of old blood. Voss turned it over. A name was written on the first page, half-dissolved, barely legible. He recognized it. The color drained from the night.

Somewhere upstream, a horn sounded. Then silence, thicker than the rain.

Voss stood. His knees cracked. He tucked the ledger under his arm and looked out at the black water. It moved without sound, without hurry, carrying everything it swallowed downstream and never giving it back.

### Sample B
The rain didn't fall; it punished. It drummed against the corrugated metal of the warehouses, a relentless, hollow percussion that drowned out the city’s heartbeat. At 2:00 AM, the riverfront was a graveyard of salt and diesel. 

Elias stepped over a coil of rotted hemp, his trench coat heavy with the soak. The streetlamp at the pier’s edge flickered, casting fractured, oily light across the wet concrete. Every puddle was a mirror of broken neon and bruised violets, shimmering like spilled gasoline. 

He stopped near the edge. A rusted iron bollard sat hunched in the shadows, weeping orange streaks of oxidation into the dark water. Something caught the light beneath its base—a sliver of something dark and organic.

Elias knelt. The grit of the dock bit into his knees. He reached into the muck, fingers closing around a mass of sodden hide. He pulled it free: a leather ledger, bloated and heavy with river water. The binding was bruised, the edges swollen like a corpse’s skin. He wiped a smear of silt from the cover, feeling the weight of a thousand secrets pressed into the pulp.

He tucked the book into his coat. The silence of the docks felt different now. It wasn't empty; it was waiting.

---

## Round 3 (seed=303) — W01_noir_dock (noir)
**Prompt:** Write a 220-word third-person noir opening set on a rain-slicked riverfront loading dock at 2:00 AM. A private investigator discovers a soaked leather ledger wedged beneath a rusted bollard. Focus on concrete physical details, light on wet concrete, and terse rhythm. End on a quiet threat.

### Sample A
Rain fell in long silver threads against the black water of the river. The loading dock stretched out, a slab of wet concrete slicked with oil and old rust. Streetlamps threw pale cones across the surface, catching the sheen of standing water in fractured shards of light. The air smelled of diesel, brine, and wet iron.

He stood at the edge of the dock, collar turned up, watching the dark current pull at the pilings. Two a.m. The city had gone quiet except for the rain. He should have left an hour ago. Instead he lingered, because the ledger had called to him from beneath the bollard.

It sat wedged in the gap where rust had eaten through steel. Leather cover, swollen with water, pages fused together. He pried it free with a gloved hand. The cover peeled back like dead skin. Inside, columns of names in a cramped hand. Some names were crossed out. Others were not.

He closed the book. The rain drummed against his shoulders. Somewhere upstream, a horn sounded. He did not look back. He tucked the ledger under his arm and walked into the dark, where the dock ended and the city waited, patient and cold, for him to come home.

### Sample B
The rain didn't fall; it hammered. It turned the riverfront into a graveyard of slick concrete and oily shadows. At 2:00 AM, the docks belonged to the fog and the ghosts. The only light came from a flickering streetlamp half a block up, casting long, shivering ribs of yellow across the wet pavement. Every drip from the rusted crane overhead sounded like a gunshot in the hollow silence.

Elias stepped around a stack of rotting crates, his trench coat heavy with moisture. His flashlight cut a weak, trembling path through the dark. The beam snagged on something dark wedged beneath a corroded iron bollard. 

He knelt, the grit of the dock grinding under his knees. It was a ledger. The leather cover was swollen, soaked through by the relentless deluge, looking less like a book and more like a piece of waterlogged skin. He pried it loose. The pages groaned, weeping black ink into his palm. The numbers inside were blurred, bleeding into illegibility, but the names remained sharp.

He closed the book. The sound was a dull thud against the rhythmic pulse of the river. He wasn't alone. Somewhere in the dark, a heavy boot crunched on gravel. 

The rain wasn't the only thing coming down.

---

## Round 1 (seed=101) — W02_tension_kitchen (dialogue_drama)
**Prompt:** Write a 220-word scene driven mostly by dialogue between two estranged siblings clearing out their late father's cluttered workshop. One finds an unmailed letter tucked inside a plane iron; neither mentions the money directly, yet every line circles it. No exposition dump.

### Sample A
“Hand me that plane.”

“It’s not a plane, it’s a—”

“Give it here.”

She set it on the bench between them. “You know what’s in it?”

“Rust.”

“No.” He turned it over, slid his thumb along the blade’s edge, and pulled out a folded slip of paper. “A letter.”

“From when?”

“Does it matter?”

“It matters if it’s from her.”

He unfolded it. “It’s from him.”

She went still. “Read it.”

“He says—” He paused. “He says he’s sorry about the house.”

“That’s it?”

“That’s it.”

“Then the money’s gone.”

He folded the paper back up. “The money’s gone.”

“You can’t just—”

“I can.”

She picked up a jar of screws, set it down again. “You were going to keep the house.”

“I was going to keep the house.”

“But you won’t.”

“I won’t.”

She looked at the letter in his hand. “So we’re back to the money.”

“We’re always back to the money.”

He tucked the letter back into the plane. “At least we agree on something.”

“Which is?”

“That it’s gone.”

### Sample B
Dust motes danced in the shafts of light piercing the grime-streaked windows. Elias shoved a rusted wrench aside, his breath hitching in the stale air.

"He kept everything," Clara muttered, lifting a heavy plane iron from the workbench. "Even the scrap that should’ve been melted down years ago."

"He liked the weight of things," Elias said, wiping grease onto his jeans. "The permanence of it."

Clara pried the wooden base of the plane open. A folded slip of paper fell out, landing softly on the sawdust. She froze.

"Find something?" Elias asked, not looking up from a box of bent nails.

"Just more clutter," Clara said, her fingers trembling as she smoothed the crease. She didn't read it aloud, but her eyes tracked the jagged handwriting. "He was always writing things down. Notes. Debts. Promises."

Elias paused, his hand hovering over a drawer. "He never could settle a score, could he? Always left things hanging."

"He thought he could fix it all with a signature," Clara whispered, staring at the ink. "As if a single piece of paper could balance the scales."

"Some things don't balance, Clara. No matter how much you stack up."

Clara shoved the letter into her pocket. "Let’s just finish this. Before the dust settles for good."

---

## Round 2 (seed=202) — W02_tension_kitchen (dialogue_drama)
**Prompt:** Write a 220-word scene driven mostly by dialogue between two estranged siblings clearing out their late father's cluttered workshop. One finds an unmailed letter tucked inside a plane iron; neither mentions the money directly, yet every line circles it. No exposition dump.

### Sample A
Dust motes danced in the shafts of light cutting through the grime of the workshop windows. Elias shoved a stack of yellowed blueprints aside, his breath hitching in the stale air.

"He kept everything," Clara said, her voice tight. She lifted a rusted plane iron from the workbench, turning it over in her gloved hands. "Even the scraps of things that didn't work."

"He liked the idea of potential," Elias replied, wiping grease from a heavy vise. "The idea that something could still be worth something if you just polished it enough."

Clara’s thumb brushed a folded slip of paper wedged deep inside the iron’s hollow. She froze. The paper was crisp, untouched by the surrounding decay.

"Found something," she murmured, pulling it free.

Elias didn't look up. "More old receipts? More debts he swore he’d settle?"

"It’s a letter. Unmailed." Clara stared at the handwriting. "He was writing to the bank. About a 'final settlement.'"

Elias stopped scrubbing. The silence grew heavy, thick as the sawdust on the floor. "He always said he’d make it right. That he’d leave us with something more than just this clutter."

"He was close," Clara whispered, her eyes scanning the lines. "He was so close to the end of it."

"But he never sent it," Elias said.

"No," Clara replied. "He just kept it tucked away."

### Sample B
“You’re not taking the plane iron,” she said.

“I’m not leaving it.”

He pried it from a nest of sawdust and rusted nails. The handle was cracked. A folded paper slipped from beneath the blade and fluttered to the bench.

He picked it up.

“Don’t,” she said.

“Don’t what?”

“Don’t get that face.”

He unfolded the letter. The handwriting was their father’s—crooked, urgent.

“It’s from him,” he said.

“To who?”

He read the first line aloud. “‘To whoever finds this after me.’”

She snatched it. Read it twice. Folded it.

“It’s about the money,” she said.

“It’s not about the money.”

“It is.”

He took it back. “It’s not.”

She pointed at the plane. “That’s not even his.”

“Then why’s it in his hand?”

“Because he was sitting here.”

He looked at the chair, the vise, the half-built shelf leaning against the wall.

“You know what,” she said. “Let’s not.”

“Not what?”

“The money thing.”

“Okay.”

“Good.”

He set the letter down. Picked it up again.

She stopped moving.

He folded it. Put it in his pocket.

She nodded.

---

## Round 3 (seed=303) — W02_tension_kitchen (dialogue_drama)
**Prompt:** Write a 220-word scene driven mostly by dialogue between two estranged siblings clearing out their late father's cluttered workshop. One finds an unmailed letter tucked inside a plane iron; neither mentions the money directly, yet every line circles it. No exposition dump.

### Sample A
“You don’t have to box those,” she said.

“I’m just going through them,” he said.

“You’re going through them like you’re not.”

He set down a crate of chisels. “What do you want me to say?”

“That I’m not going to stay.”

He turned the plane iron over in his hands. The blade was still seated in its housing, dark with old oil. “Dad kept his tools in order.”

“Dad kept his tools *anywhere*.”

She pointed at the iron. “There’s something in there.”

He pried the blade free. A folded slip of paper slid out, soft with age, the creases worn white. He unfolded it. Neither of them moved.

“Is that—”

“Mm.”

“You can’t read that now?”

“Not yet.”

She took a step closer. “You should.”

He held the letter at arm’s length, like it might bite. “You said he owed you.”

“Eight years of rent on this shop.”

“From me?”

“From the estate.”

He looked at the letter, then at her. “That’s not what it says.”

“It’s not a letter about money, is it?”

He set the letter on the bench between them. She didn’t touch it. He didn’t either. The chisels sat unboxed in their crate. The workshop smelled of linseed and dust.

### Sample B
Dust motes danced in the shafts of light cutting through the grime of the workshop windows. Elias shoved a rusted vise aside, his breathing heavy.

"He kept everything," Clara said, lifting a stack of yellowed blueprints. "Even the scrap metal he swore he’d sold in '98."

"He liked the weight of things," Elias replied, his voice tight. He reached for a heavy, blackened plane iron resting on the workbench. As he lifted it, a cream-colored envelope slid from the hollowed underside.

Clara paused, a jar of nails poised in her hand. "What’s that?"

Elias smoothed the paper. The ink was faded, the handwriting unmistakably their father’s. "Just a note. Unfinished."

"He always had a way of leaving things halfway done," she said, her eyes narrowing. "Especially when they involved... finality."

Elias traced the seal. "He wrote about the debts. And the way things were partitioned."

Clara stepped closer, the scent of sawdust and old grease thick between them. "Did he mention the distribution? The way he promised it would be handled?"

"He mentioned the cost of keeping it all," Elias murmured, staring at the unmailed words. "The cost of staying."

"He never was good at settling accounts," Clara whispered.

Elias tucked the letter into his pocket. "Let's just finish this."

---

## Round 1 (seed=101) — W03_storm_brig (historical_maritime)
**Prompt:** Write a 220-word historical scene aboard an 1840s merchant brig rounding Cape Horn in freezing sleet. A young second mate must climb the slick ratlines to free a fouled topsail gasket before the spar snaps. Emphasize wind weight, wet hemp, numb fingers, and salt sting.

### Sample A
The world was nothing but a screaming, grey void. Aboard the brig *Isabella*, the wind didn't just blow; it had mass, a physical weight that hammered against the hull like a battering ram. Freezing sleet lashed the deck, turning every inch of timber into a treacherous sheet of glass.

Elias, the second mate, gripped the wet hemp of the ratlines. The rope was a frozen serpent, slick with brine and ice, biting into his palms. His fingers were no longer part of his body; they were merely numb, wooden appendages that fumbled blindly against the rigging. Every gust threatened to peel him from the shroud and cast him into the churning, black maw of the Southern Ocean.

Above him, the topsail shrieked. A fouled gasket had snagged the yard, and the wind was twisting the spar with a sickening, rhythmic groan. If the wood snapped, the falling timber would gut the mainmast. 

He hauled himself upward, his lungs burning from the salt sting that cut his throat. The wind roared in his ears, a predatory howl. He reached the footrope, his vision blurred by stinging spray. With a desperate, trembling heave, he lunged for the knot, praying his frozen grip would hold long enough to cheat the storm.

### Sample B
The wind came off the Horn like a physical weight, a solid black mass that pinned the *Mary Celestine* against a sea of black glass. Sleet lashed the rigging in horizontal sheets, and the young second mate, barely sixteen, clawed his way up the ratlines with fingers that had long since stopped feeling the cold. The hemp was slick with brine and frozen spray, each rung a treacherous, ice-glazed thing that threatened to slip from his grip and send him tumbling into the churning dark below.

His task was madness: to free a topsail gasket fouled around the yardarm before the spar, groaning under a strain that seemed to vibrate through the ship’s very bones, snapped like a dry twig. The salt sting bit into every raw knuckle and split nail, a vicious reminder of the ocean’s contempt for small men. He could not look down. To look down was to acknowledge the void. He could not look up. To look up was to see the yardarm thrashing like a living thing. He could only climb, one hand over the other, the wind screaming in his ears, the sea roaring in his blood, until his numb fingers finally closed around the frozen knot and the ship, for one terrible moment, held its breath.

---

## Round 2 (seed=202) — W03_storm_brig (historical_maritime)
**Prompt:** Write a 220-word historical scene aboard an 1840s merchant brig rounding Cape Horn in freezing sleet. A young second mate must climb the slick ratlines to free a fouled topsail gasket before the spar snaps. Emphasize wind weight, wet hemp, numb fingers, and salt sting.

### Sample A
The wind struck the *Meridian* like a hammer blow, driving sleet sideways across her blackened decks. Young Thomas Hale gripped the shrouds, his knuckles white beneath frozen skin, and began his climb. Each rung of the ratlines bit cold into his palms, the wet hemp swollen and slick beneath his calloused hands. Salt stung the raw cuts along his fingers where the rope fibers had torn through his gloves.

The topsail yard groaned overhead, the gasket tangled and fouled around the spar’s iron band. Thomas hauled himself higher, wind pressing his chest flat against the shrouds, threatening to peel him from the rigging entirely. His legs trembled. The ship pitched, and he swung like a pendulum, boots scraping salt-stained wood.

He reached the gasket at last, fingers clumsy and numb as blocks of ice. He worked the knot free with bleeding thumbnails, the rope stiff and frozen in his grip. The wind shrieked through the rigging, a living thing, tearing at his coat, his hair, his breath.

Below, the captain shouted something lost to the gale. Thomas ignored it. His world had narrowed to the knot, the spar, the wind. He freed the gasket. The yard swung free. The spar held. He descended, legs shaking, and the sea roared beneath the hull like something ancient and hungry.

### Sample B
The sky was a bruised, churning slate, and the Southern Ocean roared with a fury that felt personal. Elias gripped the wet hemp of the ratlines, his knuckles white and uselessly numb. Every gust of wind carried a crushing weight, a physical blow that threatened to peel him from the rigging like a scrap of bark.

Freezing sleet lashed his face, each drop a needle of ice that mixed with the stinging salt spray to blind him. He climbed, his boots slipping on the slick, frozen shrouds. Below, the merchant brig groaned, her timbers shrieking against the mountainous swells of Cape Horn. 

He reached the topsail yard, where the fouled gasket hung like a strangled limb. The wind howled through the canvas, a violent, rhythmic snapping that signaled the spar’s imminent doom. Elias lunged, his fingers fumbling against the ice-crusted rope. The cold had stolen his dexterity; his hands felt like heavy, wooden blocks. He clawed at the knot, the salt stinging the raw cracks in his skin. 

With a desperate, bone-deep heave, he sliced the line. The canvas unfurled with a thunderous crack, momentarily relieving the tension. As the spar groaned back into alignment, Elias hung suspended in the void, shivering as the gale screamed through the dark.

---

## Round 3 (seed=303) — W03_storm_brig (historical_maritime)
**Prompt:** Write a 220-word historical scene aboard an 1840s merchant brig rounding Cape Horn in freezing sleet. A young second mate must climb the slick ratlines to free a fouled topsail gasket before the spar snaps. Emphasize wind weight, wet hemp, numb fingers, and salt sting.

### Sample A
The wind hit him like a wall of frozen iron, a solid, roaring weight that pressed him against the rigging. Elias gripped the ratlines, his fingers no longer his own—two swollen, useless things encased in soaked wool that had long since surrendered to the cold. Below, the *Perseverance* plunged through a black trough, the sea exploding against her hull in sheets of sleet that stung his face like scattered needles.

He had to go higher. The topsail gasket had fouled around the yardarm, and the spar groaned beneath the strain, a deep, wooden complaint that vibrated through the hemp beneath his boots. The wet ropes bit into his palms, slick and heavy, each strand swollen with brine that burned where his skin had cracked. He could taste the salt on his lips, sharp and metallic, mixing with the icy spray that found its way into his collar.

Every inch upward was a negotiation with the gale. His boots slipped on the frozen lines. He reached the gasket, fingers fumbling with knots that had stiffened into something harder than wood. The spar cracked again, louder this time, a sound like a bone breaking. He pulled. The knot gave. The wind roared its approval, and the ship surged forward into the white dark, the spar freed, the sea still hungry.

### Sample B
The sky was a bruised, churning slate, and the wind didn't just blow; it possessed a physical weight, a crushing pressure that threatened to drive the brig *Audacious* straight into the white teeth of the Southern Ocean. Freezing sleet lashed the deck, stinging like handfuls of thrown gravel.

“The topsail!” the Captain bellowed, his voice swallowed by the roar. “The gasket’s fouled! If that spar snaps, we’re a coffin ship!”

Elias, the second mate, gripped the rail. His fingers were wooden, numb beyond sensation, yet the salt sting in his raw knuckles burned like fire. He lunged for the ratlines. The wet hemp was treacherous, slick with ice and brine, sliding beneath his touch like dying eels. Each upward heave felt like pulling against the gravity of the world itself.

The gale shrieked through the rigging, a banshee’s wail that vibrated in his very bones. He climbed, lungs heaving frozen air, as the ship pitched violently. Below, the frothing, black abyss of Cape Horn churned hungrily. He reached the yard, his breath coming in ragged gasps. The topsail fluttered frantically, a trapped beast. With trembling, frost-bitten hands, he fumbled for the knife, praying the steel wouldn't slip before the wood gave way.

---

## Round 1 (seed=101) — W04_derelict_airlock (hard_scifi)
**Prompt:** Write a 220-word hard science-fiction scene as a salvage engineer cycles open the inner hatch of an abandoned orbital relay station. Zero-gravity dust floats across a single amber suit lamp. Show the moment she realizes the station's life-support scrubbers were shut down from the inside.

### Sample A
The relay station’s inner hatch resisted her pry bar before yielding with a metallic groan. Yara braced her boots against the outer frame and pulled, swinging herself into the central corridor of *Kestrel*. Zero-gravity dust—fine as talc—hung suspended in the beam of her amber suit lamp, each particle a frozen constellation. She flicked the lamp off and let her helmet lights take over, and the dust didn’t move. It simply hung there, undisturbed, like a photograph of a snowstorm.

### Sample B
The mag-lock disengaged with a structural groan that vibrated through Elara’s boots. As the inner hatch cycled open, the vacuum-seal hiss died into an eerie, pressurized silence. Her amber suit lamp cut a lonely cone through the dark, illuminating a thick, swirling nebula of particulate matter. It wasn't just dust; it was a suspended cloud of desiccated skin cells and micro-fibers, dancing in zero-gravity stillness.

Elara drifted inward, her thruster pack puffing rhythmic bursts of nitrogen. The air felt heavy, cloying with the metallic tang of recycled CO2. She bypassed the primary console, her HUD scanning the station’s telemetry. 

"Power is nominal," she whispered, her voice rasping in her helmet. "But the atmosphere is dead."

She reached the life-support manifold. Her gloved fingers danced over the haptic interface, pulling the diagnostic logs. The readout froze her breath. The scrubber arrays hadn't failed due to mechanical fatigue or solar flare interference. The logs showed a manual override command—a clean, sequential shutdown of the carbon dioxide scrubbers and the oxygen injection valves.

The timestamp was precise. The command hadn't come from the central AI or a remote command signal. It had been executed from the local terminal inside the crew quarters. They hadn't run out of air; they had chosen to stop breathing.

---

## Round 2 (seed=202) — W04_derelict_airlock (hard_scifi)
**Prompt:** Write a 220-word hard science-fiction scene as a salvage engineer cycles open the inner hatch of an abandoned orbital relay station. Zero-gravity dust floats across a single amber suit lamp. Show the moment she realizes the station's life-support scrubbers were shut down from the inside.

### Sample A
The pneumatic seal hissed, a dry, mechanical rasp that died instantly in the vacuum-stilled air of the relay station. Elara cycled the inner hatch, her mag-boots clanking against the titanium bulkhead with a hollow, lonely ring. She thumbed the toggle on her EVA suit; a single amber beam sliced through the gloom, illuminating a slow-motion nebula of particulate matter.

The dust was wrong. It wasn't the crystalline frost of a hull breach or the jagged debris of a kinetic impact. It was soft, organic, and thick—sloughed skin cells and microscopic fibers suspended in a perfect, stagnant cloud. In zero-G, it drifted like incense smoke, caught in the periphery of her lamp.

She swept the beam toward the environmental console. The readout was dark, but the physical override lever sat in the ‘manual lockout’ position. Elara froze. The scrubber telemetry didn't show a catastrophic failure or a power surge. The logs, etched into the local buffer, indicated a deliberate command sequence. 

The atmospheric composition was pure nitrogen and trace CO2—the signature of a controlled shutdown. Someone hadn't just lost air; they had turned the station into a tomb by flipping the switch from the command deck. The silence wasn't an accident. It was an execution.

### Sample B
The amber suit lamp cut a dull wedge through the dark, illuminating a slow constellation of suspended particulate. Kael braced her boot against the inner hatch’s guide rail and cranked the manual release. The wheel resisted, then gave with a shudder that traveled up her forearms.

Zero-gravity dust bloomed outward from the seal, a glittering nebula of dead skin and oxidized polymer drifting in the lamp’s beam. She held her breath, watching the motes swirl in the recycled air of her helmet. The station had been dead for eleven years—long enough for the solar wind to scour its hull bare, long enough for the internal atmosphere to settle into a still, gray suspension.

The hatch swung inward, and the cabin exhaled.

Kael floated forward, her suit’s external mic picking up the faint, rhythmic tick of her own pulse. The relay’s main corridor stretched ahead, a tunnel of darkened viewports and dormant consoles. She swept the lamp toward the life-support alcove. The scrubber array sat silent, its intake valves frozen open, its exhaust ports sealed tight.

---

## Round 3 (seed=303) — W04_derelict_airlock (hard_scifi)
**Prompt:** Write a 220-word hard science-fiction scene as a salvage engineer cycles open the inner hatch of an abandoned orbital relay station. Zero-gravity dust floats across a single amber suit lamp. Show the moment she realizes the station's life-support scrubbers were shut down from the inside.

### Sample A
The amber suit lamp swept in a slow arc, catching dust that hung motionless in the zero-gravity dark. Each particle glittered like a frozen star cluster, suspended in the cone of light before drifting just beyond its reach. Yara counted her breaths against the suit’s internal chronometer, the only rhythm her body trusted now.

The inner hatch groaned as its manual override caught. She’d expected the relay’s automated systems to have failed decades ago, leaving the door locked by default. Instead, the wheel turned with the reluctance of something deliberately held in place.

Yara pulled. The hatch swung outward, and the dust field parted around her helmet like a curtain of slow snow. Inside, the relay’s main corridor stretched away, its emergency strips long dead. She raised the lamp and swept it across the walls.

The scrubber housings lined the ceiling—four of them, each one capped with a maintenance panel. She angled the light upward. Every panel was sealed tight. No breach. No corrosion. No exposure to vacuum.

Her fingers found the nearest panel’s latch. It opened with a soft click.

Inside, the scrubber’s filter cartridge sat pristine, its indicator window showing a full charge. She checked the next. Same result. The third. The fourth.

All four units intact. All four units powered down.

Yara lowered her lamp. The dust continued its slow dance in the amber glow. The station hadn’t been abandoned to the void. Someone had walked through this corridor, checked these panels, and chosen to turn off the machines themselves.

### Sample B
The pneumatic seal hissed, a dry, metallic rasp that vibrated through Elara’s gauntlets. As the inner hatch uncoupled, the pressure differential didn't equalize with a roar, but with a pathetic, hollow wheeze. 

She drifted into the airlock, her mag-boots disengaged to conserve momentum. Her suit’s amber lamp cut a lonely swath through the dark, illuminating a thick, swirling nebula of particulate matter. It wasn't frozen condensation; it was desiccated skin cells and pulverized insulation, dancing in zero-G like a slow-motion explosion of gray silt. 

Elara frowned, her HUD scanning the atmospheric composition. *CO2: 4.2%. O2: 0.08%.* 

"Vacuum breach?" she whispered, her breath fogging the visor. 

No, the hull integrity was nominal. She drifted toward the environmental control console, her lamp sweeping over the interface. The terminal glowed a sickly, static-ridden red. She tapped the diagnostic log, her heart hammering against her ribs. The telemetry didn't show a mechanical failure or a slow leak. The life-support scrubbers hadn't malfunctioned; the command history showed a manual override. 

Someone had bypassed the automated cycling protocols and initiated a hard shutdown of the carbon dioxide scrubbers. They hadn't died from a leak. They had simply turned off the air, choosing to suffocate in the silence.

---

## Round 1 (seed=101) — W05_bakery_dawn (sensory_slice_of_life)
**Prompt:** Write a 200-word sensory vignette of a stone-hearth neighborhood bakery opening an hour before sunrise in winter. Capture the contrast between the frozen alley outside and the steam, yeast, blistered crust, and cast-iron peel inside, through the hands of an elderly baker.

### Sample A
The blue-black frost of the alley clings to Elias’s coat like needles, the air so brittle it feels as though it might snap. He shivers, his knuckles gnarled and stiff from the pre-dawn chill, until he pushes through the heavy oak door. 

Immediately, the world transforms. The biting ice is swallowed by a tidal wave of warmth—a thick, humid embrace smelling of fermented yeast and toasted grain. Inside, the stone hearth breathes. It is a living thing, radiating a deep, subterranean heat that seeps into his aching joints.

Elias reaches for the cast-iron peel, its handle familiar and warm. He slides it into the maw of the oven, where the embers glow like banked gold. As he pulls the first batch free, the sound is a symphony: the frantic, musical crackle of blistered crusts cooling in the air. He lifts a loaf, the steam rising in ghostly plumes against the dim light, smelling of caramelized sugar and woodsmoke. The frost outside is a memory; here, amidst the flour-dusted shadows, the world is soft, golden, and rising.

### Sample B
Outside, the alley is a corridor of blue-black frost. The cobblestones hold the night’s cold like a grudge; a thin crust of ice glazes the gutter, and the brick wall exhales a faint, mineral chill that numbs the knuckles.

Inside, the world inverts. The stone hearth—a black mouth built into the wall—radiates a heat that presses against the face before the door is fully shut. The baker’s hands, mapped with pale scars and swollen at the joints, move without thinking: a fist of dough pressed into a bed of flour, the wet collapse of gluten beneath the heel. Yeast breathes out, warm and sour-sweet, a living exhalation that fogs the window glass. Steam rises from the oven’s lip in slow, ghostly ribbons, curling over the loaves already blistering and darkening in the dark. The baker slides a long cast-iron peel beneath a boule, its surface crackling and blackening, and withdraws it with a single practiced motion. The crust fractures with a sound like distant ice breaking on a river. Outside, the alley still holds its frozen breath; inside, the room sweats, and the day begins in flour and ash.

---

## Round 2 (seed=202) — W05_bakery_dawn (sensory_slice_of_life)
**Prompt:** Write a 200-word sensory vignette of a stone-hearth neighborhood bakery opening an hour before sunrise in winter. Capture the contrast between the frozen alley outside and the steam, yeast, blistered crust, and cast-iron peel inside, through the hands of an elderly baker.

### Sample A
The alley is a blue-black throat of ice. Frost feathers the brickwork; the cobblestones hold the night’s cold like a grudge, and the wind threads through the narrow gap between buildings with a sound like tearing cloth.

Inside, the bakery breathes. Steam rises from a vat of boiling water, curling toward the low ceiling in slow, wet ribbons. The air is thick with the sweet, sour smell of fermenting dough—yeast alive and working in the dark. The stone hearth, built the year the baker’s father was born, radiates a heat that settles into the bones.

His hands, mapped with old scars and burned by a thousand peels, press into the dough. It yields warm and slack beneath his palms, then springs back, alive. He slides the cast-iron peel beneath a loaf, the metal hissing faintly where it meets the oven floor. The crust blisters, cracks, darkens to the color of wet earth. He pulls it free, sets it on the rack, and the whole shop exhales: flour-dust, char, butter, the iron tang of the oven door. Outside, the alley still waits, frozen. Inside, everything is rising.

### Sample B
Outside, the alley is a throat of blue shadow, choked by a frost so brittle it seems to crack the cobblestones. The air is a razor, slicing through the heavy wool of Elias’s apron, smelling of nothing but iron and frozen breath. 

But inside, the world is amber. 

The heavy oak door clicks shut, sealing out the biting wind and replacing it with the thick, humid embrace of the hearth. Elias moves through the haze of rising steam, his joints aching in rhythm with the pre-dawn stillness. The air here is alive—a heavy, intoxicating perfume of fermented yeast and toasted grain. 

He reaches for the cast-iron peel, its handle warm from the proximity of the fire. With a practiced, rhythmic motion, he slides the metal into the maw of the stone oven. The heat is a physical weight against his skin, a fierce contrast to the numbing dark outside. As he pulls the loaves free, the crusts hiss and sing—a tiny, crackling symphony of caramelizing sugars. He touches a blistered surface, feeling the crunch of the scorched flour, the warmth blooming against his calloused palms like a small, captured sun.

---

## Round 3 (seed=303) — W05_bakery_dawn (sensory_slice_of_life)
**Prompt:** Write a 200-word sensory vignette of a stone-hearth neighborhood bakery opening an hour before sunrise in winter. Capture the contrast between the frozen alley outside and the steam, yeast, blistered crust, and cast-iron peel inside, through the hands of an elderly baker.

### Sample A
Outside, the alley is a throat of blue shadow, choked by a frost so sharp it seems to crackle in the silence. The cobblestones are slick with black ice, and the air tastes of iron and biting nothingness.

But inside, the world is amber.

Elias moves through the pre-dawn haze, his joints aching in sympathy with the cold, until he hits the radius of the hearth. Here, the atmosphere is thick, a humid embrace of rising yeast and toasted grain. He breathes in the scent—warm, fermented, and alive—a stark defiance against the winter gloom.

His gnarled hands, mapped with blue veins and dusted in white flour, grip the long handle of the cast-iron peel. He slides it into the maw of the stone oven. The heat is a physical weight, a golden roar. As he pulls the trays clear, the loaves emerge: dark, blistered crusts singing a frantic, crackling song as they meet the cool air. He touches a boule; it is a sun held in his palms, radiating a primal, yeasty heat that seeps through his skin and settles deep in his bones, warming him from the inside out.

### Sample B
The alley outside is a throat of frozen breath, cobblestones glazed in black ice that swallows the amber streetlamp whole. The baker presses his thumb to the door latch—cold metal biting through calloused skin—and the neighborhood exhales.

Inside, the air is thick, almost liquid, with the sweet rot of fermenting dough and the mineral tang of the stone hearth, banked low but still radiating a heat that makes the windows sweat. Steam curls from a vat of boiling water set beside the oven mouth, ghosting upward to mingle with the yeast-sour exhalation of the proofing loaves.

His hands, mapped with old burns and flour-scarred creases, guide the cast-iron peel into the maw. The crust blisters instantly—a network of dark cracks spreading like lightning across a pale surface—releasing a sharp, caramelized smoke. He withdraws the peel, and the loaf emerges dark-veined, its surface ticking faintly as it cools. The alley’s silence presses against the window; inside, the oven roars its low, patient roar, and the baker’s hands do not tremble.

---

## Round 1 (seed=101) — W06_courtroom_goat (dry_comedy)
**Prompt:** Write a 220-word comedic scene in a small-town municipal court where a retired postman is defending himself against a citation for letting his prize pygmy goat wander into a county commissioner's tulip bed. Keep the judge deadpan and the dialogue crisp.

### Sample A
“Mr. Henderson, you are charged with one count of ‘Unlicensed Bovine Nuisance in a Restricted Garden Zone.’ How do you plead?”

“Guilty, Your Honor. But not guilty in the sense that I didn’t know the commissioner had planted *Dutch* tulips.”

The judge peered over his spectacles. “Explain.”

“Well, Your Honor, I didn’t plant them. The commissioner did. I just delivered his mail. But my goat, Barnaby—”

“Barnaby?”

“A term of endearment, Your Honor.”

The judge’s eye twitched. “Proceed.”

“Barnaby has a particular fondness for the color red, which, as it happens, is the color of the commissioner’s tulips. He ate them in a single afternoon. He did not, however, chew them.”

“Then the tulips are gone.”

“Not at all. He simply moved them. From the ground to the sky. The commissioner’s garden is now a meadow of floating petals.”

The judge stared. “That is not how gravity works.”

### Sample B
Judge Miller adjusted his spectacles, staring at the small, defiant man in the defendant’s chair.

"Mr. Henderson," Miller said, his voice a flat monotone. "You are charged with misdemeanor trespass and floral vandalism. Specifically, your goat, Barnaby, breached Commissioner Higgins’ private tulip bed."

Arthur Henderson, a man who smelled faintly of peppermint and old mailbags, stood tall. "Your Honor, I plead not guilty by reason of goat-induced gravitational error."

The courtroom went silent. Miller blinked. "Explain."

"Barnaby is a pygmy goat, not a criminal mastermind," Henderson insisted. "He didn't 'invade.' He was performing a quality control inspection. Those tulips were structurally unsound. He was merely testing their durability."

"He ate forty-two premium bulbs, Arthur," the court clerk whispered.

"He was composting!" Henderson countered. "He’s a mobile, organic fertilizing unit. He’s a public service, not a nuisance."

Miller leaned forward, his face an unreadable mask of judicial exhaustion. "The Commissioner is requesting a fine of two hundred dollars and a lifetime ban on all hoofed livestock within fifty yards of his property."

"That’s a heavy sentence for a herbivore," Henderson muttered.

"The law doesn't care about the defendant's diet," Miller said. "Do you have any further evidence, or just more excuses for your lawnmower with legs?"

"I have a very apologetic goat," Henderson said.

"Denied."

---

## Round 2 (seed=202) — W06_courtroom_goat (dry_comedy)
**Prompt:** Write a 220-word comedic scene in a small-town municipal court where a retired postman is defending himself against a citation for letting his prize pygmy goat wander into a county commissioner's tulip bed. Keep the judge deadpan and the dialogue crisp.

### Sample A
Judge Miller stared at the goat, which was currently chewing on a legal brief. 

“Mr. Higgins,” Miller said, his voice a flatline. “The citation states your pygmy goat, Barnaby, breached the perimeter of Commissioner Vance’s prize-winning tulip bed. This is a violation of Municipal Code 42: Unsanctioned Flora Consumption.”

Arthur Higgins, a man who smelled faintly of peppermint and old envelopes, adjusted his spectacles. “Your Honor, I move for dismissal on the grounds of irresistible impulse.”

“Explain,” Miller deadpanned.

“Barnaby isn't a trespasser; he’s a critic,” Higgins said, gesturing grandly. “He saw those tulips and recognized a lack of structural integrity. He was performing a quality control audit.”

“He ate forty dollars worth of Dutch bulbs, Arthur.”

“He was composting! He’s a sustainability enthusiast.”

The courtroom door creaked open. Commissioner Vance, red-faced and trembling, marched in. “That goat has the soul of a vandal, Judge!”

“Sit down, Vance,” Miller said without looking up. “The goat is currently eating your tie.”

Vance looked down. Barnaby had indeed stretched his neck toward the bench. 

“Your Honor,” Higgins pleaded, “if you fine me, I’ll have to sell his grazing rights, and he’ll end up in the county landfill. It’s a cycle of destruction.”

Miller sighed, rubbing his temples. “Fine. Dismissed. But if that goat eats my gavel, you’re going to jail.”

### Sample B
"Mr. Henderson," Judge Dolores Mott said, peering over her glasses at the docket, "you are charged with allowing a creature of the genus *Capra* to commit what the county code describes as 'botanical trespass' in the tulip bed of Commissioner Yoon."

"Your Honor, with respect, it was a pygmy goat named Sir Reginald. And he didn't commit trespass; he committed *lunch*."

"The citation specifies damage to four hundred and twelve bulbs."

"Four hundred and twelve? Sir Reginald has the constitution of a wood chipper. He ate the *bulbs*, Judge. Not the flowers. The bulbs. The tulips were collateral."

Commissioner Yoon, seated in the gallery, raised a hand. "My husband says the goat also urinated on the *Garden of Eden* plaque."

"Your Honor," the retired postman said, standing slightly too fast, "I have delivered mail to this town for thirty-one years. I have walked dogs through blizzards. I have carried packages to porches where the residents had *forgotten* they ordered anything. And now I must defend my mailbag—" he patted his chest— "my *person*—against a charge of *botanical vandalism* for a goat that eats like a lawnmower?"

---

## Round 3 (seed=303) — W06_courtroom_goat (dry_comedy)
**Prompt:** Write a 220-word comedic scene in a small-town municipal court where a retired postman is defending himself against a citation for letting his prize pygmy goat wander into a county commissioner's tulip bed. Keep the judge deadpan and the dialogue crisp.

### Sample A
Judge Miller stared at the man in the defendant’s chair. Arthur Pringle, a retired postman, sat with the rigid posture of someone awaiting a federal indictment.

"Mr. Pringle," Miller said, his voice a flat line. "The citation states you allowed a 'rogue livestock unit' to breach the private garden of Commissioner Higgins."

"It wasn't a unit, Your Honor," Arthur said, eyes flashing. "It was Barnaby. And he didn't breach. He conducted a tasting tour."

"He ate four dozen prize-winning tulips," Miller noted, flipping a page.

"He was hungry! And those tulips were looking quite smug," Arthur countered. "Besides, the Commissioner’s fence is essentially a suggestion. It’s structurally unsound."

"The fence is cedar, Mr. Pringle. It's quite sturdy."

"For humans, maybe. But Barnaby is a specialist. He’s got the head of a battering ram and the soul of a connoisseur."

Miller leaned forward, his face an unreadable mask of judicial indifference. "The Commissioner is seeking fifty dollars in damages and a permanent restraining order against the goat."

Arthur gasped. "A restraining order? He’s a goat! He doesn't even know what a zoning ordinance is!"

"He knows tulips," Miller said. "The court finds you guilty. Fifty dollars. Pay the clerk, or the goat goes to the county petting zoo."

Arthur sighed. "Fine. But don't blame me if he tastes the bailiff's begonias next."

### Sample B
**MUNICIPAL COURT, DOCKET 7B**

**JUDGE:** Mr. Henderson, you're cited for failure to restrain a goat in a public right-of-way.

**HENDERSON:** Your Honor, I've been a postman for thirty-two years. I know the right-of-way. I *built* the right-of-way.

**JUDGE:** And yet your goat ate the tulips.

**HENDERSON:** She did not eat them, sir. She *contemplated* them.

**JUDGE:** Contemplated.

**HENDERSON:** The goat is named Prudence. She's a contemplative animal.

**JUDGE:** The commissioner's tulips cost forty dollars.

**HENDERSON:** Forty dollars? For flowers that bloom for two weeks and then look like a sad salad?

**JUDGE:** The commissioner is a sensitive man.

---

## Round 1 (seed=101) — W07_gothic_conservatory (gothic)
**Prompt:** Write a 220-word gothic scene as a newly hired archivist enters a neglected glass conservatory attached to a cliffside estate during a coastal fog. Overgrown night-blooming vines press against cracked panes, and someone has recently pruned only the thorns along the center aisle.

### Sample A
The iron door groaned, a rusted protest against my intrusion, as I stepped into the belly of the glass conservatory. Outside, the coastal fog had swallowed the cliffs, turning the world into a suffocating shroud of grey. Inside, the air was thick, tasting of damp peat and something sickly sweet—the breath of things that thrive in shadow.

The structure was a skeletal ruin of iron and salt-pitted glass. Beyond the cracked panes, moonlight struggled to pierce the mist, casting long, distorted shadows that danced like drowning specters. Overgrown night-blooming vines, thick as a man’s wrist, pressed against the glass with a rhythmic, suffocating pressure, as if trying to claw their way into the warmth.

I raised my lantern, the amber glow trembling in my grip. The light cut through the gloom, illuminating the center aisle. My breath hitched. Amidst the chaotic tangle of briars and choking ivy, a single path had been cleared. The thorns had been meticulously, violently pruned away, leaving a smooth, naked corridor of dirt that sliced through the madness of the greenery. The cuts were fresh; the scent of sap hung heavy and metallic, like spilled blood. Someone had been working here recently, tending to the garden’s heart with a surgeon’s precision, leaving a trail for something to walk unseen.

### Sample B
The fog had rolled in from the sea by the time Maren stepped through the service door into the conservatory. The glass panes, webbed with cracks and filmed with age, blurred the world outside into a smear of grey water and black cliff. Inside, the air was thick with the green, vegetal breath of night-blooming vines—jasmine and moonflower, she thought, though their exact species was lost to her. They coiled along iron trellises gone to rust, pressing against the glass like pale fingers testing for warmth.

What arrested her was the pruning. Someone had taken shears to the center aisle alone, trimming the thorns back to blunt nubs, leaving the side passages tangled and wild. It was deliberate, surgical, almost ritualistic, as though the aisle were a path meant to be walked. Maren traced the cut stems with her fingertip; the wounds were fresh, weeping sap that smelled faintly of copper.

Somewhere beyond the glass, the sea moaned against the rocks. She stood very still, aware of the estate behind her—empty, forgotten, yet clearly not unattended. Someone had been here. Someone had chosen this single, narrow way through the thorns and left it bare, as if expecting her to follow it.

---

## Round 2 (seed=202) — W07_gothic_conservatory (gothic)
**Prompt:** Write a 220-word gothic scene as a newly hired archivist enters a neglected glass conservatory attached to a cliffside estate during a coastal fog. Overgrown night-blooming vines press against cracked panes, and someone has recently pruned only the thorns along the center aisle.

### Sample A
The fog came first, a slow tide of grey that swallowed the cliffside estate whole, leaving the conservatory a glass cage suspended between land and sea. Maren pushed through the iron gate, its hinge screaming a protest that died in the wet air. Inside, the air hung thick and green, heavy with the smell of brine and rotting petals. Night-blooming vines, thick as rope, pressed their pale faces against cracked panes, their leaves splayed flat like desperate hands seeking the glass.

She should have expected it. The estate had been abandoned for decades, yet the center aisle told a different story. Someone had been here. Recently. The thorns along that single path had been cut back, the cuts still pale and weeping, while the rest of the conservatory remained wild, choking itself in tangled green. A path through the overgrowth, deliberately cleared, as if someone meant to walk it. Or as if someone had walked it before her.

Maren stepped onto the cleared aisle, her boots finding the damp flagstones beneath the moss. The glass around her sweated, and somewhere in the fog beyond the panes, the sea whispered its endless, patient name. She should have turned back. She should have seen the thorns.

### Sample B
The heavy iron door groaned, a rusted throat protesting my intrusion. As I stepped into the conservatory, the salt-thick fog of the Atlantic swallowed the estate behind me, turning the world into a shroud of grey. Inside, the air was stagnant, smelling of damp earth and something sickly sweet, like lilies left too long in a funeral parlor.

The structure was a skeletal ribcage of iron and cracked glass. Outside, the cliffside roared, the waves battering the foundations with rhythmic, violent intent. Night-blooming vines, thick as a man’s wrist, pressed against the panes, their dark leaves shivering like restless hands against the glass. They seemed to be trying to push their way in, hungry for the warmth of the decay within.

I raised my lantern, the amber light cutting through the gloom. My breath hitched. Along the center aisle, the chaos of the overgrowth stopped abruptly. A path had been cleared—not by nature, but by a blade. The unruly brambles had been meticulously pruned, leaving only the jagged, obsidian-black thorns to line the walkway like a row of serrated teeth. The cuts were fresh, weeping a dark, sap-like ichor that glistened in my light. Someone had been here, tending to the cruelty of the garden, and they had left the path open for me.

---

## Round 3 (seed=303) — W07_gothic_conservatory (gothic)
**Prompt:** Write a 220-word gothic scene as a newly hired archivist enters a neglected glass conservatory attached to a cliffside estate during a coastal fog. Overgrown night-blooming vines press against cracked panes, and someone has recently pruned only the thorns along the center aisle.

### Sample A
The iron key groaned in the lock, a rusted protest against my intrusion. As I stepped into the conservatory, the coastal fog swallowed the estate behind me, pressing its damp, grey fingers against the cracked glass panes. Inside, the air was thick—not with the scent of jasmine, but with the cloying, sweet rot of things that thrive in shadows.

Moonlight struggled through the grime, casting skeletal shadows of overgrown night-blooming vines. They writhed against the glass like starving limbs, their dark leaves shivering in the salt-heavy wind. The silence was absolute, save for the rhythmic *thrum* of the Atlantic crashing against the cliffs far below the floorboards.

I raised my lantern, the amber glow cutting through the gloom. My breath hitched. Down the center aisle, the chaos of the jungle met a terrifying precision. Amidst the riot of strangling greenery, a path had been cleared. The jagged, wicked thorns that usually guarded the flora had been surgically removed, leaving only smooth, emerald stems trailing toward the dark heart of the glasshouse. The cuts were fresh, weeping pale sap that glistened like milk in my light. Someone had been working here recently, tending to the garden with a predator’s intent, carving a way through the madness.

### Sample B
The door groaned against its rusted hinges, admitting Maren into a cathedral of glass and green. Beyond the panes, the coastal fog pressed close, a grey sea of mist that erased the cliff’s edge and turned the estate’s garden into a rumor. Within, the conservatory exhaled dampness—earth and rot and the faint, copper tang of rainwater pooled in broken gutters overhead.

Night-blooming vines, thick as a man’s wrist, coiled across the cracked glass in tangled networks, their white blossoms closed in daylight but beginning to unfurl as the afternoon dimmed. Each petal was a secret; Maren had read the estate’s ledgers and knew the vines were not native to this coast.

She stepped onto the gravel path. The center aisle had been pruned. Recent. The cuts were clean, pale where the stems had been severed, and the thorns—long, black, cruel—had been removed only along this single lane. The side aisles remained choked, their thorns still bristling.

Maren’s fingers found the nearest stem. The vine was warm. Not from the sun—clouds had swallowed it hours ago—but from something metabolic, something that pulsed beneath the bark like a vein. She withdrew her hand. The blossom nearest her thumb had opened fully, revealing a throat of dark violet.

Somewhere in the fog beyond the glass, a bell tolled.

---

## Round 1 (seed=101) — W08_safehouse_debrief (crime_thriller)
**Prompt:** Write a 220-word scene inside a cramped motel room twenty minutes after a botched art courier handoff. Two partners lay the soaked canvas frame across the Formica table while sirens pass two blocks away. Establish distrust through small physical gestures rather than inner monologue.

### Sample A
The canvas frame rested across the Formica table, its wooden edges dark and swollen from rain. Marcus turned the frame a quarter-inch clockwise, then back, then a quarter-inch clockwise again—his thumb tracing the wet grain where the courier’s hands had gripped it. He did not look at Elena.

Elena stood at the window, watching the red and blue lights crawl past on the road two blocks away. She pressed her palm flat against the glass, held it there three seconds, then pulled it back as if the pane had burned her. She turned from the window and walked to the table.

Neither of them touched the canvas.

Marcus set his keys on the table beside the frame. He set them back, then forward an inch, then back again. Elena watched his hands. She folded her arms across her chest, uncrossed them, crossed them the other way. She sat down on the edge of the bed without taking off her coat.

Marcus slid the canvas an inch toward her side of the table. He did not offer to move it further. She did not ask him to.

She reached into her bag and pulled out a receipt for the courier’s fee—crumpled, damp at one corner. She smoothed it against the table with her index finger, pressed the crease flat, then lifted it and held it up between them. He looked at it. He looked at her.

She folded the receipt into quarters and tucked it back into her bag.

### Sample B
The Formica table groaned under the weight of the gilded frame. Water dripped from the sodden canvas, pooling into a dark ring that stained the cheap laminate. 

Elias didn't look at Julian. He gripped the edge of the table, his knuckles white against the peeling veneer, and began scrubbing a smear of red from his cuff with a dry napkin. He kept his eyes fixed on the rhythmic, frantic movement of his own hands.

Julian leaned against the door, the deadbolt already thrown. He reached for a cigarette, his fingers trembling just enough to make the lighter click twice before catching. He exhaled a plume of gray smoke toward the ceiling, his gaze tracking the slow, rhythmic drip of water from the frame onto the linoleum. 

When Elias reached for the heavy flashlight to inspect the damage, Julian’s hand twitched toward his waistband. Elias froze, his fingers hovering inches from the metal. He didn't turn around; he simply tightened his jaw, the muscle pulsing rhythmically.

Outside, a siren wailed, cutting through the humid air two blocks away. The sound vibrated the thin glass of the window. Neither man moved toward the light. Instead, Elias slowly slid the flashlight toward the center of the table, keeping his palm over the lens, while Julian watched the movement through a veil of smoke.

---

## Round 2 (seed=202) — W08_safehouse_debrief (crime_thriller)
**Prompt:** Write a 220-word scene inside a cramped motel room twenty minutes after a botched art courier handoff. Two partners lay the soaked canvas frame across the Formica table while sirens pass two blocks away. Establish distrust through small physical gestures rather than inner monologue.

### Sample A
The neon sign outside flickered, casting rhythmic pulses of bruised violet across the Formica tabletop. Elias gripped the edge of the laminate, his knuckles white, as he slid the sodden canvas frame toward the center of the room. The wood groaned.

Julian didn't move to help. He sat on the edge of a sagging mattress, his shadow stretching long and jagged against the peeling wallpaper. He pulled a silver lighter from his pocket, flicking it open and shut—*clack, clack, clack*—the metallic rhythm sharper than the distant, wailing sirens two blocks over.

Elias reached for a towel to dab at the moisture seeping from the frame, but Julian’s hand shot out, pinning the corner of the cloth to the table. Their eyes didn't meet, but the air between them tightened. Julian slowly retracted his hand, leaving the towel damp and useless.

Elias wiped a smudge of oil from his thumb onto his jeans, then tucked his hands deep into his pockets, refusing to let them shake. He shifted his weight, his heel scraping harshly against the linoleum, a sound like bone on stone. Julian responded by leaning back into the dark, his eyes fixed on the door, his thumb tracing the serrated edge of the lighter.

### Sample B
The canvas frame lay across the Formica table, still dripping.

Marcus set down his keys on the nightstand—too hard, too deliberate. He pulled the chair back from the table and sat at the far end, not close enough to touch the painting but not far enough to ignore it.

Elena stood by the window, arms folded. She hadn't moved since they'd entered the room. A siren wailed past two blocks away, then another. Neither flinched.

"You're staring at it," Marcus said.

"I'm staring at the water pooling under it."

He glanced down. The bead of moisture crept toward the table's edge. He reached for his shirt to blot it, then stopped his hand mid-air. He didn't.

Elena unfolded her arms. She touched the canvas's corner with one finger, pressed, then withdrew as if the fabric might burn. "You said you'd wrapped it properly."

"I did."

"You're sitting too far away."

He shifted forward an inch. The chair creaked. He caught himself, looked at Elena, then at the canvas. The water had reached the table's lip and hung there, trembling.

Elena stepped back from the window. She didn't reach for the canvas. She reached for her phone, turned it over in her palm twice, then set it face-down on the table—between them and the painting.

---

## Round 3 (seed=303) — W08_safehouse_debrief (crime_thriller)
**Prompt:** Write a 220-word scene inside a cramped motel room twenty minutes after a botched art courier handoff. Two partners lay the soaked canvas frame across the Formica table while sirens pass two blocks away. Establish distrust through small physical gestures rather than inner monologue.

### Sample A
The canvas dripped onto the Formica table, pooling around its edges like a slow bruise. Voss laid it down flat, palms pressed against the wood as though testing its weight. He did not look at Maren. He looked at the frame’s corner, where a hairline crack split the gesso beneath the paint.

Maren stood by the door, her coat still buttoned to the throat. She had not removed her gloves. She watched Voss’s hands, the way his thumb lingered near the crack, the way he angled his body away from her rather than toward her. He was not the man she had hired.

Sirens passed two blocks away, fading into the hum of the vending machine outside. Neither flinched.

Maren stepped forward. She reached for the canvas, then pulled her hand back as if it had moved. Voss noticed. He straightened, wiped his palms on his trousers, and met her eyes for the first time. His expression held nothing—no warmth, no apology, just the flat patience of a man calculating a number.

Maren sat on the edge of the bed, the mattress groaning beneath her. She kept her gloves on. She said nothing. He said nothing. The canvas continued to weep.

### Sample B
The neon sign outside hummed, casting a rhythmic, sickly pink pulse across the Formica tabletop. Elias didn't look at Julian; he kept his eyes fixed on the heavy, water-damaged frame resting between them. He gripped the edge of the table, his knuckles turning a waxy white, as if bracing for an impact.

Julian sat opposite him, his breathing shallow. He reached for a lukewarm coffee in a paper cup, but his hand hovered inches from the rim, trembling just enough to make the liquid ripple. He pulled his hand back, tucking it into his jacket pocket, and leaned away from the table.

Elias reached for a rag to wipe the moisture from the wood, but his movement was sharp, jagged. He stopped halfway, his gaze flicking to the door, then to the bulge of the handgun tucked into Julian’s waistband. 

Julian noticed the stare. Instead of relaxing, he shifted his weight, the cheap springs of the motel chair screeching against the linoleum. He didn't apologize. He simply stared at the peeling wallpaper, his jaw set so tight a muscle jumped in his cheek. 

Two blocks away, a siren wailed, rising and falling. Elias slowly withdrew his hand from the table, curling his fingers into a fist, and placed it firmly on his own lap.

---

## Round 1 (seed=101) — W09_timberline_dawn (wilderness_survival)
**Prompt:** Write a 200-word wilderness scene of a backcountry surveyor waking above timberline after an unexpected October squall collapsed half his bivy. He has to coax a spark from damp tinder with stiff hands while tracking an elk herd moving below the ridge.

### Sample A
The wind didn't howl; it hissed, a predatory sound that had shredded the nylon of his bivy during the night. Elias woke shivering, the bitter scent of ozone and crushed granite filling his lungs. Half his shelter was a mangled heap of blue fabric, plastered against the frozen scree by the October squall. 

His fingers felt like wooden pegs, clumsy and unresponsive. He knelt in the lee of a jagged boulder, his breath blooming in thick, frantic clouds. With trembling hands, he teased a pinch of tinder from a lightning-scarred larch, but the wood was weeping with frost. He struck the ferrocerium rod, his knuckles aching with every desperate scrape, praying for a single, defiant spark to catch the damp fibers.

A movement below the ridge broke his focus. Through the swirling gray mist, a silhouette emerged—an elk bull, heavy-antlered and ghost-like, leading a small herd toward the lower valley. They moved with a rhythmic, somber grace, oblivious to the storm’s teeth. Elias watched them, a hollow ache in his chest. They were heading for cover, while he sat perched on the edge of the world, fighting for a spark to keep the dark at bay.

### Sample B
The cold had done its work overnight.

Kell woke to the sound of wind tearing through the gap where his bivy’s rain fly had been—now collapsed, half-frozen and pinned beneath a lattice of snow-laden branches. The October squall had come without warning, dumping a foot of wet powder across the ridge before dawn. Above timberline, there was nowhere to hide; the alpine tundra stretched in every direction under a pale, graying sky.

His fingers were stiff, almost useless, as he worked a cotton ball soaked in petroleum jelly between his thumb and forefinger, trying to coax it into a shape that might catch. The ferro rod spat orange sparks, but the tinder stayed damp, stubborn as the weather itself. He breathed on it slowly, gently, the way you’d coax a sleeping animal.

Below him, the ridge fell away into a bowl of sage and broken granite. Through the scope, he could just make out the dark shapes of elk moving along the basin floor—six cows and two calves, moving south along the creek bed. Their tracks were already half-filled with snow.

He marked the herd’s position in his field notebook, then looked back at his fire, still waiting to be born.

---

## Round 2 (seed=202) — W09_timberline_dawn (wilderness_survival)
**Prompt:** Write a 200-word wilderness scene of a backcountry surveyor waking above timberline after an unexpected October squall collapsed half his bivy. He has to coax a spark from damp tinder with stiff hands while tracking an elk herd moving below the ridge.

### Sample A
The October squall had broken before dawn, leaving the ridge scraped clean of snow and silence. Half the bivy lay collapsed, its nylon shell frozen into a black wing against the granite. He woke to the cold first—a numbing, absolute pressure against his ribs—then to the elk.

They moved in the bowl below the ridge, a slow tide of tawny bodies threading between spruce, their breath visible in the thin air. He watched them through the gap in the torn shelter, too stiff to move, too cold to think. His fingers had swollen overnight into pale, useless things. He worked the ferro rod with the heel of his palm, grinding it against the striker until his wrist ached. Sparks leapt, died, leapt again. The tinder—a bundle of dry birch bark he'd kept in his jacket pocket—caught on the third strike, a small orange curl that held for a breath before he fed it more.

### Sample B
The wind howled through the jagged granite teeth of the ridge, a predatory sound that signaled the squall had passed, leaving only ruin. Elias sat shivering in the wreckage of his bivy; the nylon was shredded, half-collapsed under a heavy shroud of sleet and late-season snow. The October chill bit deep, turning his breath into ragged plumes of frost.

His fingers felt like wooden pegs, stiff and unresponsive as he fumbled with his ferrocerium rod. Every movement was a battle against numbness. He knelt over a small pile of damp, wind-scoured lichen and shredded bark, his knuckles raw and weeping. He struck the rod, praying for a spark that wouldn't drown in the moisture. *Clack. Clack.* A tiny, orange ember gasped against the tinder, a fragile heartbeat in the vast, grey desolation.

As he nursed the spark, his eyes drifted to the valley floor. Below the timberline, a silhouette moved through the mist—a massive bull elk, leading a small herd toward the lower breaks. They were moving with a desperate, seasonal urgency. Elias watched them, a surveyor of both land and survival, waiting for the fire to catch before the light failed entirely.

---

## Round 3 (seed=303) — W09_timberline_dawn (wilderness_survival)
**Prompt:** Write a 200-word wilderness scene of a backcountry surveyor waking above timberline after an unexpected October squall collapsed half his bivy. He has to coax a spark from damp tinder with stiff hands while tracking an elk herd moving below the ridge.

### Sample A
The cold came first—real, not theoretical—a pressure against the nylon that folded the bivy’s far side into a crease of ice. He woke to the sound of wind threading the granite, a low groan that had no name, and knew the October squall had taken the shelter’s right flank while he slept.

He crawled out into a world stripped of color. Snow lay in drifts along the ridge, and the sky was a flat, wet gray that offered no sun. His fingers, stiff and clumsy inside liner gloves, fumbled for the tinder bundle beneath his pack. The bark was damp, swollen with meltwater, but he worked it between his palms until the fibers loosened and dried.

Below the ridge, through a break in the clouds, he saw them—twelve elk moving in a slow column along the valley floor, their dark bodies small against the first snow. They were headed east, toward the drainage he’d mapped that morning. He needed to be there before they were gone.

He struck the ferro rod once, twice. The third spark caught.

### Sample B
The wind howled through the jagged granite teeth of the ridge, a predatory sound that had shredded Elias’s bivy overnight. He woke shivering, half-buried in a slurry of melting sleet and crushed nylon. The October squall had been a thief, stealing his shelter and leaving him exposed to the thin, biting air of the timberline.

His fingers felt like wooden pegs, stiff and unresponsive from the frost. With teeth chattering, he knelt over a pile of sodden birch bark and dried lichen, his breath blooming in frantic white plumes. He struck the ferrocerium rod with clumsy, heavy movements, praying for a single, defiant spark to catch the damp tinder. Each failed strike felt like a countdown against the encroaching gray sky.

A movement below the ridge caught his eye, breaking the monotony of the scree. A herd of elk was ghosting through the alpine meadows, their heavy bodies moving with a rhythmic, somber grace toward the lower valleys. They were fleeing the coming snow, driven by an ancestral clock. Elias watched them, a hollow ache in his chest, realizing they were moving toward life while he was merely fighting to endure it.

---

## Round 1 (seed=101) — W10_late_diner (psychological_thriller)
**Prompt:** Write a 220-word psychological thriller scene in a fluorescent highway diner at midnight. A waitress notices that the quiet customer in booth four has ordered the exact same pie-and-coffee combination left untouched by a missing state trooper three weeks ago. Build dread through mundane diner detail.

### Sample A
The fluorescent lights hummed their one flat note, the sound that had burrowed into her molars over eleven years of night shifts. Coffee pooled in the pot behind the counter, black and bitter, waiting. The pie case held three cherry pies under their glass dome, the crusts sweating in the cold air.

Booth four. The man in the gray jacket sat with his hands folded on the Formica table, the same posture he’d held for forty minutes. His coffee sat untouched, no steam rising. His cherry pie remained whole, the fork clean beside it.

She’d noticed the order the first time—a pattern so precise it felt rehearsed. Pie and coffee, cherry and black, the exact combination that Trooper Dale Mercer had ordered on the night his body went missing. Three weeks ago, the trooper had sat in this very booth, left the same order untouched, and walked out into the dark. No body. No call.

Now the man in gray sat in that booth, ordering that order, and the diner’s silence thickened around them like the coffee’s bitterness. The refrigerator compressor clicked off. The neon sign outside flickered its pink *OPEN* into the black parking lot.

She poured his coffee from the pot. The liquid hit the mug with a sound too loud for the room. He didn’t blink.

### Sample B
The hum of the fluorescent lights was a physical weight, a rhythmic, electric buzz that vibrated against the Formica tabletop. It was 12:04 AM. The air smelled of burnt decaf and floor wax.

Marge wiped the counter, her rag moving in mechanical circles. Her eyes drifted to booth four. The man sat perfectly still, a silhouette carved from the midnight shadows outside. Before him sat a slice of cherry pie and a ceramic mug of black coffee.

The sight sent a cold needle sliding down her spine.

Three weeks ago, Trooper Miller had sat in that exact spot. He had ordered the same cherry pie, the same black coffee. He had left them untouched, staring at the salt shaker until the night shift ended and he simply… vanished. No struggle, no goodbye. Just a half-eaten crust and a lukewarm cup.

The man in booth four hadn't moved a muscle. He hadn't even breathed deeply enough to fog the window. He was wearing a heavy, dark coat that seemed to absorb the sickly yellow light. 

Marge gripped the damp rag. The pie looked unnervingly fresh, the red filling glistening like a fresh wound under the buzzing tubes. She realized with a jolt of dread that the man wasn't eating. He was waiting.

---

## Round 2 (seed=202) — W10_late_diner (psychological_thriller)
**Prompt:** Write a 220-word psychological thriller scene in a fluorescent highway diner at midnight. A waitress notices that the quiet customer in booth four has ordered the exact same pie-and-coffee combination left untouched by a missing state trooper three weeks ago. Build dread through mundane diner detail.

### Sample A
The fluorescent lights hummed with a headache-inducing frequency, casting a sickly, greenish pallor over the Formica counters. Outside, the midnight highway was a void, swallowing the headlights of passing trucks. 

Marge wiped the same spot on the counter for the tenth time, her rag damp with lukewarm grease. Her eyes drifted to booth four. The man sat perfectly still, his silhouette carved out of the shadows by the flickering neon sign outside. He hadn't moved in forty minutes.

On the table sat a slice of cherry pie, the crust congealed and weeping red syrup, alongside a ceramic mug of black coffee with a thin, oily film shimmering on the surface. 

Marge’s stomach tightened. A cold, prickling dread crawled up her spine. Three weeks ago, Trooper Miller had sat in that exact booth. He’d ordered that exact combination—cherry pie and black coffee. He had vanished mid-bite, leaving his radio crackling on the empty seat and his cruiser idling in the lot.

The man in booth four picked up his fork. The metal scraped against the plate with a screech that set Marge’s teeth on edge. He hadn't taken a single bite, yet the pie looked exactly as it had the night the Trooper disappeared: fresh, untouched, and waiting.

### Sample B
The fluorescent tubes hummed their sick, electric hymn over the cracked vinyl of booth four. Daleen wiped the counter in slow, circular strokes, her rag dragging through yesterday’s coffee rings like a tide. The diner was empty save for the man in booth four—quiet, still, his hands folded on the Formica like a man waiting for a verdict.

He had ordered cherry pie and black coffee. The same combination. The exact same combination that had sat untouched on this very table three weeks ago, cooling into a sticky, congealed mess while the world outside searched for State Trooper Ray Calloway.

Daleen set the plate down. The pie glistened under the lights, a grotesque little sun. She retreated to the counter, her fingers trembling slightly. She should have felt relief. A normal order from a normal customer. But the order felt like a signature, a message pinned beneath glass.

The man did not touch his pie. He did not touch his coffee. He simply watched her through the steam rising from the cup, his eyes flat and patient. Daleen returned to her rag, scrubbing harder now, as if she could erase the silence. Outside, headlights swept across the parking lot, pausing, then vanishing. The man in booth four had not blinked.

---

## Round 3 (seed=303) — W10_late_diner (psychological_thriller)
**Prompt:** Write a 220-word psychological thriller scene in a fluorescent highway diner at midnight. A waitress notices that the quiet customer in booth four has ordered the exact same pie-and-coffee combination left untouched by a missing state trooper three weeks ago. Build dread through mundane diner detail.

### Sample A
The fluorescent lights hummed with a migraine-inducing frequency, casting a sickly, jaundiced hue over the cracked linoleum. Outside, the midnight highway was a void of wet asphalt and nothingness. 

Marge wiped the counter, the scent of burnt grease and lemon disinfectant clinging to her skin. Her eyes drifted to booth four. The man sat perfectly still, his silhouette a jagged tear against the window’s reflection. He hadn't moved in twenty minutes.

On the table sat a slice of cherry pie, the crust congealing into a waxy film, and a ceramic mug of black coffee, now filmed with a thin, oily sheen. 

Marge’s hand trembled, the rag slipping from her grip. It was the same spread. The exact same configuration of crumbs and cold caffeine that had sat untouched three weeks ago when Trooper Miller disappeared mid-shift. He’d vanished between bites, leaving his keys and his life behind. 

The man in booth four finally shifted. The screech of the vinyl bench sounded like a dying animal in the hollow silence. He didn't look up, but the rhythmic, wet sound of him stirring the cold coffee—clink, clink, clink—sent a chill down her spine. It was the same cadence Miller had used. The same pattern. The same ghost.

### Sample B
The fluorescent hum was a sound Dolores had stopped hearing years ago, a constant beneath the sizzle of the grill and the clatter of silverware. Tonight, it felt like a held breath.

Booth four. The man sat with his hands flat on the Formica, not moving, not blinking. He had ordered cherry pie and black coffee. The same order the state trooper had left untouched three weeks ago, the morning the patrol car was found idling in the county lot with its door hanging open.

Dolores watched him from the coffee station, the pot cooling in her grip. The diner was empty except for the cook, who had gone silent mid-verse of a song he’d been humming. The pie case light flickered, casting a sick green pallor over the display. The man in booth four hadn’t touched his pie. He hadn’t touched his coffee. He just sat there, staring at the window where the headlights of passing trucks smeared like red wounds across the glass.

Dolores remembered the trooper’s face the last time she’d seen him—pale, hollowed, eyes fixed on this very booth. She remembered the way he’d whispered, *Don’t look at me,* before he’d walked out into the dark and never come back.

The man in booth four slowly lifted his head. His eyes were the trooper’s eyes.

---
