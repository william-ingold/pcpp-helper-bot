# pcpp-helper-bot
Helper bot for posting [PC Part Picker](https://pcpartpicker.com/) links as tables in Reddit and informing users
to anonymize their list URLs.

The bot will read through new submissions from [r/buildapc](https://www.reddit.com/r/buildapc) via [PRAW](https://praw.readthedocs.io/en/latest). Currently, only
submissions with the following flairs will be inspected: 
* Build Complete
* Build Upgrade
* Build Help
* Build Ready
* No flair

If a submission has PC Part Picker list URL, but either no table or a malformed one, the bot will post a reply
with a table with the list's components. The table is essentially the same as the one created by PC Part Picker,
although it contains the affiliate links for vendors and items as well.

Additionally, if the bot detects an identifiable list URL, it will find the anonymous list URL and
inform the user to use it instead.

## Example
One example is below, additional ones are in the examples folder.

### Post
This is a test post. Here is an anonymous PCPP list url: https://pcpartpicker.com/list/ZqWwj2

### Reply:
Hello, I am the [PC Part Picker](https://pcpartpicker.com) Helper Bot!

Wah-oh! I found at least one instance of the following table issue(s) in your post: a missing table

To help out, I made this for you:

[PCPartPicker Part List](https://pcpartpicker.com/list/3pK2Bc)

Type|Item|Price
:----|:----|:----
**CPU** | [AMD Ryzen 5 5600X 3.7 GHz 6-Core Processor](https://pcpartpicker.com/product/g94BD3/amd-ryzen-5-5600x-37-ghz-6-core-processor-100-100000065box) | $299.00
**Motherboard** | [ASRock X570 Phantom Gaming 4S ATX AM4 Motherboard](https://pcpartpicker.com/product/cvhmP6/asrock-x570-phantom-gaming-4s-atx-am4-motherboard-x570-phantom-gaming-4s) | $139.99 @ Newegg
**Memory** | [Crucial Ballistix 16 GB (2 x 8 GB) DDR4-3200 CL16 Memory](https://pcpartpicker.com/product/BxTzK8/crucial-ballistix-16-gb-2-x-8-gb-ddr4-3200-memory-bl2k8g32c16u4b) | $79.95 @ B&H Photo
**Storage** | [Samsung 860 Evo 500 GB 2.5" Solid State Drive](https://pcpartpicker.com/product/6yKcCJ/samsung-860-evo-500gb-25-solid-state-drive-mz-76e500bam) | $54.99 @ B&H Photo
**Video Card** | [Asus GeForce RTX 3080 10 GB TUF GAMING Video Card](https://pcpartpicker.com/product/DgMTwP/asus-geforce-rtx-3080-10-gb-tuf-gaming-video-card-tuf-rtx3080-10g-gaming) | $699.00
**Case** | [Montech X1 ATX Mid Tower Case](https://pcpartpicker.com/product/4vJmP6/montech-x1-atx-mid-tower-case-x1-black) | $53.69 @ Amazon
**Power Supply** | [Cooler Master MWE Gold 750 W 80+ Gold Certified Fully Modular ATX Power Supply](https://pcpartpicker.com/product/v6gzK8/cooler-master-mwe-gold-750-w-80-gold-certified-fully-modular-atx-power-supply-mpy-7501-afaag-us) | $116.39 @ Amazon
*Prices include shipping, taxes, rebates, and discounts* |
| **Total** | **$1443.01** |
Generated at 2021-01-17 21:22:45 EST-0500 |  |


PC Part Picker will create the table for you if you click on the Reddit logo at the top of your list.

---
Please don't reply directly to me, so that we can minimize spam!

[You can PM me](https://www.reddit.com/message/compose/?to=pcpp-helper-bot) any concerns, issues, or suggestions!

My GitHub repository [can be found here](https://github.com/william-ingold/pcpp-helper-bot), if you'd like to take a gander.
 
 ## Potential Ideas
 This could be linked up with [r/buildapcsales](https://www.reddit.com/r/buildapcsales) to determine if an item has recently gone on sale.
 The difficulty lies in tying the component and sale together. Either the name has to be similar
 or the linked vendor from PC Part Picker must be the same as the link from r/buildapcsales. Research
 and experimentation need to be done.
 
 Either read through comments for links as well, or await for a mention of the bot to post a list table
 in response to a comment.
 
 ## TODO
Work on getting the vendor names correct, since it's currently just parsing them from the affiliate URL.
