# pcpp-helper-bot
Helper bot for posting [PC Part Picker](https://pcpartpicker.com/) links as tables in Reddit.

The bot will read through new submissions from [r/buildapc](https://www.reddit.com/r/buildapc) via [PRAW](https://praw.readthedocs.io/en/latest). Currently, only
submissions with the following flairs will be inspected: 
* Build Complete
* Build Upgrade
* Build Help
* Build Ready.

If a submission has PC Part Picker list URL, but either no table or a malformed one, the bot will post a reply
with a table with the list's components. The table is essentially the same as the one created by PC Part Picker,
although it contains the affiliate links for vendors and items as well.

## Example
Given the PC Part Picker list https://pcpartpicker.com/list/HQzZgJ,
the bot will create a table, such as:

Type|Item|Price
:----|:----|:----
 **CPU** | [AMD Ryzen 7 3700X 3.6 GHz 8-Core Processor](https://pcpartpicker.com/product/QKJtt6/amd-ryzen-7-3700x-36-ghz-8-core-processor-100-100000071box) | $319.99 @ [Newegg](https://pcpartpicker.com/mr/newegg/QKJtt6)
 **Motherboard** | [Asus ROG STRIX B550-F GAMING ATX AM4 Motherboard](https://pcpartpicker.com/product/JXBhP6/asus-rog-strix-b550-f-gaming-atx-am4-motherboard-rog-strix-b550-f-gaming) | $184.99 @ [B&H Photo](https://pcpartpicker.com/mr/bhphotovideo/JXBhP6)
 **Memory** | [G.Skill Ripjaws V 16 GB (2 x 8 GB) DDR4-3600 CL16 Memory](https://pcpartpicker.com/product/jBZzK8/gskill-ripjaws-v-16-gb-2-x-8-gb-ddr4-3600-memory-f4-3600c16d-16gvkc) | $92.99 @ [Newegg](https://pcpartpicker.com/mr/newegg/jBZzK8)
 **Storage** | [Samsung 860 Evo 500 GB 2.5" Solid State Drive](https://pcpartpicker.com/product/6yKcCJ/samsung-860-evo-500gb-25-solid-state-drive-mz-76e500bam) | $54.99 @ [Adorama](https://pcpartpicker.com/mr/adorama/6yKcCJ)
 **Case** | [Fractal Design Meshify C ATX Mid Tower Case](https://pcpartpicker.com/product/BBrmP6/fractal-design-meshify-c-white-tg-atx-mid-tower-case-fd-ca-mesh-c-wt-tgc) | $99.98 @ [Newegg](https://pcpartpicker.com/mr/newegg/BBrmP6)
 **Power Supply** | [Thermaltake Smart DPS G 750 W 80+ Gold Certified Semi-modular ATX Power Supply](https://pcpartpicker.com/product/4x648d/thermaltake-smart-dps-g-750w-80-gold-certified-semi-modular-atx-power-supply-ps-spg-0750dpcgus-g) | No Prices Available 
 **Operating System** | [Microsoft Windows 10 Pro OEM 64-bit](https://pcpartpicker.com/product/MfH48d/microsoft-os-fqc08930) | $139.88 @ [Otherworldcomputing](https://pcpartpicker.com/mr/otherworldcomputing/MfH48d)
 *Prices include shipping, taxes, rebates, and discounts* | 
 | **Total** | **$892.82** | 
 Generated at 2021-01-07 20:01:49 EST-0500 |  |
 
 ## Potential Ideas
 This could be linked up with [r/buildapcsales](https://www.reddit.com/r/buildapcsales) to determine if an item has recently gone on sale.
 The difficulty lies in tying the component and sale together. Either the name has to be similar
 or the linked vendor from PC Part Picker must be the same as the link from r/buildapcsales. Research
 and experimentation need to be done.
 
 Either read through comments for links as well, or await for a mention of the bot to post a list table
 in response to a comment.
 
 ## Roadmap
 Step 1...make a roadmap
 
