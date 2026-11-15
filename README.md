# LaundryParseBench

Ten images of text-bearing objects that went through the wash: two supplied photos and eight found online. The selection favors visible damage with enough surviving text to make OCR worthwhile.

![All ten images](previews/contact-sheet.jpg)

## Collection

| ID | Image | What makes it useful | Source |
| --- | --- | --- | --- |
| 01 | [Fox in Socks — wide view](images/01-fox-in-socks-wide.jpeg) | Surviving cover titles and publisher text amid detached paper pulp. | User supplied |
| 02 | [Fox in Socks — close view](images/02-fox-in-socks-close.jpeg) | Closer view of surviving printed cover; wrinkles, missing material and pulp. | User supplied |
| 03 | [Anatomy textbook](images/03-anatomy-textbook.jpg) | Readable body-text fragments and headings on crumpled pages; many folds and missing regions. | [u/Pol_Slattery](https://www.reddit.com/r/Wellthatsucks/comments/m9024o/my_textbook_somehow_made_it_into_my_washing/) |
| 04 | [Letters from a Stoic](images/04-stoic-book.jpeg) | Title fragments, SENECA and CAPSTONE survive on a torn, deformed book. | [u/gogodboss](https://www.reddit.com/r/mildlyinfuriating/comments/1ukoqxz/i_accidentally_put_my_book_in_the_washing_machine/) |
| 05 | [Pokémon card pinned flat](images/05-pokemon-card.jpeg) | Attack names and numbers remain readable through wrinkles, reflections and thumbtack occlusion. | [u/rhubarb_thehawlic](https://www.reddit.com/r/Wellthatsucks/comments/1xqsui7/5th_grade_me_accidentally_washed_a_pokemon_card_i/) |
| 06 | [Meathook Massacre II](images/06-meathook-massacre.jpg) | Title and rules remain readable, with ragged edges and damaged border text. | [u/cartmicah3](https://www.reddit.com/r/mtg/comments/1fw9vqq/this_is_what_meathook_massacre_2_looks_like_going/) |
| 07 | [Trading-card pack left in a pocket](images/07-shredded-card-pack.jpg) | Several cards retain title and rule fragments despite torn edges, folds and missing sections. | [u/Lipzilla](https://www.reddit.com/r/mtg/comments/129syxr/so_i_just_ruin_a_most_wanted_card_on_accident/) |
| 08 | [Jeans with a washed-out patch](images/08-silvertab-jeans.jpg) | Inner baggy pleated and silverTab labels remain readable beside the almost blank back patch. | [u/carschap](https://www.reddit.com/r/VintageClothing/comments/xyrs37/rmildlyinfuriating_washed_these_one_time_and_the/) |
| 09 | [Banknotes shredded in the wash](images/09-shredded-banknotes.jpg) | Denominations, lettering and serial-number fragments survive on scattered, torn banknote pieces. | [u/BocceBurger](https://www.reddit.com/r/mildlyinfuriating/comments/tyoljy/i_accidentally_washed_10/) |
| 10 | [Game cartridge with its label washed away](images/10-washed-ds-cartridge.jpg) | The cartridge has a ruined printed label with handwritten markings; a readable game booklet sits beside it. | [u/Annual_Marsupial3039](https://www.reddit.com/r/gamecollecting/comments/177yav4/whats_the_best_way_to_restore_this_ds_cartridge/) |

## Files and provenance

- `images/`: original source files, without enhancement or artificial damage.
- `manifest.json`: attribution, source URLs, washing accounts, visual notes, dimensions and SHA-256 hashes.
- `previews/contact-sheet.jpg`: a resized overview for browsing.

The online washing accounts come from the people posting the images; they have not been independently verified. Images 01 and 02 show the same washed book, so the collection contains nine distinct washing events. Keep those two views together when splitting data.

Image 09 shows shredded banknotes; its washing account is disputed in the source comments and recorded as unverified. In image 10, the booklet beside the damaged cartridge is readable context, not washed material. Handwritten markings are visible on the cartridge, but their timing is unknown.

This is a curated seed collection. No OCR runs, reference transcripts, or performance scores are included. Ground truth should distinguish readable text, partial text, and unrecoverable regions. Object names and source stories are context, not evidence that missing words can be read from an image. Keep source titles and descriptions out of image-only model inputs.

## Image rights

This repository is private. The eight online images remain third-party material; no redistribution license has been verified. Attribution and source links are recorded for every file. Inclusion does not grant permission to republish the photographs. The two supplied images have no public license specified either.
