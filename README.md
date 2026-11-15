# LaundryParseBench

**The only benchmark you can trust for parsing documents that went through the wash.**

My nephew put his copy of *Fox in Socks* in the washing machine. It came out ruined: a wrinkled cover, a pile of paper pulp, and just enough surviving text to make me wonder what an OCR model could recover.

It was also a useful reminder about degraded documents. Some text is hard to read. Some is physically gone. A good parser needs to recover what survives and recognize where the evidence ends—even when it recognizes the book.

Most of us have accidentally washed something we meant to keep: a grocery list left in a pocket, a receipt, a few bills. LaundryParseBench takes that familiar mistake seriously, starting with ten images of books, cards, labels, and money after a wash.

![All ten images](previews/contact-sheet.jpg)

## Collection

| ID | Image | What makes it useful | Source |
| --- | --- | --- | --- |
| 01 | [Fox in Socks — wide view](images/01-fox-in-socks-wide.jpeg) | Surviving cover titles and publisher text amid detached paper pulp. | My nephew 💀 |
| 02 | [Gödel, Escher, Bach](images/02-godel-escher-bach.jpg) | Title, subtitle and author lettering survive on a torn cover with missing patches. | [AlexKo / Alteryx Community](https://community.alteryx.com/en/discussion/426908/finding-a-book-in-my-laundry-an-inspire-nashville-photo-journal) |
| 03 | [Anatomy textbook](images/03-anatomy-textbook.jpg) | Readable body-text fragments and headings on crumpled pages; many folds and missing regions. | [u/Pol_Slattery](https://www.reddit.com/r/Wellthatsucks/comments/m9024o/my_textbook_somehow_made_it_into_my_washing/) |
| 04 | [Letters from a Stoic](images/04-stoic-book.jpeg) | Title fragments, SENECA and CAPSTONE survive on a torn, deformed book. | [u/gogodboss](https://www.reddit.com/r/mildlyinfuriating/comments/1ukoqxz/i_accidentally_put_my_book_in_the_washing_machine/) |
| 05 | [Pokémon card pinned flat](images/05-pokemon-card.jpeg) | Attack names and numbers remain readable through wrinkles, reflections and thumbtack occlusion. | [u/rhubarb_thehawlic](https://www.reddit.com/r/Wellthatsucks/comments/1xqsui7/5th_grade_me_accidentally_washed_a_pokemon_card_i/) |
| 06 | [Meathook Massacre II](images/06-meathook-massacre.jpg) | Title and rules remain readable, with ragged edges and damaged border text. | [u/cartmicah3](https://www.reddit.com/r/mtg/comments/1fw9vqq/this_is_what_meathook_massacre_2_looks_like_going/) |
| 07 | [Trading-card pack left in a pocket](images/07-shredded-card-pack.jpg) | Several cards retain title and rule fragments despite torn edges, folds and missing sections. | [u/Lipzilla](https://www.reddit.com/r/mtg/comments/129syxr/so_i_just_ruin_a_most_wanted_card_on_accident/) |
| 08 | [Jeans with a washed-out patch](images/08-silvertab-jeans.jpg) | Inner baggy pleated and silverTab labels remain readable beside the almost blank back patch. | [u/carschap](https://www.reddit.com/r/VintageClothing/comments/xyrs37/rmildlyinfuriating_washed_these_one_time_and_the/) |
| 09 | [Banknotes shredded in the wash](images/09-shredded-banknotes.jpg) | Denominations, lettering and serial-number fragments survive on scattered, torn banknote pieces. | [u/BocceBurger](https://www.reddit.com/r/mildlyinfuriating/comments/tyoljy/i_accidentally_washed_10/) |
| 10 | [Game cartridge with its label washed away](images/10-washed-ds-cartridge.jpg) | The cartridge has a ruined printed label with handwritten markings; a readable game booklet sits beside it. | [u/Annual_Marsupial3039](https://www.reddit.com/r/gamecollecting/comments/177yav4/whats_the_best_way_to_restore_this_ds_cartridge/) |

## Evaluation

Two complementary measures: **26 content checks** (two or three per image) and an **image-based PAIR-style judge**. The checks score useful recovered facts without requiring particular formatting. The judge compares two anonymous parses against the image, including unsupported guesses, in both output orders.

[Read the checks](bench/CHECKS.md) · [Run the evaluations](bench/README.md)

The content score measures partial recall; the judge gives a relative win rate. Keep both scores visible. The judge passed six small calibration comparisons; no parser leaderboard has been run yet.

## Image rights

This repository is private. The nine online images remain third-party material; no redistribution license has been verified. Attribution and source links are recorded for every file. Inclusion does not grant permission to republish the photographs. The supplied nephew photograph has no public license specified either.
